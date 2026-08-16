from datetime import timedelta

MIN_SESSION_TTL = timedelta(minutes=5)  # Firebase floor
MAX_SESSION_TTL = timedelta(days=14)  # Firebase ceiling
