import sys
import os

class StealthMode:
    def __init__(self):
        self._original_modules = set(sys.modules.keys())
        self._hidden = False
    
    def hide_from_modules(self):
        apimero_modules = [m for m in sys.modules.keys() if 'apimero' in m or 'm8taim' in m.lower()]
        
        self._hidden_modules = {}
        for module in apimero_modules:
            self._hidden_modules[module] = sys.modules[module]
            sys.modules['_' + module] = sys.modules[module]
        
        self._hidden = True
    
    def reveal_modules(self):
        if not self._hidden:
            return
        
        for module, obj in self._hidden_modules.items():
            sys.modules[module] = obj
        
        self._hidden = False
    
    def hide_files(self, file_patterns):
        hidden_files = []
        
        for pattern in file_patterns:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if pattern in file:
                        filepath = os.path.join(root, file)
                        hidden_path = os.path.join(root, '.' + file)
                        try:
                            os.rename(filepath, hidden_path)
                            hidden_files.append(hidden_path)
                        except:
                            pass
        
        return hidden_files
    
    def obfuscate_error_messages(self, error_msg):
        obfuscated = error_msg.replace('M8taim', 'System')
        obfuscated = obfuscated.replace('apimero', 'core')
        obfuscated = obfuscated.replace('protection', 'validation')
        return obfuscated
    
    def disable_traceback(self):
        sys.tracebacklimit = 0
    
    def enable_traceback(self):
        sys.tracebacklimit = 1000
