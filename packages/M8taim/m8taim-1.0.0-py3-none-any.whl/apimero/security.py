import os
import sys
import time
import platform
import hashlib
import socket
import uuid

class SecurityValidator:
    def __init__(self):
        self._baseline_time = time.time()
        self._monotonic_baseline = time.monotonic()
        self._system_id = self._compute_system_id()
        self._pid_chain = self.get_pid_chain()
        self._boot_time = self._get_boot_time()
    
    def validate_all(self, expiry_timestamp):
        checks = [
            self._check_time_manipulation(),
            self._check_pid_injection(),
            self._check_system_integrity(),
            self._check_debugger(),
            self._check_time_consistency(expiry_timestamp)
        ]
        return all(checks)
    
    def _check_time_manipulation(self):
        current_time = time.time()
        current_monotonic = time.monotonic()
        
        expected_time = self._baseline_time + (current_monotonic - self._monotonic_baseline)
        
        if abs(current_time - expected_time) > 5:
            return False
        
        self._baseline_time = current_time
        self._monotonic_baseline = current_monotonic
        
        return True
    
    def _check_pid_injection(self):
        current_chain = self.get_pid_chain()
        
        if len(current_chain) != len(self._pid_chain):
            return False
        
        for i, pid in enumerate(current_chain):
            if pid != self._pid_chain[i]:
                return False
        
        return True
    
    def _check_system_integrity(self):
        current_id = self._compute_system_id()
        return current_id == self._system_id
    
    def _check_debugger(self):
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            return False
        
        try:
            import ctypes
            if platform.system() == "Windows":
                if ctypes.windll.kernel32.IsDebuggerPresent():  # type: ignore
                    return False
        except:
            pass
        
        return True
    
    def _check_time_consistency(self, expiry_timestamp):
        now = time.time()
        
        if now >= expiry_timestamp:
            return False
        
        boot_time = self._get_boot_time()
        if boot_time != self._boot_time:
            return False
        
        return True
    
    def get_pid_chain(self):
        chain = []
        pid = os.getpid()
        
        for _ in range(10):
            chain.append(pid)
            try:
                ppid = os.getppid()
                if ppid == pid or ppid <= 1:
                    break
                pid = ppid
            except:
                break
        
        return tuple(chain)
    
    def get_system_id(self):
        return self._system_id
    
    def _compute_system_id(self):
        components = []
        
        try:
            components.append(platform.node())
            components.append(platform.machine())
            components.append(platform.processor())
            components.append(str(uuid.getnode()))
            components.append(socket.gethostname())
            components.append(sys.executable)
        except:
            pass
        
        raw = ''.join(components).encode()
        return hashlib.sha256(raw).hexdigest()
    
    def _get_boot_time(self):
        try:
            if platform.system() == "Linux":
                with open('/proc/uptime', 'r') as f:
                    uptime = float(f.readline().split()[0])
                return int(time.time() - uptime)
            elif platform.system() == "Windows":
                import ctypes
                return ctypes.windll.kernel32.GetTickCount64() // 1000  # type: ignore
        except:
            pass
        
        return 0
