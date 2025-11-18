import functools
import time
from datetime import datetime

def time_protected(year=None, month=None, day=None, hour=None, message=None):
    def decorator(func):
        from .core import M8taim
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            M8taim(year=year, month=month, day=day, hour=hour, message=message)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_license(license_token):
    def decorator(func):
        from .lic import LicenseManager
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            manager = LicenseManager()
            validation = manager.validate_license(license_token)
            
            if not validation['valid']:
                raise PermissionError(f"Invalid license: {validation['reason']}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def track_usage(analytics_engine):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                analytics_engine.track_metric(f"{func.__name__}_success")
                return result
            except Exception as e:
                analytics_engine.track_error(func.__name__, str(e))
                raise
            finally:
                duration = time.time() - start_time
                analytics_engine.track_timing(func.__name__, duration)
        
        return wrapper
    return decorator

def retry_on_failure(max_attempts=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def rate_limit(calls_per_minute=60):
    def decorator(func):
        calls = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            calls[:] = [c for c in calls if now - c < 60]
            
            if len(calls) >= calls_per_minute:
                raise RuntimeError(f"Rate limit exceeded: {calls_per_minute} calls per minute")
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
