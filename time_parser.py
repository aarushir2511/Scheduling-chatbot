import parsedatetime
from datetime import datetime, timedelta

cal = parsedatetime.Calendar()

def parse_time_string(text):
    time_struct, _ = cal.parse(text)
    dt = datetime(*time_struct[:6])
    return dt
