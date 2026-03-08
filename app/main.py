from fastapi import FastAPI
from pydantic import BaseModel
from app.guardrails import validate_query
from app.agents import run_trip_planner, run_trip_planner_stream
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="AI Trip Planner Agent",
    description="Multi-agent AI system for planning travel itineraries",
    version="1.0"
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