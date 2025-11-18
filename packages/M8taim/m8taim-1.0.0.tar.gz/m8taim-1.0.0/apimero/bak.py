import json
import time
import shutil
from pathlib import Path

class BackupRecovery:
    def __init__(self):
        self._backup_dir = Path.home() / '.m8taim' / 'backups'
        self._backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, data, name=None):
        if not name:
            name = f"backup_{int(time.time())}.json"
        
        backup_path = self._backup_dir / name
        
        backup_data = {
            'timestamp': time.time(),
            'data': data,
            'version': '1.0.0'
        }
        
        try:
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            return str(backup_path)
        except:
            return None
    
    def restore_backup(self, name):
        backup_path = self._backup_dir / name
        
        if not backup_path.exists():
            return None
        
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            return backup_data.get('data')
        except:
            return None
    
    def list_backups(self):
        backups = []
        
        for backup_file in self._backup_dir.glob('*.json'):
            try:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                
                backups.append({
                    'name': backup_file.name,
                    'timestamp': backup_data.get('timestamp'),
                    'version': backup_data.get('version'),
                    'size': backup_file.stat().st_size
                })
            except:
                continue
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_backup(self, name):
        backup_path = self._backup_dir / name
        
        try:
            backup_path.unlink()
            return True
        except:
            return False
    
    def cleanup_old_backups(self, keep_count=10):
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        deleted = 0
        for backup in backups[keep_count:]:
            if self.delete_backup(backup['name']):
                deleted += 1
        
        return deleted
