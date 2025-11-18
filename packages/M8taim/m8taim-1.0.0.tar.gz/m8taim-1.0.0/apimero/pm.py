import os
import sys
import time
import threading
import psutil

class ProcessMonitor:
    def __init__(self):
        self._pid = os.getpid()
        self._ppid = os.getppid()
        self._process = psutil.Process(self._pid)
        self._baseline_metrics = self._capture_metrics()
        self._monitoring = False
    
    def _capture_metrics(self):
        try:
            return {
                'cpu_percent': self._process.cpu_percent(),
                'memory_percent': self._process.memory_percent(),
                'num_threads': self._process.num_threads(),
                'num_fds': self._process.num_fds() if hasattr(self._process, 'num_fds') else 0,
                'create_time': self._process.create_time()
            }
        except:
            return {}
    
    def detect_debugger_attach(self):
        try:
            if sys.gettrace() is not None:
                return True
        except:
            pass
        
        try:
            import ctypes
            if hasattr(ctypes, 'windll'):
                if ctypes.windll.kernel32.IsDebuggerPresent():  # type: ignore
                    return True
        except:
            pass
        
        try:
            if os.path.exists(f'/proc/{self._pid}/status'):
                with open(f'/proc/{self._pid}/status', 'r') as f:
                    for line in f:
                        if line.startswith('TracerPid:'):
                            tracer = int(line.split()[1])
                            if tracer != 0:
                                return True
        except:
            pass
        
        return False
    
    def detect_injection(self):
        try:
            current_threads = self._process.num_threads()
            baseline_threads = self._baseline_metrics.get('num_threads', 0)
            
            if current_threads > baseline_threads + 5:
                return True
        except:
            pass
        
        try:
            if hasattr(self._process, 'memory_maps'):
                maps = self._process.memory_maps()
                for m in maps:
                    if 'inject' in m.path.lower() or 'hook' in m.path.lower():
                        return True
        except:
            pass
        
        return False
    
    def verify_parent_process(self):
        try:
            current_ppid = os.getppid()
            return current_ppid == self._ppid
        except:
            return False
    
    def get_process_tree(self):
        tree = []
        try:
            current = self._process
            while current:
                tree.append({
                    'pid': current.pid,
                    'name': current.name(),
                    'cmdline': ' '.join(current.cmdline())
                })
                current = current.parent()
        except:
            pass
        
        return tree
    
    def monitor_resource_usage(self):
        try:
            cpu = self._process.cpu_percent(interval=0.1)
            memory = self._process.memory_percent()
            
            if cpu > 90.0:
                return {'status': 'high_cpu', 'value': cpu}
            
            if memory > 80.0:
                return {'status': 'high_memory', 'value': memory}
            
            return {'status': 'normal', 'cpu': cpu, 'memory': memory}
        except:
            return {'status': 'error'}
    
    def start_continuous_monitoring(self, callback):
        self._monitoring = True
        
        def monitor_loop():
            while self._monitoring:
                try:
                    if self.detect_debugger_attach():
                        callback('debugger_detected')
                        break
                    
                    if self.detect_injection():
                        callback('injection_detected')
                        break
                    
                    if not self.verify_parent_process():
                        callback('parent_changed')
                        break
                    
                    time.sleep(0.5)
                except:
                    break
        
        thread = threading.Thread(target=monitor_loop, daemon=False)
        thread.start()
    
    def stop_monitoring(self):
        self._monitoring = False
