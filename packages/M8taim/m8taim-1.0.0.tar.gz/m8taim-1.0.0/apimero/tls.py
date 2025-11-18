import time
import threading
import hashlib

class TimeLockSystem:
    def __init__(self, expiry):
        self._expiry = expiry
        self._locks = []
        self._running = True
        self._init_locks()
    
    def _init_locks(self):
        for i in range(5):
            lock_data = {
                'id': i,
                'time': time.time(),
                'hash': hashlib.sha256(str(time.time() + i).encode()).hexdigest()
            }
            self._locks.append(lock_data)
    
    def verify_all(self):
        now = time.time()
        
        if now >= self._expiry:
            return False
        
        for lock in self._locks:
            lock_time = lock['time']
            if now < lock_time - 5:
                return False
        
        return True
    
    def start_monitor(self, callback):
        def monitor():
            while self._running:
                if not self.verify_all():
                    callback()
                    break
                time.sleep(0.3)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def stop(self):
        self._running = False
