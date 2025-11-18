import sys
import time
from datetime import datetime

class HookSystem:
    def __init__(self):
        self._hooks = {
            'pre_validation': [],
            'post_validation': [],
            'on_expiry': [],
            'on_tampering': [],
            'on_success': []
        }
    
    def register_hook(self, event_type, callback):
        if event_type in self._hooks:
            self._hooks[event_type].append(callback)
            return True
        return False
    
    def trigger_hook(self, event_type, *args, **kwargs):
        if event_type not in self._hooks:
            return
        
        for callback in self._hooks[event_type]:
            try:
                callback(*args, **kwargs)
            except:
                pass
    
    def clear_hooks(self, event_type=None):
        if event_type:
            self._hooks[event_type] = []
        else:
            for key in self._hooks:
                self._hooks[key] = []
    
    def get_hook_count(self, event_type):
        return len(self._hooks.get(event_type, []))

class EventLogger:
    def __init__(self):
        self._events = []
        self._max_events = 10000
    
    def log_event(self, event_type, details=None):
        event = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'type': event_type,
            'details': details or {}
        }
        
        self._events.append(event)
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
    
    def get_events(self, event_type=None, limit=None):
        if event_type:
            filtered = [e for e in self._events if e['type'] == event_type]
        else:
            filtered = self._events
        
        if limit:
            return filtered[-limit:]
        return filtered
    
    def clear_events(self):
        self._events = []
    
    def export_events(self, filepath):
        import json
        try:
            with open(filepath, 'w') as f:
                json.dump(self._events, f, indent=2)
            return True
        except:
            return False
    
    def get_statistics(self):
        stats = {}
        for event in self._events:
            event_type = event['type']
            stats[event_type] = stats.get(event_type, 0) + 1
        return stats

class PluginManager:
    def __init__(self):
        self._plugins = {}
        self._enabled_plugins = set()
    
    def register_plugin(self, name, plugin_class):
        self._plugins[name] = plugin_class
        return True
    
    def enable_plugin(self, name):
        if name in self._plugins:
            self._enabled_plugins.add(name)
            return True
        return False
    
    def disable_plugin(self, name):
        if name in self._enabled_plugins:
            self._enabled_plugins.remove(name)
            return True
        return False
    
    def get_plugin(self, name):
        if name in self._plugins and name in self._enabled_plugins:
            return self._plugins[name]
        return None
    
    def list_plugins(self):
        return list(self._plugins.keys())
    
    def list_enabled_plugins(self):
        return list(self._enabled_plugins)
