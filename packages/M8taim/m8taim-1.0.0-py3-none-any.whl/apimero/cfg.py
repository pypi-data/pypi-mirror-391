import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file=None):
        self._config_file = config_file or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self):
        config_dir = Path.home() / '.m8taim'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.json'
    
    def _load_config(self):
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return self._get_default_config()
    
    def _get_default_config(self):
        return {
            'strict_mode': True,
            'auto_lock': True,
            'verbose': False,
            'grace_period': 0,
            'max_violations': 3,
            'check_interval': 0.1,
            'enable_network_check': True,
            'enable_hardware_check': True,
            'enable_process_monitor': True,
            'custom_message': None
        }
    
    def save_config(self):
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except:
            return False
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def set(self, key, value):
        self._config[key] = value
        return self.save_config()
    
    def update(self, config_dict):
        self._config.update(config_dict)
        return self.save_config()
    
    def reset_to_defaults(self):
        self._config = self._get_default_config()
        return self.save_config()
    
    def export_config(self, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except:
            return False
    
    def import_config(self, filepath):
        try:
            with open(filepath, 'r') as f:
                self._config = json.load(f)
            return self.save_config()
        except:
            return False
