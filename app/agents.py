from agents import Agent, Runner
from app.schemas import DestinationResearch, FoodRecommendations, Itinerary, HotelRecommendation, FlightRecommendation, FinalTravelPlan
from app.tools import search_places, travel_time, get_weather
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from opentelemetry import trace
from app.telemetry import trips_counter, agent_errors_counter, agent_duration_histogram
import time
import json

tracer = trace.get_tracer("voyage.agents")

DEFAULT_MODEL = "gpt-4.1-mini"



research_agent = Agent(
    name="Destination Research Agent",
    instructions="""
    {RECOMMENDED_PROMPT_PREFIX}
    Research the travel destination and provide attractions
    """,
    tools=[search_places],
    output_type=DestinationResearch,
    model=DEFAULT_MODEL
    
)

food_agent = Agent(
    name="Food Explorer",
    instructions="""
    {RECOMMENDED_PROMPT_PREFIX}
    Reseach and recommend restuarants,popular dishes, and local specialties to try at the destination. 
    """,
    tools=[search_places],
    output_type=FoodRecommendations,
    model=DEFAULT_MODEL
    
)


itinerary_agent = Agent(
    name="Itinerary Planner",
    instructions="""
    {RECOMMENDED_PROMPT_PREFIX}
    Create a detailed day-by-day itinerary for the trip based on the destination research and food recommendations.
    Provide morning, afternoon, and evening activities for each day.

    For each day, use the travel_time tool to estimate travel time between the morning and afternoon locations,
    and between the afternoon and evening locations.
    Format the result as "<duration> (<distance>)" — e.g. "20 mins (3.2 km)" — and store it in
    morning_to_afternoon_travel and afternoon_to_evening_travel respectively.
    If travel time cannot be determined, leave the field as null.
    """,
    tools=[travel_time,get_weather],
    output_type=Itinerary,
    model=DEFAULT_MODEL

)

hotel_agent = Agent(
    name="Hotel Planner",
    instructions="""
    {RECOMMENDED_PROMPT_PREFIX}
    Find and recommend suitable hotels or hostels based on the destination research.
    """,
    tools=[search_places],
    output_type=HotelRecommendation,
    model=DEFAULT_MODEL
)

flight_agent = Agent(
    name="Flight Planner",
    instructions="""
    {RECOMMENDED_PROMPT_PREFIX}
    Research and recommend flights to the destination, including airlines, prices, departure and arrival times, and dates.
    """,
    output_type=FlightRecommendation
)


realism_guardrail = Agent(
    name="Travel Plan Validator",
    instructions="""
    Evaluate whether a travel plan is realistic.

    Check for:
    - realistic budgets for the destination
    - reasonable number of activities per day
    - realistic travel time between places
    - realistic flight and hotel costs

    If unrealistic, explain why.
    """
)


critic_agent = Agent(
    name="Travel Plan Critic",
    instructions="""
    Review the travel plan created by other agents. Makes corrections if needed.
    """,
    output_type= FinalTravelPlan,
    model=DEFAULT_MODEL
)


# orchestrator = Agent(
#     name="Trip Planner Orchestrator",
#     instructions="""
#     You coordinate end to end trip planning using the agents at your disposal. Always follow the workflow and delegate to the next agent until the critic produces the final plan.:

#     Always follow this workflow in order:

#     1. Call the Destination Research Agent to gather information about the destination.
#     2. Call the Hotel Planner to find accommodations.
#     3. Call the Food Explorer to find restaurants and local dishes.
#     4. Call the Itinerary Planner to create a day-by-day plan using the research results.
#     5. Send the full plan to the Travel Plan Critic to review and finalize it.

#     Do not answer the user directly.
#     Always delegate to the next agent until the critic produces the final plan
#     """,
#     #handoffs=[research_agent, flight_agent, hotel_agent, food_agent,itinerary_agent,critic_agent]
#     handoffs=[research_agent, hotel_agent, food_agent,itinerary_agent,critic_agent]

# )

# async def run_trip_planner(user_query: str):

#     result = await Runner.run(
#         orchestrator,
#         user_query
#     )
        
#     return result.final_output


async def run_trip_planner(user_query: str):


    # 1️⃣ Research
    research_result = await Runner.run(
        research_agent,
        user_query
    )
    research = research_result.final_output

    # 2️⃣ Hotels
    hotel_result = await Runner.run(
        hotel_agent,
        f"""
User request:
{user_query}

Destination research:
{research}
"""
    )
    hotels = hotel_result.final_output.hotels

    # 3️⃣ Food
    food_result = await Runner.run(
        food_agent,
        f"""
User request:
{user_query}

Destination research:
{research}
"""
    )
    restaurants = food_result.final_output

    # 4️⃣ Itinerary
    itinerary_result = await Runner.run(
        itinerary_agent,
        f"""
User request:
{user_query}

Destination research:
{research}

Hotel recommendations:
{hotels}

Food recommendations:
{restaurants}
"""
    )
    itinerary = itinerary_result.final_output

    # 5️⃣ Critic / Final Plan
    final_result = await Runner.run(
        critic_agent,
        f"""
User request:
{user_query}

Destination research:
{research}

Hotels:
{hotels}

Restaurants:
{restaurants}

Itinerary:
{itinerary}
"""
    )

    return final_result.final_output


