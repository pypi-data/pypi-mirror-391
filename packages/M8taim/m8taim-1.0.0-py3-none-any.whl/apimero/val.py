import re
import hashlib
from datetime import datetime

class InputValidator:
    @staticmethod
    def validate_year(year):
        if year is None:
            return True
        
        if not isinstance(year, int):
            return False
        
        current_year = datetime.now().year
        return current_year <= year <= current_year + 100
    
    @staticmethod
    def validate_month(month):
        if month is None:
            return True
        
        if not isinstance(month, int):
            return False
        
        return 1 <= month <= 12 or 0 <= month <= 1200
    
    @staticmethod
    def validate_day(day):
        if day is None:
            return True
        
        if not isinstance(day, int):
            return False
        
        return 1 <= day <= 31 or 0 <= day <= 36500
    
    @staticmethod
    def validate_hour(hour):
        if hour is None:
            return True
        
        if not isinstance(hour, int):
            return False
        
        return 0 <= hour <= 23 or 0 <= hour <= 876000
    
    @staticmethod
    def validate_message(message):
        if message is None:
            return True
        
        if not isinstance(message, str):
            return False
        
        return 1 <= len(message) <= 500

class SecurityValidator:
    @staticmethod
    def validate_checksum(data, expected_checksum, algorithm='sha256'):
        if algorithm == 'sha256':
            actual = hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()
        elif algorithm == 'sha512':
            actual = hashlib.sha512(data.encode() if isinstance(data, str) else data).hexdigest()
        else:
            return False
        
        return actual == expected_checksum
    
    @staticmethod
    def validate_signature(data, signature, key):
        import hmac
        expected = hmac.new(key.encode() if isinstance(key, str) else key, 
                           data.encode() if isinstance(data, str) else data, 
                           hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)
    
    @staticmethod
    def validate_token_format(token):
        pattern = r'^[A-Za-z0-9+/]+=*$'
        return bool(re.match(pattern, token))
    
    @staticmethod
    def validate_license_key(key):
        if not isinstance(key, str):
            return False
        
        if len(key) < 16:
            return False
        
        return True

class DataValidator:
    @staticmethod
    def validate_json(json_string):
        import json
        try:
            json.loads(json_string)
            return True
        except:
            return False
    
    @staticmethod
    def validate_timestamp(timestamp):
        if not isinstance(timestamp, (int, float)):
            return False
        
        min_timestamp = 0
        max_timestamp = 2147483647
        
        return min_timestamp <= timestamp <= max_timestamp
    
    @staticmethod
    def sanitize_input(user_input):
        if not isinstance(user_input, str):
            return str(user_input)
        
        sanitized = re.sub(r'[^\w\s\-\_\.]', '', user_input)
        return sanitized[:1000]
