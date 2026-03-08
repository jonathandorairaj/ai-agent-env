def validate_query(message: str) -> bool:

    banned_topics = [
        "hack",
        "illegal",
        "weapon",
        "bomb",
        "drugs"
    ]

    msg = message.lower()

    for word in banned_topics:
        if word in msg:
            return False

    return True