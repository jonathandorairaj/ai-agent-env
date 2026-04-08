from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.telemetry import setup_telemetry, trips_counter, pdf_downloads_counter
from app.guardrails import validate_query
from app.agents import run_trip_planner, run_trip_planner_stream
from frontend.pdf_export import generate_trip_pdf

# Initialise OTel before the app is created so the instrumentor
# can attach to the tracer/meter providers we just configured.
setup_telemetry()

app = FastAPI(
    title="AI Trip Planner Agent",
    description="Multi-agent AI system for planning travel itineraries",
    version="1.0"
)

# Auto-instruments every request: traces, latency histogram, status codes.
FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripRequest(BaseModel):
    query: str


class TripResponse(BaseModel):
    result: dict


@app.get("/")
def root():
    return {"message": "AI Trip Planner API running"}


@app.post("/plan-trip")
async def plan_trip(request: TripRequest):


    if not validate_query(request.query):
        return {"error": "Query contains banned topics. Please revise your query."}

    try:
        result = await run_trip_planner(request.query)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
    

@app.post("/generate-pdf")
async def generate_pdf(request: Request):
    body = await request.json()
    result = body.get("result", {})
    pdf_buffer = generate_trip_pdf(result)
    destination = result.get("destination", "trip")
    pdf_downloads_counter.add(1, {"destination": destination})
    return Response(
        content=pdf_buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{destination}_trip_plan.pdf"'}
    )


@app.post("/plan-trip-stream")
async def plan_trip_stream(request: TripRequest):

    if not validate_query(request.query):
        return {"error": "Query contains banned topics. Please revise your query."}

    try:
        return StreamingResponse(
            run_trip_planner_stream(request.query),
            media_type="text/event-stream"
        )
    except Exception as e:
        return {"error": str(e)}