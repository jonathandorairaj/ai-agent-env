import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from typing import Any
import json


def render_trip(result:dict):

    #df = pd.DataFrame()

    places = []

    for a in result["attractions"]:
        if a.get("lat") and a.get("lng"):
            places.append({
                "name": a["name"],
                "lat": a["lat"],
                "lon": a["lng"],
                "type": "attraction",
                "map_url": a["map_url"],
                "color": [168,85,247] 
            })

    # Hotels
    for h in result["hotels"]:
        if h.get("lat") and h.get("lng"):
            places.append({
                "name": h["name"],
                "lat": h["lat"],
                "lon": h["lng"],
                "type": "hotel",
                "color": [59,130,246] 
            })

    # Restaurants
    for r in result["restaurants"]:
        if r.get("lat") and r.get("lng"):
            places.append({
                "name": r["name"],
                "lat": r["lat"],
                "lon": r["lng"],
                "type": "restaurant",
                "color": [249,115,22]
            })

    df = pd.DataFrame(places)

    st.markdown(
    f'<div class="section-header">📍 Destination: {result["destination"]}</div>',
    unsafe_allow_html=True
                )
    cols = st.columns(2)

    for i, att in enumerate(result["attractions"]):

        with cols[i % 2]:

            # image_html = ""
            # if att.get("photo_url"):
            #     image_html = f'<img src="{att["photo_url"]}" width="100%">'
            
            st.markdown(f"""
            <div class="card">
            <div class="card-title">{att['name']}</div>
            <p><b>Description:</b> {att['description']}</p>
            <p><b>Rating:</b> {att['rating']}</p>
            <p><a href="{att['map_url']}" target="_blank"> View on Google Maps</a></p>
            </div>
            """, unsafe_allow_html=True)


    # Hotels
    st.markdown('<div class="section-header">🏨 Hotels</div>', unsafe_allow_html=True)

    cols = st.columns(2)

    for i, hotel in enumerate(result["hotels"]):

        with cols[i % 2]:

            # image_html = ""
            # if hotel.get("photo_url"):
            #     image_html = f'<img src="{hotel["photo_url"]}" width="100%">'

            amenities = ", ".join(hotel["amenities"])

            st.markdown(f"""
            <div class="card">
            <div class="card-title">{hotel['name']}</div>
            <p><b>Price:</b> {hotel['price']}</p>
            <p><b>Amenities:</b> {amenities}</p>
            <p><a href="{hotel['map_url']}" target="_blank">View on Google Maps</a></p>
            </div>
            """, unsafe_allow_html=True)

    # Restaurants
    st.markdown('<div class="section-header">🍽 Restaurants</div>', unsafe_allow_html=True)

    cols = st.columns(2)

    for i, r in enumerate(result["restaurants"]):

        with cols[i % 2]:

            # image_html = ""
            # if r.get("photo_url"):
            #     image_html = f'<img src="{r["photo_url"]}" width="100%">'

            st.markdown(f"""
            <div class="card">
            <div class="card-title">{r['name']}</div>
            <p><b>Cuisine:</b> {r['cuisine']}</p>
            <p><b>Neighborhood:</b> {r['neighborhood']}</p>
            <p><a href="{r['map_url']}" target="_blank">View on Google Maps</a></p>
            </div>
            """, unsafe_allow_html=True)

    if not df.empty:

        st.markdown('<div class="section-header">Map</div>', unsafe_allow_html=True)

        view_state = pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lon"].mean(),
            zoom=12,
            pitch=40,
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[lon, lat]',
            get_radius=150,
            get_fill_color="color",
            pickable=True
        )
        
        # tooltip: Any = {"text": "{name}\nType: {type}"}
        # tooltip = {
        #         "html": "<b>{name}</b><br/>Type: {type}<br/><a href='{map_url}' target='_blank'>Open in Google Maps</a>",
        #         "style": {"backgroundColor": "steelblue", "color": "white"}
        #         }
        tooltip = {
                "html": """
                <b>{name}</b><br/>
                ⭐ {rating}<br/>
                <i>{type}</i><br/>
                <a href='{map_url}' target='_blank'>Open in Google Maps</a>
                """,
                "style": {
                    "backgroundColor": "#1e293b",
                    "color": "white"
                }
            }
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
        )

        st.pydeck_chart(deck)

    # Itinerary
    st.markdown('<div class="section-header">📅 Itinerary</div>', unsafe_allow_html=True)

    for i, day in enumerate(result["itinerary"], start=1):

        st.markdown(f"""
        <div class="card">
        <div class="card-title">Day {i}</div>
        <p><b>Morning:</b> {day['morning']}</p>
        <p><b>Afternoon:</b> {day['afternoon']}</p>
        <p><b>Evening:</b> {day['evening']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Notes
    if result.get("notes"):

        st.markdown('<div class="section-header">📝 Notes</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
        {result["notes"]}
        </div>
        """, unsafe_allow_html=True)
