import os
import sys
import hashlib
import platform
from datetime import datetime, timedelta

class SystemUtils:
    @staticmethod
    def get_system_info():
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'hostname': platform.node()
        }
    
    @staticmethod
    def get_process_info():
        return {
            'pid': os.getpid(),
            'ppid': os.getppid(),
            'uid': os.getuid() if hasattr(os, 'getuid') else None,
            'gid': os.getgid() if hasattr(os, 'getgid') else None,
            'cwd': os.getcwd()
        }
    
    @staticmethod
    def safe_exit(code=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(code)
    
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

class CryptoUtils:
    @staticmethod
    def generate_hash(data, algorithm='sha256'):
        if isinstance(data, str):
            data = data.encode()
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def generate_random_key(length=32):
        return os.urandom(length).hex()
    
    @staticmethod
    def xor_encrypt(data, key):
        if isinstance(data, str):
            data = data.encode()
        if isinstance(key, str):
            key = key.encode()
        
        return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

class TimeUtils:
    @staticmethod
    def timestamp_to_datetime(timestamp):
        return datetime.fromtimestamp(timestamp)
    
    @staticmethod
    def datetime_to_timestamp(dt):
        return dt.timestamp()
    
    @staticmethod
    def format_duration(seconds):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return ' '.join(parts)
    
    @staticmethod
    def add_duration(base_dt, days=0, hours=0, minutes=0, seconds=0):
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return base_dt + delta

class FileUtils:
    @staticmethod
    def ensure_directory(path):
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def file_exists(path):
        return os.path.isfile(path)
    
    @staticmethod
    def read_file(path, binary=False):
        mode = 'rb' if binary else 'r'
        try:
            with open(path, mode) as f:
                return f.read()
        except:
            return None
    
    @staticmethod
    def write_file(path, content, binary=False):
        mode = 'wb' if binary else 'w'
        try:
            with open(path, mode) as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def get_file_hash(filepath, algorithm='sha256'):
        try:
            hasher = hashlib.new(algorithm)
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None
