# packages/schemas/intents.py

from enum import Enum

class Intent(str, Enum):
    GET_EVENTS = "GET_EVENTS"
    CHECK_TRAFFIC = "CHECK_TRAFFIC"
    FIND_PLACES = "FIND_PLACES"
    UNKNOWN = "UNKNOWN"
