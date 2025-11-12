from datetime import datetime, timezone, timedelta
import pytz as zone
from one_interfaces import jsonTicksDateTime_pb2 as jsonTicksTime
from one_interfaces import enum_timezone_pb2

timeZoneDictionary = {
    54: zone.timezone('America/Adak'),
    55: zone.timezone('America/Anchorage'),
    93: zone.timezone('America/Chicago'),
    104: zone.timezone('America/Denver'),
    146: zone.timezone('America/Los_Angeles'),
    168: zone.timezone('America/New_York'),
    179: zone.timezone('America/Phoenix'),
    184: zone.timezone('America/Puerto_Rico'),
    202: zone.timezone('America/St_Johns'),
    348: zone.timezone('Australia/Darwin'),
    349: zone.timezone("Australia/Eucla"),
    354: zone.timezone("Australia/Melbourne"),
    357: zone.timezone("Australia/Perth"),
    428: zone.timezone("Europe/Berlin"),
    441: zone.timezone("Europe/Istanbul"),
    444: zone.timezone("Europe/Kiev"),
    446: zone.timezone("Europe/Lisbon"),
    455: zone.timezone("Europe/Moscow"),
    536: zone.timezone("Pacific/Honolulu")
}

def GetRowNumber(date: datetime, wsType):
    date = date.replace(tzinfo=timezone.utc)
    BaseTime = datetime(1900, 1, 1, 0, 0, 0, 0, timezone.utc)
    diffTime = date - BaseTime
    windowSize = TimeSpanOfWorksheetType(wsType)
    diffTimeMinutes = diffTime.total_seconds()/60
    windowSizeMinutes = windowSize.total_seconds()/60
    return int(diffTimeMinutes / windowSizeMinutes) + 1


def AssumePlantTimeConvertToUtc(date: datetime, localTz: enum_timezone_pb2):
    tz = timeZoneDictionary[localTz]
    date = tz.localize(date.replace(tzinfo=None))
    utc = zone.timezone('utc')
    date = date.astimezone(utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return date

def ConvertToUtc(date: datetime):   
    utc = zone.timezone('utc')
    date = date.astimezone(utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return date

def GetDateFromRowNumber(rowNumber, wsType):
    BaseTime = datetime(1900, 1, 1, 0, 0, 0, 0, timezone.utc)
    row = rowNumber-1
    windowSize = TimeSpanOfWorksheetType(wsType)
    windowSizeMinutes = windowSize.total_seconds()/60
    mins = windowSizeMinutes*row
    return BaseTime+timedelta(minutes=mins)


def ToJsonTicksDateTime(date: datetime):
    jsTime = jsonTicksTime.JsonTicksDateTime()
    jsTime.jsonDateTime.value = str(date)
    return jsTime


def TimeSpanOfWorksheetType(wsType):
    if wsType == 1:
        return timedelta(minutes=15)
    elif wsType == 2:
        return timedelta(hours=1)
    elif wsType == 3:
        return timedelta(hours=4)
    elif wsType == 4:
        return timedelta(days=1)
    else:
        return "Invalid worksheet type"
