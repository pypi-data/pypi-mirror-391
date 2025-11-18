import os
import sys
import time
import hashlib
import pickle
from datetime import datetime, timedelta
from .security import SecurityValidator
from .tg import TimeGuard
from .tls import TimeLockSystem

class M8taim:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, year=None, month=None, day=None, hour=None, message=None):
        if self._initialized:
            return
        
        self._validator = SecurityValidator()
        self._time_guard = TimeGuard()
        self._lock_file = self._get_lock_path()
        
        if self._check_permanent_lock():
            self._terminate(self._get_stored_message())
        
        self._expiry = self._calculate_expiry(year, month, day, hour)
        self._message = message or "TIME EXPIRED - TOOL PERMANENTLY DISABLED"
        self._signature = self._generate_signature()
        
        if time.time() >= self._expiry:
            self._create_permanent_lock()
            self._terminate(self._message)
        
        self._initialized = True
        self._lock_system = TimeLockSystem(self._expiry)
        self._lock_system.start_monitor(lambda: self._terminate(self._message))
        self._start_monitor()
    
    def _get_lock_path(self):
        script_path = os.path.abspath(sys.argv[0])
        script_hash = hashlib.sha256(script_path.encode()).hexdigest()[:16]
        
        lock_paths = [
            os.path.join(os.path.expanduser("~"), ".config", f".m8taim_{script_hash}.lock"),
            os.path.join("/tmp", f".m8taim_{script_hash}.lock"),
            os.path.join(os.path.dirname(script_path), f".m8taim_{script_hash}.lock")
        ]
        
        for path in lock_paths:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                return path
            except:
                continue
        
        return lock_paths[0]
    
    def _check_permanent_lock(self):
        if not os.path.exists(self._lock_file):
            return False
        
        try:
            with open(self._lock_file, 'rb') as f:
                lock_data = pickle.load(f)
            
            required_keys = {'signature', 'timestamp', 'message', 'pid_chain', 'system_id'}
            if not all(key in lock_data for key in required_keys):
                return False
            
            current_sig = self._generate_signature()
            if lock_data['signature'] != current_sig:
                return False
            
            return True
        except:
            return False
    
    def _create_permanent_lock(self):
        lock_data = {
            'signature': self._signature,
            'timestamp': time.time(),
            'message': self._message,
            'pid_chain': self._validator.get_pid_chain(),
            'system_id': self._validator.get_system_id()
        }
        
        try:
            with open(self._lock_file, 'wb') as f:
                pickle.dump(lock_data, f)
            
            os.chmod(self._lock_file, 0o444)
        except:
            pass
    
    def _get_stored_message(self):
        try:
            with open(self._lock_file, 'rb') as f:
                lock_data = pickle.load(f)
            return lock_data.get('message', "TIME EXPIRED")
        except:
            return "TIME EXPIRED"
    
    def _calculate_expiry(self, year, month, day, hour):
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
    
    def _generate_signature(self):
        components = [
            str(os.getpid()),
            str(os.getppid()),
            os.path.abspath(sys.argv[0]),
            sys.executable,
            str(os.stat(__file__).st_ino),
            str(self._validator.get_system_id())
        ]
        
        raw = ''.join(components).encode()
        return hashlib.sha512(raw).hexdigest()
    
    def _start_monitor(self):
        import threading
        
        def monitor():
            while True:
                time.sleep(0.5)
                
                if not self._time_guard.multi_verify(self._expiry):
                    self._create_permanent_lock()
                    self._terminate(self._message)
                
                if time.time() >= self._expiry:
                    self._create_permanent_lock()
                    self._terminate(self._message)
                
                if not self._validator._check_time_manipulation():
                    self._create_permanent_lock()
                    self._terminate(self._message)
                
                if not self._validator._check_pid_injection():
                    self._create_permanent_lock()
                    self._terminate(self._message)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _terminate(self, message):
        import ctypes
        import sys
        
        print(f"\n{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        
        for _ in range(50):
            print(message)
        
        sys.stdout.flush()
        sys.stderr.flush()
        
        try:
            if hasattr(ctypes, 'windll'):
                ctypes.windll.kernel32.ExitProcess(1)  # type: ignore
            else:
                import signal
                os.kill(os.getpid(), signal.SIGKILL)
        except:
            import faulthandler
            faulthandler._sigsegv()  # type: ignore
