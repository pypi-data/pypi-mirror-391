import time
import hashlib
import hmac
from collections import defaultdict

class APIProtection:
    def __init__(self):
        self._api_keys = {}
        self._rate_limits = defaultdict(list)
        self._blacklist = set()
    
    def generate_api_key(self, user_id, permissions=None):
        timestamp = str(time.time())
        raw = f"{user_id}:{timestamp}".encode()
        api_key = hashlib.sha256(raw).hexdigest()
        
        self._api_keys[api_key] = {
            'user_id': user_id,
            'created': time.time(),
            'permissions': permissions or [],
            'active': True
        }
        
        return api_key
    
    def validate_api_key(self, api_key):
        if api_key in self._blacklist:
            return {'valid': False, 'reason': 'blacklisted'}
        
        if api_key not in self._api_keys:
            return {'valid': False, 'reason': 'invalid_key'}
        
        key_data = self._api_keys[api_key]
        
        if not key_data['active']:
            return {'valid': False, 'reason': 'inactive'}
        
        return {'valid': True, 'user_id': key_data['user_id'], 'permissions': key_data['permissions']}
    
    def check_rate_limit(self, api_key, max_requests_per_minute=60):
        now = time.time()
        
        self._rate_limits[api_key] = [t for t in self._rate_limits[api_key] if now - t < 60]
        
        if len(self._rate_limits[api_key]) >= max_requests_per_minute:
            return False
        
        self._rate_limits[api_key].append(now)
        return True
    
    def revoke_api_key(self, api_key):
        if api_key in self._api_keys:
            self._api_keys[api_key]['active'] = False
            self._blacklist.add(api_key)
            return True
        return False
    
    def check_permission(self, api_key, required_permission):
        validation = self.validate_api_key(api_key)
        
        if not validation['valid']:
            return False
        
        return required_permission in validation.get('permissions', [])
    
    def generate_signature(self, data, secret_key):
        if isinstance(data, dict):
            data_str = '|'.join(f"{k}:{v}" for k, v in sorted(data.items()))
        else:
            data_str = str(data)
        
        signature = hmac.new(
            secret_key.encode() if isinstance(secret_key, str) else secret_key,
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, data, signature, secret_key):
        expected_signature = self.generate_signature(data, secret_key)
        return hmac.compare_digest(signature, expected_signature)
