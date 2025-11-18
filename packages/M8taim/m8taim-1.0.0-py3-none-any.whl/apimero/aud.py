import time
import json
from pathlib import Path
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self._log_dir = Path.home() / '.m8taim' / 'audit'
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._current_log = []
    
    def log_action(self, action_type, user, details=None):
        entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'action': action_type,
            'user': user,
            'details': details or {}
        }
        
        self._current_log.append(entry)
        
        if len(self._current_log) >= 100:
            self.flush()
    
    def log_security_event(self, event_type, severity, description):
        self.log_action('security_event', 'system', {
            'event_type': event_type,
            'severity': severity,
            'description': description
        })
    
    def log_access(self, resource, user, granted):
        self.log_action('access', user, {
            'resource': resource,
            'granted': granted
        })
    
    def log_modification(self, resource, user, changes):
        self.log_action('modification', user, {
            'resource': resource,
            'changes': changes
        })
    
    def flush(self):
        if not self._current_log:
            return
        
        filename = f"audit_{int(time.time())}.json"
        filepath = self._log_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self._current_log, f, indent=2)
            
            self._current_log = []
            return True
        except:
            return False
    
    def search_logs(self, action_type=None, user=None, start_time=None, end_time=None):
        results = []
        
        for log_file in sorted(self._log_dir.glob('audit_*.json')):
            try:
                with open(log_file, 'r') as f:
                    entries = json.load(f)
                
                for entry in entries:
                    if action_type and entry['action'] != action_type:
                        continue
                    if user and entry['user'] != user:
                        continue
                    if start_time and entry['timestamp'] < start_time:
                        continue
                    if end_time and entry['timestamp'] > end_time:
                        continue
                    
                    results.append(entry)
            except:
                continue
        
        return results
    
    def get_statistics(self):
        all_logs = self.search_logs()
        
        stats = {
            'total_entries': len(all_logs),
            'actions': {},
            'users': {},
            'first_entry': None,
            'last_entry': None
        }
        
        for entry in all_logs:
            action = entry['action']
            user = entry['user']
            
            stats['actions'][action] = stats['actions'].get(action, 0) + 1
            stats['users'][user] = stats['users'].get(user, 0) + 1
            
            if stats['first_entry'] is None or entry['timestamp'] < stats['first_entry']:
                stats['first_entry'] = entry['timestamp']
            
            if stats['last_entry'] is None or entry['timestamp'] > stats['last_entry']:
                stats['last_entry'] = entry['timestamp']
        
        return stats
