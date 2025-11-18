import time
from collections import deque

class NotificationSystem:
    def __init__(self):
        self._notifications = deque(maxlen=1000)
        self._handlers = []
    
    def add_handler(self, handler_func):
        self._handlers.append(handler_func)
    
    def send_notification(self, level, message, details=None):
        notification = {
            'timestamp': time.time(),
            'level': level,
            'message': message,
            'details': details or {}
        }
        
        self._notifications.append(notification)
        
        for handler in self._handlers:
            try:
                handler(notification)
            except:
                pass
    
    def get_notifications(self, level=None, limit=None):
        if level:
            filtered = [n for n in self._notifications if n['level'] == level]
        else:
            filtered = list(self._notifications)
        
        if limit:
            return filtered[-limit:]
        return filtered
    
    def clear_notifications(self):
        self._notifications.clear()
    
    def get_unread_count(self, level=None):
        return len(self.get_notifications(level))

class AlertSystem:
    def __init__(self):
        self._alerts = []
        self._alert_thresholds = {}
    
    def set_threshold(self, metric_name, threshold, comparison='greater'):
        self._alert_thresholds[metric_name] = {
            'threshold': threshold,
            'comparison': comparison
        }
    
    def check_metric(self, metric_name, value):
        if metric_name not in self._alert_thresholds:
            return False
        
        threshold_data = self._alert_thresholds[metric_name]
        threshold = threshold_data['threshold']
        comparison = threshold_data['comparison']
        
        if comparison == 'greater' and value > threshold:
            self._trigger_alert(metric_name, value, threshold)
            return True
        elif comparison == 'less' and value < threshold:
            self._trigger_alert(metric_name, value, threshold)
            return True
        elif comparison == 'equal' and value == threshold:
            self._trigger_alert(metric_name, value, threshold)
            return True
        
        return False
    
    def _trigger_alert(self, metric_name, value, threshold):
        alert = {
            'timestamp': time.time(),
            'metric': metric_name,
            'value': value,
            'threshold': threshold
        }
        self._alerts.append(alert)
    
    def get_alerts(self, limit=None):
        if limit:
            return self._alerts[-limit:]
        return self._alerts.copy()
    
    def clear_alerts(self):
        self._alerts.clear()
