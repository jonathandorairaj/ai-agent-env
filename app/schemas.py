from pydantic import BaseModel
from typing import List, Optional


class Attraction(BaseModel):
    name: str
    description: str
    lat: float
    lng: float
    #photo_url: Optional[str] = None
    map_url: Optional[str] = None
    rating: Optional[float] = None
    address: str

class DestinationResearch(BaseModel):
    destination: str
    attractions: List[Attraction]
    #neighborhoods: List[str]
    #cultural_highlights: List[str]


class DayPlan(BaseModel):
    morning: str
    afternoon: str
    evening: str


class Itinerary(BaseModel):
    destination: str
    days: List[DayPlan]

class Hotel(BaseModel):
    name: str
    price: str
    lat: float
    lng: float
    amenities: List[str]
    #photo_url: Optional[str] = None
    map_url: Optional[str] = None
    rating: Optional[float] = None
    address: str

class HotelRecommendation(BaseModel):
    hotels: List[Hotel]

class FlightRecommendation(BaseModel):
    airline: str
    price: str
    departure_time: str
    arrival_time: str
    date: str

class Restaurant(BaseModel):
    name: str
    cuisine: str
    lat: float
    lng: float
    neighborhood: str
    #photo_url: Optional[str] = None
    map_url: Optional[str] = None
    rating: Optional[float] = None
    address: str


class FoodRecommendations(BaseModel):
    restaurants: List[Restaurant]

class Place(BaseModel):
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    rating: Optional[float]
    types: list[str]
    #photo_url: Optional[str] = None
    map_url: Optional[str] = None
    rating: Optional[float] = None

class TravelInfo(BaseModel):
    origin: str
    destination: str
    distance: str
    duration: str

class WeatherInfo(BaseModel):
    location: str
    description: str
    temperature: float
    humidity: int
    wind_speed: float


class FinalTravelPlan(BaseModel):
    destination: str
    attractions: List[Attraction]
    itinerary: List[DayPlan]
    hotels: List[Hotel]
    restaurants: List[Restaurant]
    notes: str