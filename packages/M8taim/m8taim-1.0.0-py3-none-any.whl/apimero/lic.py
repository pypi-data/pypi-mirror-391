import json
import time
import hashlib
from datetime import datetime, timedelta
from .enc import EncryptionEngine

class LicenseManager:
    def __init__(self):
        self._encryption = EncryptionEngine()
        self._licenses = {}
    
    def create_license(self, license_id, user_id, expiry_date, features=None):
        license_data = {
            'id': license_id,
            'user_id': user_id,
            'created': time.time(),
            'expiry': expiry_date.timestamp() if isinstance(expiry_date, datetime) else expiry_date,
            'features': features or [],
            'activations': 0,
            'max_activations': 1,
            'hardware_locked': False
        }
        
        token = self._encryption.generate_token(license_data)
        self._licenses[license_id] = {
            'data': license_data,
            'token': token
        }
        
        return token
    
    def validate_license(self, token):
        try:
            decrypted = self._encryption.decrypt_data(token)
            if not decrypted:
                return {'valid': False, 'reason': 'invalid_token'}
            
            parts = decrypted.split('|')
            license_data = {}
            for part in parts:
                key, value = part.split(':', 1)
                license_data[key] = value
            
            expiry = float(license_data.get('expiry', 0))
            if time.time() > expiry:
                return {'valid': False, 'reason': 'expired'}
            
            activations = int(license_data.get('activations', 0))
            max_activations = int(license_data.get('max_activations', 1))
            
            if activations >= max_activations:
                return {'valid': False, 'reason': 'activation_limit'}
            
            return {'valid': True, 'license': license_data}
        except:
            return {'valid': False, 'reason': 'invalid_format'}
    
    def activate_license(self, token, hardware_id=None):
        validation = self.validate_license(token)
        
        if not validation['valid']:
            return validation
        
        license_data = validation['license']
        license_id = license_data.get('id')
        
        if license_id in self._licenses:
            self._licenses[license_id]['data']['activations'] += 1
            
            if hardware_id:
                self._licenses[license_id]['data']['hardware_id'] = hardware_id
                self._licenses[license_id]['data']['hardware_locked'] = True
        
        return {'valid': True, 'activated': True}
    
    def check_feature(self, token, feature_name):
        validation = self.validate_license(token)
        
        if not validation['valid']:
            return False
        
        features = validation['license'].get('features', '').split(',')
        return feature_name in features
    
    def extend_license(self, license_id, days):
        if license_id not in self._licenses:
            return False
        
        current_expiry = self._licenses[license_id]['data']['expiry']
        new_expiry = current_expiry + (days * 86400)
        self._licenses[license_id]['data']['expiry'] = new_expiry
        
        new_token = self._encryption.generate_token(self._licenses[license_id]['data'])
        self._licenses[license_id]['token'] = new_token
        
        return new_token
    
    def revoke_license(self, license_id):
        if license_id in self._licenses:
            self._licenses[license_id]['data']['expiry'] = time.time() - 1
            return True
        return False
    
    def get_license_info(self, token):
        validation = self.validate_license(token)
        
        if not validation['valid']:
            return None
        
        license_data = validation['license']
        expiry_time = float(license_data.get('expiry', 0))
        
        return {
            'user_id': license_data.get('user_id'),
            'expires_in': int((expiry_time - time.time()) / 86400),
            'features': license_data.get('features', '').split(','),
            'activations': license_data.get('activations', '0'),
            'hardware_locked': license_data.get('hardware_locked', 'False') == 'True'
        }
