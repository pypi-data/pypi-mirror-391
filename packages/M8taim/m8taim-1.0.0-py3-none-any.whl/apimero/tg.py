import time
import hashlib
import os
import pickle
from datetime import datetime

class TimeGuard:
    def __init__(self):
        self._baseline = time.time()
        self._mono_baseline = time.monotonic()
        self._checkpoints = []
        self._hidden_files = []
        self._create_checkpoints()
    
    def _create_checkpoints(self):
        paths = [
            os.path.join(os.path.expanduser("~"), ".cache", ".m8tm"),
            os.path.join("/tmp", ".m8tm_ck"),
            os.path.join(os.path.expanduser("~"), ".local", ".m8tm_guard"),
            os.path.join("/var/tmp", ".m8_tg") if os.path.exists("/var/tmp") else None
        ]
        
        for path in paths:
            if path:
                try:
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    
                    data = {
                        't': time.time(),
                        'm': time.monotonic(),
                        'h': hashlib.sha512(str(time.time()).encode()).hexdigest()
                    }
                    
                    with open(path, 'wb') as f:
                        pickle.dump(data, f)
                    
                    os.chmod(path, 0o400)
                    self._hidden_files.append(path)
                except:
                    pass
    
    def verify(self, expiry):
        now = time.time()
        mono = time.monotonic()
        
        if now >= expiry:
            return False
        
        expected = self._baseline + (mono - self._mono_baseline)
        if abs(now - expected) > 3:
            return False
        
        for fpath in self._hidden_files:
            try:
                with open(fpath, 'rb') as f:
                    data = pickle.load(f)
                
                file_time = data.get('t', 0)
                if now < file_time - 10:
                    return False
            except:
                return False
        
        self._baseline = now
        self._mono_baseline = mono
        
        return True
    
    def multi_verify(self, expiry):
        checks = []
        
        checks.append(time.time() < expiry)
        checks.append(self.verify(expiry))
        
        try:
            import psutil
            boot_time = psutil.boot_time()
            checks.append(boot_time > 0)
        except:
            pass
        
        return all(checks)
