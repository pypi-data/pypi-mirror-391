import time
from datetime import datetime, timedelta
import calendar

class AdvancedTimeManager:
    def __init__(self):
        self._time_sources = []
        self._calibrated = False
    
    def add_time_source(self, source_func):
        self._time_sources.append(source_func)
    
    def get_consensus_time(self):
        if not self._time_sources:
            return time.time()
        
        times = []
        for source in self._time_sources:
            try:
                t = source()
                if t:
                    times.append(t)
            except:
                continue
        
        if not times:
            return time.time()
        
        times.sort()
        median_idx = len(times) // 2
        return times[median_idx]
    
    def calculate_expiry_absolute(self, year, month, day, hour, minute=0, second=0):
        target = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        return target.timestamp()
    
    def calculate_expiry_relative(self, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        now = datetime.now()
        
        if years or months:
            new_month = now.month + months + (years * 12)
            new_year = now.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            
            max_day = calendar.monthrange(new_year, new_month)[1]
            new_day = min(now.day, max_day)
            
            target = datetime(new_year, new_month, new_day, now.hour, now.minute, now.second)
        else:
            target = now
        
        delta = timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        
        target = target + delta
        return target.timestamp()
    
    def parse_duration_string(self, duration_str):
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
            'M': 2592000,
            'y': 31536000
        }
        
        total_seconds = 0
        current_number = ''
        
        for char in duration_str:
            if char.isdigit():
                current_number += char
            elif char in multipliers:
                if current_number:
                    total_seconds += int(current_number) * multipliers[char]
                    current_number = ''
        
        return time.time() + total_seconds
    
    def get_remaining_time(self, expiry_timestamp):
        remaining = expiry_timestamp - time.time()
        
        if remaining <= 0:
            return {'expired': True}
        
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        
        return {
            'expired': False,
            'total_seconds': int(remaining),
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{days}d {hours}h {minutes}m {seconds}s"
        }
    
    def is_within_grace_period(self, expiry_timestamp, grace_seconds=3600):
        time_diff = expiry_timestamp - time.time()
        return 0 <= time_diff <= grace_seconds
