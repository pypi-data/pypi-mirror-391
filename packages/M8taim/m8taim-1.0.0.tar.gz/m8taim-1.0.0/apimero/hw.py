import platform
import hashlib
import os
import uuid

class HardwareFingerprint:
    def __init__(self):
        self._fingerprint = self._generate_fingerprint()
        self._components = self._collect_components()
    
    def _collect_components(self):
        components = {}
        
        components['machine'] = platform.machine()
        components['processor'] = platform.processor()
        components['system'] = platform.system()
        components['release'] = platform.release()
        components['version'] = platform.version()
        components['node'] = platform.node()
        
        try:
            components['mac'] = hex(uuid.getnode())
        except:
            components['mac'] = 'unknown'
        
        try:
            if platform.system() == 'Linux':
                components['machine_id'] = self._get_linux_machine_id()
            elif platform.system() == 'Windows':
                components['machine_id'] = self._get_windows_machine_id()
            else:
                components['machine_id'] = str(uuid.uuid4())
        except:
            components['machine_id'] = 'unknown'
        
        return components
    
    def _get_linux_machine_id(self):
        paths = ['/etc/machine-id', '/var/lib/dbus/machine-id']
        
        for path in paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return f.read().strip()
            except:
                continue
        
        return 'unknown'
    
    def _get_windows_machine_id(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography')
            value, _ = winreg.QueryValueEx(key, 'MachineGuid')
            winreg.CloseKey(key)
            return value
        except:
            return 'unknown'
    
    def _generate_fingerprint(self):
        data = []
        
        data.append(platform.machine())
        data.append(platform.processor())
        data.append(platform.system())
        data.append(platform.node())
        data.append(str(uuid.getnode()))
        
        try:
            import cpuinfo
            info = cpuinfo.get_cpu_info()
            data.append(info.get('brand_raw', ''))
        except:
            pass
        
        combined = '|'.join(str(d) for d in data)
        return hashlib.sha512(combined.encode()).hexdigest()
    
    def get_fingerprint(self):
        return self._fingerprint
    
    def verify_hardware(self):
        current_fingerprint = self._generate_fingerprint()
        return current_fingerprint == self._fingerprint
    
    def get_component(self, name):
        return self._components.get(name, 'unknown')
    
    def get_all_components(self):
        return self._components.copy()
    
    def detect_vm(self):
        vm_indicators = {
            'manufacturer': ['VMware', 'VirtualBox', 'QEMU', 'Xen', 'Bochs', 'Parallels'],
            'model': ['Virtual', 'VMware', 'VirtualBox'],
            'system': ['Linux']
        }
        
        system_info = platform.uname()
        
        for field, indicators in vm_indicators.items():
            value = getattr(system_info, field, '').lower()
            if any(indicator.lower() in value for indicator in indicators):
                return True
        
        try:
            if platform.system() == 'Linux':
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    if 'hypervisor' in cpuinfo or 'vmware' in cpuinfo:
                        return True
        except:
            pass
        
        return False
    
    def get_cpu_count(self):
        try:
            return os.cpu_count() or 1
        except:
            return 1
