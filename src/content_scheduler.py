from datetime import datetime


DAY_MAPPING = {
    0: "research breakdown",
    1: "engineering lesson",
    2: "failure analysis",
    3: "tool comparison",
    4: "future prediction",
    5: "tutorial",
    6: "deep insight",
}


CONTENT_MIX = {
    "research breakdown": 40,
    "engineering lesson": 20,
    "failure analysis": 15,
    "tool comparison": 10,
    "future prediction": 10,
    "career guidance": 5,
}


def get_day_content_type():
    weekday = datetime.now().weekday()
    return DAY_MAPPING.get(weekday, "research breakdown")


def choose_next_post_type(history=None):
    """
    Weekly scheduler.
    """
    return get_day_content_type()