import socket
import struct
import hashlib
import time

class NetworkGuard:
    def __init__(self):
        self._network_baseline = self._capture_network_state()
        self._connection_log = []
        self._blocked_ips = set()
    
    def _capture_network_state(self):
        state = {
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'interfaces': []
        }
        
        try:
            state['ip'] = socket.gethostbyname(socket.gethostname())
        except:
            state['ip'] = '127.0.0.1'
        
        return state
    
    def verify_network_integrity(self):
        current = self._capture_network_state()
        
        if current['hostname'] != self._network_baseline['hostname']:
            return False
        
        if current['ip'] != self._network_baseline['ip']:
            return False
        
        return True
    
    def detect_vpn_or_proxy(self):
        checks = []
        
        try:
            hostname = socket.gethostname()
            vpn_indicators = ['vpn', 'proxy', 'tor', 'tunnel', 'tun', 'tap']
            checks.append(any(indicator in hostname.lower() for indicator in vpn_indicators))
        except:
            pass
        
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith('10.') or ip.startswith('172.') or ip.startswith('192.168.'):
                checks.append(False)
        except:
            pass
        
        return any(checks)
    
    def log_connection_attempt(self, destination, port):
        entry = {
            'timestamp': time.time(),
            'destination': destination,
            'port': port,
            'hash': hashlib.sha256(f"{destination}:{port}".encode()).hexdigest()
        }
        self._connection_log.append(entry)
        
        if len(self._connection_log) > 1000:
            self._connection_log = self._connection_log[-1000:]
    
    def block_ip(self, ip):
        self._blocked_ips.add(ip)
    
    def is_blocked(self, ip):
        return ip in self._blocked_ips
    
    def get_mac_address(self):
        try:
            import uuid
            mac = uuid.getnode()
            return ':'.join(('%012x' % mac)[i:i+2] for i in range(0, 12, 2))
        except:
            return None
    
    def verify_dns_integrity(self):
        try:
            google_ips = socket.gethostbyname_ex('google.com')[2]
            if not google_ips:
                return False
            
            for ip in google_ips:
                if not self._is_valid_ip(ip):
                    return False
            
            return True
        except:
            return False
    
    def _is_valid_ip(self, ip):
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts)
        except:
            return False
