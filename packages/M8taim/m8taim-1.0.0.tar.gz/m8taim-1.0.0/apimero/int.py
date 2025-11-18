import sys
import importlib

class IntegrationHelpers:
    @staticmethod
    def integrate_with_flask(app, expiry_config):
        from .core import M8taim
        
        @app.before_first_request
        def protect_flask():
            M8taim(**expiry_config)
        
        return app
    
    @staticmethod
    def integrate_with_django(expiry_config):
        from .core import M8taim
        
        class M8taimMiddleware:
            def __init__(self, get_response):
                self.get_response = get_response
                M8taim(**expiry_config)
            
            def __call__(self, request):
                response = self.get_response(request)
                return response
        
        return M8taimMiddleware
    
    @staticmethod
    def integrate_with_fastapi(app, expiry_config):
        from .core import M8taim
        
        @app.on_event("startup")
        async def protect_fastapi():
            M8taim(**expiry_config)
        
        return app
    
    @staticmethod
    def protect_module(module_name, expiry_config):
        from .core import M8taim
        
        original_import = __builtins__.__import__
        
        def protected_import(name, *args, **kwargs):
            module = original_import(name, *args, **kwargs)
            
            if name == module_name:
                M8taim(**expiry_config)
            
            return module
        
        __builtins__.__import__ = protected_import
    
    @staticmethod
    def protect_function(func, expiry_config):
        from .dec import time_protected
        return time_protected(**expiry_config)(func)
    
    @staticmethod
    def protect_class(cls, expiry_config):
        from .core import M8taim
        
        original_init = cls.__init__
        
        def protected_init(self, *args, **kwargs):
            M8taim(**expiry_config)
            original_init(self, *args, **kwargs)
        
        cls.__init__ = protected_init
        return cls
    
    @staticmethod
    def bulk_protect_functions(module, expiry_config):
        from .dec import time_protected
        
        decorator = time_protected(**expiry_config)
        
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not name.startswith('_'):
                setattr(module, name, decorator(obj))
        
        return module
