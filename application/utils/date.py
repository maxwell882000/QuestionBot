from dateutil import tz
from datetime import datetime


def convert_utc_to_asia_tz(utc_date: datetime):
    from_zone = tz.tzutc()
    to_zone = tz.gettz('Asia/Tashkent')
    utc = utc_date.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return local


def convert_asia_tz_to_utc(asia_date: datetime):
    from_zone = tz.gettz('Asia/Tashkent')
    to_zone = tz.tzutc()
    local_date = asia_date.replace(tzinfo=from_zone)
    utc = local_date.astimezone(to_zone)
    return utc
