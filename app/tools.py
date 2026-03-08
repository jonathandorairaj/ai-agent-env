import os
import requests
from dotenv import load_dotenv
from typing import List
from app.schemas import Place, TravelInfo,WeatherInfo
from agents import function_tool
load_dotenv()

GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

def get_location_coords(location):

    url = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {
        "address": location,
        "key": GOOGLE_MAPS_KEY
    }

    r = requests.get(url, params=params)

    data = r.json()

    if data["results"]:

        loc = data["results"][0]["geometry"]["location"]

        return loc["lat"], loc["lng"]

    return None, None




@function_tool
def search_places(query: str, location: str) -> List[Place]:
    """
    Search Google Places for attractions, restaurants, or hotels.

    Use this tool to find places relevant to travel planning.
    """

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    lat, lng = get_location_coords(location)

    # Map query to Google place types
    type_map = {
        "restaurant": "restaurant",
        "restaurants": "restaurant",
        "food": "restaurant",
        "hotel": "lodging",
        "hotels": "lodging",
        "attraction": "tourist_attraction",
        "attractions": "tourist_attraction"
    }

    place_type = type_map.get(query.lower())

    params = {
    "location": f"{lat},{lng}",
    "radius": 6000,
    #"keyword": query,
    "key": GOOGLE_MAPS_KEY
    }
    if place_type:
        params["type"] = place_type
    else:
        params["keyword"] = query

    try:

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        places = []

        for p in data.get("results", [])[:6]:

            # photo_url = None
            # photos = p.get("photos")
            # if photos:
            #     first_photo = photos[0]
            #     if isinstance(first_photo, dict):
            #         photo_ref = first_photo.get("photo_reference")
            
            #         if photo_ref:
            #             photo_url = (
            #                 "https://maps.googleapis.com/maps/api/place/photo"
            #                 f"?maxwidth=600"
            #                 f"&photo_reference={photo_ref}"
            #                 f"&key={GOOGLE_MAPS_KEY}"
            #             )
            map_url = f"https://www.google.com/maps/place/?q=place_id:{p['place_id']}"
            places.append(
                Place(
                    place_id=p["place_id"],
                    name=p["name"],
                    address=p.get("vicinity", ""),
                    lat=p["geometry"]["location"]["lat"],
                    lng=p["geometry"]["location"]["lng"],
                    rating=p.get("rating"),
                    types=p.get("types", []),
                    map_url=map_url
                    #photo_url=photo_url
                )
            )

        return places

    except Exception:

        return []

@function_tool
def travel_time(origin: str, destination: str) -> TravelInfo:

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": origin,
        "destinations": destination,
        "key": GOOGLE_MAPS_KEY
    }

    #r = requests.get(url, params=params)

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if data.get("rows"):
            element = data["rows"][0]["elements"][0]

            if element.get("status") == "OK":
                return TravelInfo(
                    origin=origin,
                    destination=destination,
                    distance=element["distance"]["text"],
                    duration=element["duration"]["text"]
                )

        # fallback if API fails
        return TravelInfo(
            origin=origin,
            destination=destination,
            distance="unknown",
            duration="unknown"
        )

    except Exception:
        return TravelInfo(
            origin=origin,
            destination=destination,
            distance="error",
            duration="error"
        )


@function_tool
def get_weather(location: str) -> WeatherInfo:
    """
    Get current weather conditions for a location.

    Useful for deciding outdoor vs indoor activities
    when planning itineraries.
    """

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": location,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }

    try:

        r = requests.get(url, params=params, timeout=10)

        data = r.json()

        return WeatherInfo(
            location=location,
            description=data["weather"][0]["description"],
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"]
        )

    except Exception:

        return WeatherInfo(
            location=location,
            description="unknown",
            temperature=0,
            humidity=0,
            wind_speed=0
        )