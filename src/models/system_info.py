"""
System information gathering module.
"""
import psutil
import platform
import socket
import time
import subprocess
import winreg
from typing import List, Dict, Any


class SystemInfo:
    """Gathers system information using psutil and Windows commands."""
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Get CPU information."""
        cpu_freq = psutil.cpu_freq()
        return {
            'name': platform.processor(),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'freq_current': cpu_freq.current if cpu_freq else 0,
            'freq_max': cpu_freq.max if cpu_freq else 0,
            'freq_min': cpu_freq.min if cpu_freq else 0,
            'usage': psutil.cpu_percent(interval=0.1),
            'usage_per_core': psutil.cpu_percent(interval=0.1, percpu=True)
        }
    
    @staticmethod
    def get_cpu_times() -> Dict[str, float]:
        """Get CPU time breakdown."""
        times = psutil.cpu_times()
        return {
            'user': times.user,
            'system': times.system,
            'idle': times.idle
        }
    
    @staticmethod
    def get_gpu_info() -> List[Dict[str, Any]]:
        """Get GPU information."""
        import json
        gpus = []
        
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 
                 'name,adapterram,driverversion,currenthorizontalresolution,currentverticalresolution,status'],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for i in range(1, len(lines)):
                    if lines[i].strip():
                        parts = lines[i].strip().split()
                        if len(parts) >= 2:
                            gpu_name = ' '.join(parts[:-5]) if len(parts) > 5 else ' '.join(parts)
                            gpus.append({
                                'name': gpu_name,
                                'memory': ' '.join(parts[-5:-4]) if len(parts) > 5 else 'N/A',
                                'driver': ' '.join(parts[-4:-3]) if len(parts) > 5 else 'N/A',
                                'resolution': ' '.join(parts[-3:-1]) if len(parts) > 5 else 'N/A',
                                'status': parts[-1] if parts else 'N/A'
                            })
        except:
            pass
        
        if not gpus:
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 
                     "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, CurrentHorizontalResolution, CurrentVerticalResolution | ConvertTo-Json"],
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout:
                    data = json.loads(result.stdout)
                    if isinstance(data, dict):
                        data = [data]
                    for gpu in data:
                        ram_bytes = gpu.get('AdapterRAM', 0)
                        ram_gb = ram_bytes / (1024**3) if ram_bytes else 0
                        h_res = gpu.get('CurrentHorizontalResolution', 0)
                        v_res = gpu.get('CurrentVerticalResolution', 0)
                        gpus.append({
                            'name': gpu.get('Name', 'Unknown'),
                            'memory_gb': round(ram_gb, 2),
                            'driver': gpu.get('DriverVersion', 'N/A'),
                            'resolution': f"{h_res}x{v_res}" if h_res and v_res else 'N/A',
                            'status': 'OK'
                        })
            except:
                pass
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 "(Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | Measure-Object -Property UtilizationPercentage -Average).Average"],
                capture_output=True, text=True, timeout=3
            )
            usage = result.stdout.strip()
            usage = usage.replace(',', '.')
            if usage and usage.replace('.', '').isdigit():
                for gpu in gpus:
                    gpu['usage'] = float(usage)
        except:
            pass
        
        return gpus if gpus else [{'name': 'No detectada', 'memory_gb': 0, 'driver': 'N/A', 'resolution': 'N/A', 'status': 'N/A', 'usage': 0}]
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """Get memory information."""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'free': mem.free
        }
    
    @staticmethod
    def get_swap_info() -> Dict[str, Any]:
        """Get swap memory information."""
        swap = psutil.swap_memory()
        return {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent
        }
    
    @staticmethod
    def get_disk_info() -> List[Dict[str, Any]]:
        """Get disk partitions and usage."""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except:
                pass
        return partitions
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Get network information."""
        interfaces = {}
        stats = psutil.net_io_counters()
        net_if_stats = psutil.net_if_stats()
        
        for iface, addrs in psutil.net_if_addrs().items():
            interfaces[iface] = {'addresses': []}
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces[iface]['ipv4'] = addr.address
                    interfaces[iface]['netmask'] = addr.netmask
                elif addr.family == psutil.AF_LINK:
                    interfaces[iface]['mac'] = addr.address
        
        for iface, stats_data in net_if_stats.items():
            if iface in interfaces:
                interfaces[iface]['connected'] = stats_data.isup
                interfaces[iface]['speed'] = stats_data.speed
        
        return {
            'interfaces': interfaces,
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv
        }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get general system information."""
        boot_time = psutil.boot_time()
        return {
            'computer_name': socket.gethostname(),
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'boot_time': boot_time,
            'uptime': time.time() - boot_time
        }
    
    @staticmethod
    def get_current_user() -> str:
        """Get current logged in user."""
        return psutil.users()[0].name if psutil.users() else 'Unknown'
    
    @staticmethod
    def get_processes() -> List[Dict[str, Any]]:
        """Get running processes."""
        import json
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu': pinfo['cpu_percent'] or 0,
                    'memory_mb': pinfo['memory_info'].rss / (1024 * 1024) if pinfo['memory_info'] else 0,
                    'memory_percent': proc.memory_percent(),
                    'status': proc.status()
                })
            except:
                pass
        return sorted(processes, key=lambda x: x['cpu'], reverse=True)
    
    @staticmethod
    def get_installed_software() -> List[Dict[str, str]]:
        """Get installed software from Windows registry."""
        software = []
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for hkey, path in registry_paths:
            try:
                with winreg.OpenKey(hkey, path):
                    pass
            except:
                continue
            
            try:
                with winreg.OpenKey(hkey, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                version = ""
                                install_date = ""
                                publisher = ""
                                try:
                                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except:
                                    pass
                                try:
                                    install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                except:
                                    pass
                                try:
                                    publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                except:
                                    pass
                                
                                if name and name.strip():
                                    software.append({
                                        'name': name,
                                        'version': version,
                                        'install_date': install_date,
                                        'publisher': publisher
                                    })
                        except:
                            continue
            except:
                continue
        
        seen = set()
        unique_software = []
        for item in software:
            if item['name'] not in seen:
                seen.add(item['name'])
                unique_software.append(item)
        
        return sorted(unique_software, key=lambda x: x['name'].lower())
    
    @staticmethod
    def get_security_info() -> Dict[str, Any]:
        """Get security information."""
        import json
        security_info = {
            'firewall_status': 'Unknown',
            'antivirus_status': 'Unknown',
            'antivirus_name': 'N/A',
            'suspicious_processes': [],
            'open_ports': [],
            'recent_users': [],
            'running_services': [],
            'startup_programs': [],
            'network_shares': [],
            'recent_connections': []
        }
        
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                capture_output=True, text=True, timeout=10
            )
            if 'ON' in result.stdout.upper():
                security_info['firewall_status'] = 'Activo'
            elif 'OFF' in result.stdout.upper():
                security_info['firewall_status'] = 'Inactivo'
        except:
            pass
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 "Get-MpComputerStatus | Select-Object AntivirusEnabled, AntivirusSignatureLastUpdated, RealTimeProtectionEnabled | ConvertTo-Json"],
                capture_output=True, text=True, timeout=15
            )
            if result.stdout:
                data = json.loads(result.stdout)
                security_info['antivirus_status'] = 'Activo' if data.get('AntivirusEnabled') else 'Desactivado'
                if data.get('AntivirusSignatureLastUpdated'):
                    security_info['antivirus_name'] = 'Windows Defender'
                if data.get('RealTimeProtectionEnabled'):
                    security_info['antivirus_status'] += ' + Protección en tiempo real'
        except:
            pass
        
        suspicious_keywords = ['crack', 'keygen', 'patch', 'torrent', 'bitcoin', 'miner', 
                              'cryptominer', 'payload', 'rat', 'keylogger', 'stealer']
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower()
                    for keyword in suspicious_keywords:
                        if keyword in proc_name:
                            security_info['suspicious_processes'].append({
                                'name': proc.info['name'],
                                'pid': proc.info['pid'],
                                'path': proc.exe() if proc.exe() else 'N/A'
                            })
                except:
                    pass
        except:
            pass
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr:
                    security_info['open_ports'].append({
                        'port': conn.laddr.port,
                        'address': conn.laddr.ip,
                        'pid': conn.pid
                    })
        except:
            pass
        
        try:
            for user in psutil.users():
                security_info['recent_users'].append({
                    'name': user.name,
                    'host': user.host,
                    'started': time.strftime('%Y-%m-%d %H:%M', time.localtime(user.started))
                })
        except:
            pass
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, DisplayName, Status | ConvertTo-Json -Depth 2"],
                capture_output=True, text=True, timeout=20
            )
            if result.stdout:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                for svc in data[:50]:
                    security_info['running_services'].append({
                        'name': svc.get('Name', 'N/A'),
                        'display_name': svc.get('DisplayName', 'N/A'),
                        'status': svc.get('Status', 'N/A')
                    })
        except:
            pass
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | ConvertTo-Json"],
                capture_output=True, text=True, timeout=15
            )
            if result.stdout:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                for item in data[:30]:
                    security_info['startup_programs'].append({
                        'name': item.get('Name', 'N/A'),
                        'command': item.get('Command', 'N/A')[:100],
                        'location': item.get('Location', 'N/A')
                    })
        except:
            pass
        
        try:
            result = subprocess.run(
                ['net', 'share'], capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Shared' in line or 'Recursos' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        security_info['network_shares'].append(line.strip())
        except:
            pass
        
        return security_info
    
    @staticmethod
    def get_motherboard_info() -> Dict[str, Any]:
        """Get motherboard information."""
        info = {'manufacturer': 'N/A', 'product': 'N/A', 'version': 'N/A', 'serial': 'N/A'}
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version, SerialNumber | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10
            )
            if result.stdout:
                import json
                data = json.loads(result.stdout)
                info = {
                    'manufacturer': data.get('Manufacturer', 'N/A'),
                    'product': data.get('Product', 'N/A'),
                    'version': data.get('Version', 'N/A'),
                    'serial': data.get('SerialNumber', 'N/A')
                }
        except:
            pass
        return info
    
    @staticmethod
    def get_bios_info() -> Dict[str, Any]:
        """Get BIOS information."""
        info = {'manufacturer': 'N/A', 'version': 'N/A', 'date': 'N/A'}
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 "Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10
            )
            if result.stdout:
                import json
                data = json.loads(result.stdout)
                date = data.get('ReleaseDate', '')
                if date:
                    date = date[:8]
                info = {
                    'manufacturer': data.get('Manufacturer', 'N/A'),
                    'version': data.get('SMBIOSBIOSVersion', 'N/A'),
                    'date': date
                }
        except:
            pass
        return info
    
    @staticmethod
    def get_battery_info() -> Dict[str, Any]:
        """Get battery information."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged_in': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1
                }
        except:
            pass
        return {'percent': 0, 'plugged_in': True, 'time_left': -1}
    
    @staticmethod
    def get_boot_info() -> Dict[str, Any]:
        """Get boot information."""
        import datetime
        boot_time = psutil.boot_time()
        boot_datetime = datetime.datetime.fromtimestamp(boot_time)
        return {
            'boot_time': boot_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime_seconds': time.time() - boot_time
        }
