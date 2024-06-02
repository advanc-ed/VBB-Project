import pytz
from datetime import time, datetime, timedelta


def time_to_iso(time: time):
    timezone = pytz.timezone('Europe/Berlin')
    current_datetime = timezone.localize(datetime.now())
    target_time = time or datetime.strptime("09:00", "%H:%M").time()
    target_datetime = timezone.localize(datetime.combine(
        current_datetime.date(),
        target_time
    ))

    if current_datetime.time() > target_time:
        target_datetime += timedelta(days=1)

    iso_format = target_datetime.strftime("%Y-%m-%dT%H:%M%z")

    return iso_format
