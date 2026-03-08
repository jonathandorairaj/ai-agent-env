from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
from typing import Any


def generate_trip_pdf(result):

    buffer = BytesIO()

    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(
        Paragraph(
            f"<font size=22><b>{result['destination']} Travel Plan</b></font>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    # ----------------
    # Hotels Table
    # ----------------

    elements.append(Paragraph("Hotels", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    hotel_data: list[list[Any]] = [["Hotel", "Price", "Rating", "Map"]]

    for h in result["hotels"]:
        rating = f"⭐ {h.get('rating', 'N/A')}"
        
        map_link = f'<link href="{h["map_url"]}">View on Maps</link>' if h.get("map_url") else ""
        hotel_data.append([
                h["name"],
                h["price"],
                rating,
                Paragraph(map_link, styles["BodyText"])
            ])
    

    hotel_table = Table(hotel_data, colWidths=[250,80,70,80])

    hotel_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(hotel_table)
    elements.append(Spacer(1, 20))

    # ----------------
    # Restaurants
    # ----------------

    elements.append(Paragraph("Restaurants", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    restaurant_data: list[list[Any]] = [["Restaurant", "Cuisine", "Rating", "Map"]]

    for r in result["restaurants"]:

        rating = f"⭐ {r.get('rating', 'N/A')}"

        map_link = f'<link href="{r["map_url"]}">Open</link>' if r.get("map_url") else ""

        restaurant_data.append([
            r["name"],
            r["cuisine"],
            rating,
            Paragraph(map_link, styles["BodyText"])
        ])

    restaurant_table = Table(restaurant_data, colWidths=[220, 120, 70, 80])

    restaurant_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(restaurant_table)
    elements.append(Spacer(1, 20))

    # ----------------
    # Attractions
    # ----------------

    if "attractions" in result:

        elements.append(Paragraph("Attractions", styles["Heading2"]))
        elements.append(Spacer(1, 10))

        for a in result["attractions"]:

            elements.append(
                Paragraph(
                    f"<b>{a['name']}</b> — {a['address']} "
                    f"(⭐ {a.get('rating','N/A')}) "
                    f"<link href='{a.get('map_url','')}' color='blue'>Map</link>",
                    styles["BodyText"]
                )
            )

            elements.append(Spacer(1, 5))

        elements.append(Spacer(1, 20))

    # ----------------
    # Itinerary
    # ----------------

    elements.append(Paragraph("Itinerary", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for i, day in enumerate(result["itinerary"], start=1):

        elements.append(
            Paragraph(
                f"<b>Day {i}</b>",
                styles["Heading3"]
            )
        )

        elements.append(
            Paragraph(f"Morning: {day['morning']}", styles["BodyText"])
        )

        elements.append(
            Paragraph(f"Afternoon: {day['afternoon']}", styles["BodyText"])
        )

        elements.append(
            Paragraph(f"Evening: {day['evening']}", styles["BodyText"])
        )

        elements.append(Spacer(1, 12))

    # ----------------
    # Notes
    # ----------------

    if result.get("notes"):

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph("Notes", styles["Heading2"])
        )

        elements.append(
            Paragraph(result["notes"], styles["BodyText"])
        )

    # Build PDF

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    doc.build(elements)

    buffer.seek(0)

    return buffer