async def run_trip_planner_stream(user_query: str):

    with tracer.start_as_current_span("trip.plan") as root_span:
        root_span.set_attribute("query", user_query)

        # STEP 1 — Research
        yield json.dumps({"status": "researching"}) + "\n"

        with tracer.start_as_current_span("agent.research") as span:
            t0 = time.perf_counter()
            try:
                research_result = await Runner.run(research_agent, user_query)
                research = research_result.final_output
                span.set_attribute("destination", research.destination)
            except Exception as e:
                agent_errors_counter.add(1, {"agent": "research"})
                span.record_exception(e)
                raise
            finally:
                agent_duration_histogram.record(
                    time.perf_counter() - t0, {"agent": "research"}
                )

        # Record the trip now we know the destination
        trips_counter.add(1, {"destination": research.destination})
        root_span.set_attribute("destination", research.destination)

        yield json.dumps({
            "status": "research_done",
            "destination": research.destination,
            "attractions": [a.model_dump() for a in research.attractions]
        }) + "\n"

        # STEP 2 — Hotels
        yield json.dumps({"status": "finding_hotels"}) + "\n"

        with tracer.start_as_current_span("agent.hotels") as span:
            t0 = time.perf_counter()
            try:
                hotel_result = await Runner.run(
                    hotel_agent,
                    f"""
User request:
{user_query}

Destination research:
{research}
"""
                )
                hotels = hotel_result.final_output.hotels
                span.set_attribute("hotels.count", len(hotels))
            except Exception as e:
                agent_errors_counter.add(1, {"agent": "hotels"})
                span.record_exception(e)
                raise
            finally:
                agent_duration_histogram.record(
                    time.perf_counter() - t0, {"agent": "hotels"}
                )

        yield json.dumps({
            "status": "hotels_done",
            "hotels": [h.model_dump() for h in hotels]
        }) + "\n"

        # STEP 3 — Restaurants
        yield json.dumps({"status": "finding_food"}) + "\n"

        with tracer.start_as_current_span("agent.food") as span:
            t0 = time.perf_counter()
            try:
                food_result = await Runner.run(
                    food_agent,
                    f"""
User request:
{user_query}

Destination research:
{research}
"""
                )
                restaurants = food_result.final_output.restaurants
                span.set_attribute("restaurants.count", len(restaurants))
            except Exception as e:
                agent_errors_counter.add(1, {"agent": "food"})
                span.record_exception(e)
                raise
            finally:
                agent_duration_histogram.record(
                    time.perf_counter() - t0, {"agent": "food"}
                )

        yield json.dumps({
            "status": "restaurants_done",
            "restaurants": [r.model_dump() for r in restaurants]
        }) + "\n"

        # STEP 4 — Itinerary
        yield json.dumps({"status": "building_itinerary"}) + "\n"

        with tracer.start_as_current_span("agent.itinerary") as span:
            t0 = time.perf_counter()
            try:
                itinerary_result = await Runner.run(
                    itinerary_agent,
                    f"""
User request:
{user_query}

Destination research:
{research.destination}

Top attractions:
{research.attractions}

Hotel recommendations:
{hotels}

Food recommendations:
{restaurants}
"""
                )
                itinerary = itinerary_result.final_output
                span.set_attribute("itinerary.days", len(itinerary.days))
            except Exception as e:
                agent_errors_counter.add(1, {"agent": "itinerary"})
                span.record_exception(e)
                raise
            finally:
                agent_duration_histogram.record(
                    time.perf_counter() - t0, {"agent": "itinerary"}
                )

        yield json.dumps({
            "status": "itinerary_done",
            "itinerary": [day.model_dump() for day in itinerary.days]
        }) + "\n"

        # STEP 5 — Final critic
        yield json.dumps({"status": "finalizing"}) + "\n"

        with tracer.start_as_current_span("agent.critic") as span:
            t0 = time.perf_counter()
            try:
                final_result = await Runner.run(
                    critic_agent,
                    f"""
User request:
{user_query}

Destination research:
{research}

Hotels:
{hotels}

Restaurants:
{restaurants}

Itinerary:
{itinerary}
"""
                )
            except Exception as e:
                agent_errors_counter.add(1, {"agent": "critic"})
                span.record_exception(e)
                raise
            finally:
                agent_duration_histogram.record(
                    time.perf_counter() - t0, {"agent": "critic"}
                )

    yield json.dumps({
        "status": "done",
        "result": final_result.final_output.model_dump()
    }) + "\n"