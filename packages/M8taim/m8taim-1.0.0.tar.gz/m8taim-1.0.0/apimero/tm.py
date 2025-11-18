import time
from datetime import datetime, timedelta
import calendar

def get_remaining(expiry_timestamp):
    remaining = expiry_timestamp - time.time()
    
    if remaining <= 0:
        return {
            'expired': True,
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
            'total': 0,
            'text': 'EXPIRED'
        }
    
    days = int(remaining // 86400)
    hours = int((remaining % 86400) // 3600)
    minutes = int((remaining % 3600) // 60)
    seconds = int(remaining % 60)
    
    return {
        'expired': False,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'total': int(remaining),
        'text': f"{days}d {hours}h {minutes}m {seconds}s"
    }

def calc_expiry(year=None, month=None, day=None, hour=None):
    now = datetime.now()
    
    if year:
        target = datetime(year=year, month=month or 1, day=day or 1, hour=hour or 0)
    elif month or day or hour:
        delta = timedelta(
            days=(month or 0) * 30 + (day or 0),
            hours=(hour or 0)
        )
        target = now + delta
    else:
        delta = timedelta(days=30)
        target = now + delta
    
    return target.timestamp()
