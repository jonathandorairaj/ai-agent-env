import asyncio
from app.agents import run_trip_planner

async def main():

    user_query = "Plan a 3 day complete trip to Bengaluru including hotels, restaurants and itinerary."

    result = await run_trip_planner(user_query)

    #print(result)
    print("\n===== RUN RESULT =====\n")
    print(result)

"""     print("\n===== RAW MESSAGES =====\n")
    for m in result.messages:
        print(m) """
    #print("Final agent:", result.last_agent.name)

asyncio.run(main())