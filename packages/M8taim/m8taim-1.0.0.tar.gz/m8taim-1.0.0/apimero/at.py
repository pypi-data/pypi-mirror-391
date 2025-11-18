import os
import sys
import hashlib
import inspect
import dis
import types

class AntiTamperSystem:
    def __init__(self):
        self._checksums = {}
        self._code_hashes = {}
        self._integrity_verified = False
    
    def register_module(self, module):
        if hasattr(module, '__file__') and module.__file__:
            try:
                with open(module.__file__, 'rb') as f:
                    content = f.read()
                self._checksums[module.__name__] = hashlib.sha512(content).hexdigest()
            except:
                pass
        
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                try:
                    code_bytes = obj.__code__.co_code
                    self._code_hashes[f"{module.__name__}.{name}"] = hashlib.sha256(code_bytes).hexdigest()
                except:
                    pass
    
    def verify_integrity(self):
        for module_name, expected_checksum in self._checksums.items():
            try:
                module = sys.modules.get(module_name)
                if module and hasattr(module, '__file__') and module.__file__:
                    with open(module.__file__, 'rb') as f:
                        current = hashlib.sha512(f.read()).hexdigest()
                    
                    if current != expected_checksum:
                        return False
            except:
                return False
        
        return True
    
    def check_function_integrity(self, func_name):
        if func_name not in self._code_hashes:
            return True
        
        module_name, func = func_name.rsplit('.', 1)
        try:
            module = sys.modules.get(module_name)
            if module:
                func_obj = getattr(module, func, None)
                if func_obj:
                    current_hash = hashlib.sha256(func_obj.__code__.co_code).hexdigest()
                    return current_hash == self._code_hashes[func_name]
        except:
            pass
        
        return False
    
    def detect_code_injection(self):
        frame = inspect.currentframe()
        
        try:
            while frame:
                code = frame.f_code
                
                if '<string>' in code.co_filename or '<stdin>' in code.co_filename:
                    return True
                
                if 'eval' in code.co_name or 'exec' in code.co_name:
                    return True
                
                frame = frame.f_back
        finally:
            del frame
        
        return False
    
    def check_imports(self):
        dangerous_modules = {
            'pdb', 'ipdb', 'pudb', 'bdb',
            'trace', 'profile', 'cProfile',
            'importlib', 'imp', '__builtin__', 'builtins'
        }
        
        for module_name in sys.modules.keys():
            if any(danger in module_name for danger in dangerous_modules):
                frame = inspect.currentframe()
                try:
                    while frame:
                        if module_name in frame.f_locals or module_name in frame.f_globals:
                            return False
                        frame = frame.f_back
                finally:
                    del frame
        
        return True
    
    def protect_namespace(self, namespace):
        protected = {}
        for key, value in namespace.items():
            if callable(value):
                protected[key] = self._wrap_function(value)
            else:
                protected[key] = value
        
        return types.SimpleNamespace(**protected)
    
    def _wrap_function(self, func):
        def wrapper(*args, **kwargs):
            if self.detect_code_injection():
                os._exit(1)
            return func(*args, **kwargs)
        
        return wrapper
