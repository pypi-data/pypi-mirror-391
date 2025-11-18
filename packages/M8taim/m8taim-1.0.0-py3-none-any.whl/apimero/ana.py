import time
import json
from collections import defaultdict
from datetime import datetime

class AnalyticsEngine:
    def __init__(self):
        self._metrics = defaultdict(int)
        self._timings = defaultdict(list)
        self._errors = []
        self._start_time = time.time()
    
    def track_metric(self, name, value=1):
        self._metrics[name] += value
    
    def track_timing(self, name, duration):
        self._timings[name].append(duration)
    
    def track_error(self, error_type, message, details=None):
        self._errors.append({
            'timestamp': time.time(),
            'type': error_type,
            'message': message,
            'details': details or {}
        })
    
    def get_metric(self, name):
        return self._metrics.get(name, 0)
    
    def get_average_timing(self, name):
        timings = self._timings.get(name, [])
        return sum(timings) / len(timings) if timings else 0
    
    def get_all_metrics(self):
        return dict(self._metrics)
    
    def get_uptime(self):
        return time.time() - self._start_time
    
    def get_report(self):
        return {
            'uptime': self.get_uptime(),
            'metrics': dict(self._metrics),
            'timings': {k: self.get_average_timing(k) for k in self._timings},
            'errors': len(self._errors),
            'last_error': self._errors[-1] if self._errors else None
        }
    
    def export_report(self, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(self.get_report(), f, indent=2)
            return True
        except:
            return False
