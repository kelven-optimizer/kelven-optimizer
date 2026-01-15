# Kelven Optimizer PRO v4.1 - Hardware Smart Edition
# Sistema Inteligente de Detecção e Aplicação de Tweaks

import sys
import subprocess
import importlib.util

def install_dependencies():
    """Instala dependências automaticamente"""
    dependencies = {
        'psutil': 'psutil',
        'requests': 'requests',
        'packaging': 'packaging',
        'GPUtil': 'gputil'
    }
    print("📦 Verificando dependências...")
    for module, package in dependencies.items():
        if importlib.util.find_spec(module) is None:
            print(f"📥 Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            except Exception as e:
                print(f"❌ Erro ao instalar {package}: {e}")

try:
    install_dependencies()
except:
    pass

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import json
import threading
import time
from datetime import datetime
import winreg
import ctypes
import platform
import shutil
import psutil
from collections import deque
from typing import Dict, List
import requests
from packaging import version
import queue

try:
    import GPUtil
except:
    GPUtil = None

# ========= CONFIGURAÇÕES PREMIUM =========
class AdvancedConfig:
    APP_NAME = "Kelven Optimizer PRO"
    VERSION = "2.0"
    AUTHOR = "kelvenapk"
    GITHUB = "https://github.com/kelvenapk"
    DISCORD = "https://discord.gg/gNPhS3m3QF"
    
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    CONFIG_FILE = os.path.join(BASE_DIR, "kelven_config_v10.json")
    BACKUP_DIR = os.path.join(BASE_DIR, "backups")
    LOG_FILE = os.path.join(BASE_DIR, "kelven_optimizer.log")
    PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
    UPDATE_DIR = os.path.join(BASE_DIR, "updates")
    
    COLORS = {
        'primary': '#00D4FF',
        'secondary': '#FF6B6B',
        'success': '#4ECDC4',
        'warning': '#FFE66D',
        'danger': '#FF4757',
        'info': '#00C9FF',
        'dark': '#0F0F0F',
        'darker': '#080808',
        'card': '#1C1C1C',
        'hover': '#252525',
        'border': '#2A2A2A',
        'text': '#FFFFFF',
        'text_secondary': '#A0A0A0',
        'terminal': '#00FF88',
        'purple': '#A855F7',
        'cyan': '#00E5FF',
        'orange': '#FF8C00',
        'gold': '#FFD700',
        'amd_red': '#ED1C24',
        'nvidia_green': '#76B900',
        'intel_blue': '#0071C5',
        'gradient_start': '#667eea',
        'gradient_end': '#764ba2',
        'neon_blue': '#00F0FF',
        'neon_pink': '#FF006E',
        'neon_green': '#00FF41'
    }

# ========= SISTEMA DE LOGGING =========
class Logger:
    _instance = None
    
    @staticmethod
    def get_instance():
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance
    
    def __init__(self):
        self.callback = None
        self.logs = deque(maxlen=1000)
        self.lock = threading.Lock()
        
    def set_callback(self, callback):
        self.callback = callback
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{level}] {message}"
        
        with self.lock:
            self.logs.append(formatted_msg)
            
        try:
            with open(AdvancedConfig.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted_msg + "\n")
        except:
            pass
            
        if self.callback:
            self.callback(formatted_msg)
            
    def get_recent_logs(self, count=100):
        with self.lock:
            return list(self.logs)[-count:]

# ========= UTILITÁRIOS DO SISTEMA =========
class SystemUtils:
    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    @staticmethod
    def run_elevated():
        if getattr(sys, 'frozen', False):
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    def execute_cmd(self, cmd, timeout=30):
        if not isinstance(cmd, str):
            return False
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, shell=True, capture_output=True, startupinfo=startupinfo, 
                          creationflags=subprocess.CREATE_NO_WINDOW, timeout=timeout)
            return result.returncode == 0
        except:
            return False

    def safe_reg_write(self, root, path, name, value, reg_type):
        try:
            winreg.CreateKey(root, path)
            with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, name, 0, reg_type, value)
            return True
        except Exception as e:
            print(f"❌ Reg Error: {e}")
            return False

    @staticmethod
    def get_system_info():
        info = {
            'os': f"{platform.system()} {platform.release()}",
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'ram_total': round(psutil.virtual_memory().total / (1024**3), 1),
            'ram_available': round(psutil.virtual_memory().available / (1024**3), 1),
            'disk_total': round(psutil.disk_usage('/').total / (1024**3), 1),
            'disk_free': round(psutil.disk_usage('/').free / (1024**3), 1),
        }
        
        try:
            info['cpu_name'] = platform.processor()
            if 'AMD' in info['cpu_name'].upper():
                info['cpu_brand'] = 'AMD'
                info['cpu_color'] = AdvancedConfig.COLORS['amd_red']
            elif 'INTEL' in info['cpu_name'].upper():
                info['cpu_brand'] = 'Intel'
                info['cpu_color'] = AdvancedConfig.COLORS['intel_blue']
            else:
                info['cpu_brand'] = 'Unknown'
                info['cpu_color'] = AdvancedConfig.COLORS['primary']
        except:
            info['cpu_name'] = 'Unknown'
            info['cpu_brand'] = 'Unknown'
            info['cpu_color'] = AdvancedConfig.COLORS['primary']
            
        return info

# ========= DETECTOR DE HARDWARE =========
class HardwareDetector:
    def __init__(self):
        self.cpu_info = {'name': 'Unknown', 'brand': 'Unknown', 'model': 'Unknown', 'color': AdvancedConfig.COLORS['primary']}
        self.gpu_info = {'name': 'Unknown', 'brand': 'Unknown', 'model': 'Unknown', 'color': AdvancedConfig.COLORS['primary'], 'is_dedicated': False}
        self.memory_info = {'total': 0, 'available': 0, 'used': 0, 'percent': 0}
        self.motherboard_info = {'manufacturer': 'Unknown', 'model': 'Unknown'}
        
        try:
            sys_info = SystemUtils.get_system_info()
            self.cpu_info.update({
                'name': sys_info.get('cpu_name', 'Unknown'),
                'brand': sys_info.get('cpu_brand', 'Unknown'),
                'model': sys_info.get('cpu_brand', 'Unknown'),
                'color': sys_info.get('cpu_color', AdvancedConfig.COLORS['primary'])
            })
            
            memory = psutil.virtual_memory()
            self.memory_info = {
                'total': round(memory.total / (1024**3), 1),
                'available': round(memory.available / (1024**3), 1),
                'used': round(memory.used / (1024**3), 1),
                'percent': memory.percent
            }
        except:
            pass

# ========= GERENCIADOR DE SISTEMA =========
class SystemManager:
    def __init__(self):
        self.utils = SystemUtils()
        self.logger = Logger.get_instance()
    
    def cleanup_pro(self, mode="normal"):
        """Sistema de limpeza profissional"""
        results = {"cleaned": 0, "errors": [], "freed_space": 0}
        
        try:
            temp_dirs = [
                os.environ.get('TEMP'),
                os.environ.get('TMP'),
                os.path.join(os.environ.get('WINDIR', ''), 'Temp')
            ]
            
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        for item in os.listdir(temp_dir):
                            item_path = os.path.join(temp_dir, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.unlink(item_path)
                                    results["cleaned"] += 1
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path)
                                    results["cleaned"] += 1
                            except:
                                pass
                    except:
                        pass
            
            self.logger.log(f"Cleanup completed: {results['cleaned']} items", "SUCCESS")
            
        except Exception as e:
            results["errors"].append(f"Fatal error: {e}")
            self.logger.log(f"Cleanup error: {e}", "ERROR")
        
        return results

# ========= MONITOR DE PERFORMANCE =========
class PerformanceMonitor(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = True
        self.callbacks = []
        self.data = {
            'cpu': deque(maxlen=60),
            'ram': deque(maxlen=60),
            'gpu': deque(maxlen=60),
            'disk': 0,
            'temp': 0
        }
        
    def register_callback(self, callback):
        self.callbacks.append(callback)
        
    def run(self):
        while self.running:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                self.data['cpu'].append(cpu_percent)
                
                ram_percent = psutil.virtual_memory().percent
                self.data['ram'].append(ram_percent)
                
                self.data['disk'] = psutil.disk_usage('C:\\').percent
                
                # Temperatura da CPU
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries:
                                self.data['temp'] = entries[0].current
                                break
                    else:
                        self.data['temp'] = 0
                except:
                    self.data['temp'] = 0
                
                for callback in self.callbacks:
                    callback(self.data)
                
                time.sleep(1)
            except:
                pass
    
    def stop(self):
        self.running = False

# ========= ENGINE DE TWEAKS COMPLETO =========
class SmartTweaksEngine:
    def __init__(self):
        self.utils = SystemUtils()
        self.logger = Logger.get_instance()
        self.hardware_detector = HardwareDetector()
        self.tweak_database = self.build_tweak_database()
    
    def build_tweak_database(self):
        """Constrói banco de dados completo de tweaks"""
        return {
            'cpu': self.get_cpu_tweaks(),
            'gpu': self.get_gpu_tweaks(),
            'nvidia': self.get_nvidia_tweaks(),
            'amd': self.get_amd_tweaks(),
            'memory': self.get_memory_tweaks(),
            'network': self.get_network_tweaks(),
            'gaming': self.get_gaming_tweaks(),
            'system': self.get_system_tweaks(),
            'debloat': self.get_debloat_tweaks(),
            'kernel': self.get_kernel_tweaks()
        }
    
    def get_kernel_tweaks(self):
        """Tweaks avançados do Kernel do Windows"""
        return [
            {'name': 'Kernel Timer Resolution', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "GlobalTimerResolutionRequests", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Kernel Paging', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Kernel DPC Watchdog', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "DpcWatchdogProfileOffset", 10000, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Kernel Stack Size', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "KernelStackSize", 0x6000, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Kernel DEP', 'category': 'KERNEL', 'registry': [], 'commands': ["bcdedit /set nx AlwaysOff"]},
            {'name': 'Kernel Priority Separation', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 38, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Kernel Address Space Layout', 'category': 'KERNEL', 'registry': [], 'commands': ["bcdedit /set nointegritychecks on"]},
            {'name': 'Kernel Interrupt Steering', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "EnableRSS", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Kernel Mitigations', 'category': 'KERNEL', 'registry': [], 'commands': ["bcdedit /set allowedinmemorysettings 0x0"]},
            {'name': 'Kernel TSC Sync Policy', 'category': 'KERNEL', 'registry': [], 'commands': ["bcdedit /set tscsyncpolicy Enhanced"]},
            {'name': 'Disable Spectre/Meltdown', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverride", 3, winreg.REG_DWORD), (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverrideMask", 3, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Kernel DMA Protection', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\DmaSecurity", "AllowExternalDevices", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Kernel Large Pages', 'category': 'KERNEL', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargePageMinimum", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Kernel Debugging', 'category': 'KERNEL', 'registry': [], 'commands': ["bcdedit /set debug off"]},
            {'name': 'Kernel Boot Optimization', 'category': 'KERNEL', 'registry': [], 'commands': ["bcdedit /set bootmenupolicy Legacy", "bcdedit /timeout 3"]}
        ]
    
    def get_debloat_tweaks(self):
        """Debloat completo do Windows - mantém Windows Store"""
        return [
            {'name': 'Remove OneDrive', 'category': 'DEBLOAT', 'registry': [], 'commands': ["taskkill /f /im OneDrive.exe", "C:\\Windows\\SysWOW64\\OneDriveSetup.exe /uninstall"]},
            {'name': 'Disable Xbox Services', 'category': 'DEBLOAT', 'registry': [], 'commands': ["sc config XblAuthManager start= disabled", "sc config XblGameSave start= disabled", "sc config XboxGipSvc start= disabled", "sc config XboxNetApiSvc start= disabled"]},
            {'name': 'Disable Cortana Process', 'category': 'DEBLOAT', 'registry': [], 'commands': ["taskkill /f /im SearchUI.exe"]},
            {'name': 'Disable Delivery Optimization', 'category': 'DEBLOAT', 'registry': [], 'commands': ["sc config DoSvc start= disabled"]},
            {'name': 'Disable Sync Host', 'category': 'DEBLOAT', 'registry': [], 'commands': ["sc config OneSyncSvc start= disabled"]},
            {'name': 'Disable Windows Spotlight', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "RotatingLockScreenEnabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Consumer Features', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableWindowsConsumerFeatures", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable App Suggestions', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SystemPaneSuggestionsEnabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Live Tiles', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\PushNotifications", "NoTileApplicationNotification", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable People Icon', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\People", "PeopleBand", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable News and Interests', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\Windows Feeds", "EnableFeeds", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Meet Now', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer", "HideSCAMeetNow", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Task View', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Unnecessary Services', 'category': 'DEBLOAT', 'registry': [], 'commands': [
                "sc config MapsBroker start= disabled",
                "sc config lfsvc start= disabled",
                "sc config SharedAccess start= disabled",
                "sc config WMPNetworkSvc start= disabled",
                "sc config CscService start= disabled",
                "sc config PhoneSvc start= disabled",
                "sc config SensorDataService start= disabled",
                "sc config SensrSvc start= disabled",
                "sc config SensorService start= disabled",
                "sc config ShellHWDetection start= disabled",
                "sc config ScDeviceEnum start= disabled",
                "sc config SSDPSRV start= disabled",
                "sc config WiaRpc start= disabled",
                "sc config OneSyncSvc start= disabled",
                "sc config MessagingService start= disabled",
                "sc config PimIndexMaintenanceSvc start= disabled",
                "sc config UserDataSvc start= disabled",
                "sc config UnistoreSvc start= disabled",
                "sc config BcastDVRUserService start= disabled",
                "sc config Fax start= disabled",
                "sc config fhsvc start= disabled",
                "sc config dmwappushservice start= disabled",
                "sc config TrkWks start= disabled",
                "sc config WpcMonSvc start= disabled",
                "sc config RetailDemo start= disabled",
                "sc config diagsvc start= disabled",
                "sc config WerSvc start= disabled",
                "sc config Wecsvc start= disabled",
                "sc config stisvc start= disabled",
                "sc config wisvc start= disabled"
            ]},
            {'name': 'Optimize RAM Usage', 'category': 'DEBLOAT', 'registry': [
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", 0, winreg.REG_DWORD),
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", 1, winreg.REG_DWORD),
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", 0, winreg.REG_DWORD),
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "NonPagedPoolSize", 0, winreg.REG_DWORD),
                (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "PagedPoolSize", 0, winreg.REG_DWORD)
            ], 'commands': []},
            {'name': 'Disable Runtime Broker', 'category': 'DEBLOAT', 'registry': [(r"SYSTEM\CurrentControlSet\Services\TimeBrokerSvc", "Start", 4, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Windows Search Indexing', 'category': 'DEBLOAT', 'registry': [], 'commands': ["sc config WSearch start= disabled"]},
            {'name': 'Disable SysMain (Superfetch)', 'category': 'DEBLOAT', 'registry': [], 'commands': ["sc config SysMain start= disabled"]},
            {'name': 'Disable Windows Tips', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Background Apps', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Startup Apps', 'category': 'DEBLOAT', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", "DisableAll", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Minimal Visual Effects', 'category': 'DEBLOAT', 'registry': [
                (r"Control Panel\Desktop", "DragFullWindows", "0", winreg.REG_SZ),
                (r"Control Panel\Desktop", "FontSmoothing", "0", winreg.REG_SZ),
                (r"Control Panel\Desktop\WindowMetrics", "MinAnimate", "0", winreg.REG_SZ),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ListviewAlphaSelect", 0, winreg.REG_DWORD),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAnimations", 0, winreg.REG_DWORD),
                (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2, winreg.REG_DWORD)
            ], 'commands': []},
            {'name': 'Disable Scheduled Tasks', 'category': 'DEBLOAT', 'registry': [], 'commands': [
                "schtasks /Change /TN \"Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\Application Experience\\ProgramDataUpdater\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\Autochk\\Proxy\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\Customer Experience Improvement Program\\UsbCeip\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\Maintenance\\WinSAT\" /Disable",
                "schtasks /Change /TN \"Microsoft\\Windows\\Windows Error Reporting\\QueueReporting\" /Disable"
            ]}
        ]
    
    def get_cpu_tweaks(self):
        return [
            {'name': 'Disable Core Parking', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318d583", "ValueMax", 0, winreg.REG_DWORD)], 'commands': ["powercfg -setacvalueindex SCHEME_CURRENT SUB_PROCESSOR 0cc5b647-c1df-4637-891a-dec35c318d583 0"]},
            {'name': 'CPU Priority Optimization', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 38, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable CPU Throttling', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\5d76a2ca-e8c0-402f-a133-2158492d58ad", "Attributes", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Maximum CPU Performance', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-33abaf5935ec", "Attributes", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable CPU Idle States', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Processor", "Capabilities", 516198, winreg.REG_DWORD)], 'commands': []},
            {'name': 'CPU Scheduling Priority', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "IoPageLockLimit", 983040, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable CPU Power Saving', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Power", "HibernateEnabled", 0, winreg.REG_DWORD)], 'commands': ["powercfg -h off"]},
            {'name': 'CPU Affinity Optimization', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\PriorityControl", "IRQ8Priority", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable CPU C-States', 'category': 'CPU', 'registry': [], 'commands': ["powercfg -setacvalueindex SCHEME_CURRENT SUB_PROCESSOR CPMINCORES 100"]},
            {'name': 'CPU Turbo Boost Max', 'category': 'CPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\be337238-0d82-4146-a960-4f3749d470c7", "Attributes", 0, winreg.REG_DWORD)], 'commands': []}
        ]
    
    def get_gpu_tweaks(self):
        return [
            {'name': 'GPU Hardware Acceleration', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 2, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable GPU Power Saving', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "DisablePowerManagement", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'GPU Max Performance Mode', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "TdrLevel", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable GPU Preemption', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler", "EnablePreemption", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'GPU TDR Delay Increase', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "TdrDelay", 60, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable GPU Timeout', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "TdrDdiDelay", 60, winreg.REG_DWORD)], 'commands': []},
            {'name': 'GPU Shader Cache', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "EnableShaderCache", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable GPU ULPS', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "EnableUlps", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'GPU Priority High', 'category': 'GPU', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority", 8, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable GPU Throttling', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "DisableThrottling", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'GPU MSI Mode', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Enum\PCI", "MSISupported", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable GPU Power Gating', 'category': 'GPU', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "PP_ThermalAutoThrottlingEnable", 0, winreg.REG_DWORD)], 'commands': []}
        ]
    
    def get_nvidia_tweaks(self):
        return [
            {'name': 'NVIDIA Low Latency Mode', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "DisplayPowerSaving", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Max Performance', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\FTS", "EnableRID61684", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Shader Cache', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "ShaderCache", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Threaded Optimization', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "ThreadedOptimization", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Power Management', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "PowerMizerEnable", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Ansel Disable', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "AnselEnable", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Telemetry Disable', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\NvControlPanel2\Client", "OptInOrOutPreference", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA CUDA Force P2 State', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "CUDAForceP2State", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Disable HDCP', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "HDCP", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'NVIDIA Disable GSync', 'category': 'NVIDIA', 'registry': [(r"SOFTWARE\NVIDIA Corporation\Global\NVTweak", "GSync", 0, winreg.REG_DWORD)], 'commands': []}
        ]
    
    def get_amd_tweaks(self):
        return [
            {'name': 'AMD Radeon Anti-Lag', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "AntiLag", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Radeon Boost', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "RadeonBoost", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Enhanced Sync', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "EnhancedSync", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Disable ULPS', 'category': 'AMD', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "EnableUlps", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Tessellation Mode', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "TessellationMode", 2, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Surface Format Optimization', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "SurfaceFormatReplacements", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Disable Frame Rate Target', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "FrameRateTarget", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Power Efficiency Disable', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "PowerEfficiency", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD Chill Disable', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "Chill", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'AMD FreeSync Optimization', 'category': 'AMD', 'registry': [(r"SOFTWARE\AMD\CN", "FreeSync", 1, winreg.REG_DWORD)], 'commands': []}
        ]
    
    def get_memory_tweaks(self):
        return [
            {'name': 'Disable Paging Executive', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Large System Cache', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Clear PageFile at Shutdown', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Memory Compression', 'category': 'MEMORY', 'registry': [], 'commands': ["powershell -Command \"Disable-MMAgent -MemoryCompression\""]},
            {'name': 'Optimize Memory Pool', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "PoolUsageMaximum", 60, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Second Level Cache', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "SecondLevelDataCache", 1024, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Prefetcher', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnablePrefetcher", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Superfetch', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnableSuperfetch", 0, winreg.REG_DWORD)], 'commands': ["sc config SysMain start= disabled"]},
            {'name': 'Memory Priority', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "SystemPages", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Page Combining', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePageCombining", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Optimize Paging', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "PagingFiles", "C:\\pagefile.sys 0 0", winreg.REG_SZ)], 'commands': []},
            {'name': 'Memory Standby List', 'category': 'MEMORY', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearStandbyListOnLowMemory", 1, winreg.REG_DWORD)], 'commands': []}
        ]
    
    def get_network_tweaks(self):
        return [
            {'name': 'TCP/IP Optimization', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "Tcp1323Opts", 1, winreg.REG_DWORD), (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "DefaultTTL", 64, winreg.REG_DWORD)], 'commands': ["netsh int tcp set global autotuninglevel=normal"]},
            {'name': 'Disable Network Throttling', 'category': 'NETWORK', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", 4294967295, winreg.REG_DWORD)], 'commands': []},
            {'name': 'TCP Window Scaling', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpWindowSize", 65535, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Nagle Algorithm', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces", "TcpAckFrequency", 1, winreg.REG_DWORD), (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces", "TCPNoDelay", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Enable RSS', 'category': 'NETWORK', 'registry': [], 'commands': ["netsh int tcp set global rss=enabled"]},
            {'name': 'Enable Chimney Offload', 'category': 'NETWORK', 'registry': [], 'commands': ["netsh int tcp set global chimney=enabled"]},
            {'name': 'Disable NetBIOS', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\NetBT\Parameters", "EnableLMHOSTS", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'DNS Cache Optimization', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Dnscache\Parameters", "MaxCacheTtl", 86400, winreg.REG_DWORD)], 'commands': []},
            {'name': 'MTU Optimization', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces", "MTU", 1500, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Large Send Offload', 'category': 'NETWORK', 'registry': [], 'commands': ["netsh int tcp set global dca=enabled"]},
            {'name': 'QoS Packet Scheduler', 'category': 'NETWORK', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\Psched", "NonBestEffortLimit", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Network Adapter Power', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0000", "PnPCapabilities", 24, winreg.REG_DWORD)], 'commands': []},
            {'name': 'TCP Timestamps', 'category': 'NETWORK', 'registry': [(r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "Timestamps", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable ECN', 'category': 'NETWORK', 'registry': [], 'commands': ["netsh int tcp set global ecncapability=disabled"]},
            {'name': 'TCP Fast Open', 'category': 'NETWORK', 'registry': [], 'commands': ["netsh int tcp set global fastopen=enabled"]}
        ]
    
    def get_gaming_tweaks(self):
        return [
            {'name': 'Enable Game Mode', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\GameBar", "AutoGameModeEnabled", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Game Bar', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Gaming Priority', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority", 8, winreg.REG_DWORD), (r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Priority", 6, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Game DVR', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR", "GameDVR_Enabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Fullscreen Optimizations', 'category': 'GAMING', 'registry': [(r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Xbox Services', 'category': 'GAMING', 'registry': [], 'commands': ["sc config XboxGipSvc start= disabled", "sc config XblAuthManager start= disabled"]},
            {'name': 'Gaming Scheduling', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Scheduling Category", "High", winreg.REG_SZ)], 'commands': []},
            {'name': 'Disable VSync', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\DirectX", "DisableVSync", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Mouse Precision', 'category': 'GAMING', 'registry': [(r"Control Panel\Mouse", "MouseSpeed", "0", winreg.REG_SZ), (r"Control Panel\Mouse", "MouseThreshold1", "0", winreg.REG_SZ)], 'commands': []},
            {'name': 'Disable Mouse Acceleration', 'category': 'GAMING', 'registry': [(r"Control Panel\Mouse", "MouseThreshold2", "0", winreg.REG_SZ)], 'commands': []},
            {'name': 'Gaming Audio Priority', 'category': 'GAMING', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Audio Priority", 8, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Sticky Keys', 'category': 'GAMING', 'registry': [(r"Control Panel\Accessibility\StickyKeys", "Flags", "506", winreg.REG_SZ)], 'commands': []},
            {'name': 'Disable Filter Keys', 'category': 'GAMING', 'registry': [(r"Control Panel\Accessibility\Keyboard Response", "Flags", "122", winreg.REG_SZ)], 'commands': []},
            {'name': 'Disable Toggle Keys', 'category': 'GAMING', 'registry': [(r"Control Panel\Accessibility\ToggleKeys", "Flags", "58", winreg.REG_SZ)], 'commands': []},
            {'name': 'Gaming Power Plan', 'category': 'GAMING', 'registry': [], 'commands': ["powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61"]}
        ]
    
    def get_system_tweaks(self):
        return [
            {'name': 'Disable Telemetry', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", 0, winreg.REG_DWORD)], 'commands': ["sc config DiagTrack start= disabled"]},
            {'name': 'Disable Windows Animations', 'category': 'SYSTEM', 'registry': [(r"Control Panel\Desktop\WindowMetrics", "MinAnimate", "0", winreg.REG_SZ)], 'commands': []},
            {'name': 'Power Plan Ultimate', 'category': 'SYSTEM', 'registry': [], 'commands': ["powercfg -duplicatescheme 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "powercfg -h off"]},
            {'name': 'Disable Windows Search', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config WSearch start= disabled"]},
            {'name': 'Disable Windows Update', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU", "NoAutoUpdate", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Cortana', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Windows Defender', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", 1, winreg.REG_DWORD)], 'commands': ["sc config WinDefend start= disabled"]},
            {'name': 'Disable Firewall', 'category': 'SYSTEM', 'registry': [], 'commands': ["netsh advfirewall set allprofiles state off"]},
            {'name': 'Disable UAC', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "EnableLUA", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable System Restore', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore", "DisableSR", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Error Reporting', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Maintenance', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance", "MaintenanceDisabled", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Background Apps', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", 1, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Transparency', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Startup Delay', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Serialize", "StartupDelayInMSec", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Hibernation', 'category': 'SYSTEM', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Power", "HibernateEnabled", 0, winreg.REG_DWORD)], 'commands': ["powercfg -h off"]},
            {'name': 'Disable Fast Startup', 'category': 'SYSTEM', 'registry': [(r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Windows Tips', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Activity History', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", 0, winreg.REG_DWORD)], 'commands': []},
            {'name': 'Disable Location Tracking', 'category': 'SYSTEM', 'registry': [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location", "Value", "Deny", winreg.REG_SZ)], 'commands': []},
            {'name': 'Visual Effects Performance', 'category': 'SYSTEM', 'registry': [(r"Control Panel\Desktop", "UserPreferencesMask", bytes([0x90, 0x12, 0x03, 0x80, 0x10, 0x00, 0x00, 0x00]), winreg.REG_BINARY)], 'commands': []},
            {'name': 'Disable Print Spooler', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config Spooler start= disabled"]},
            {'name': 'Disable Fax Service', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config Fax start= disabled"]},
            {'name': 'Disable Remote Registry', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config RemoteRegistry start= disabled"]},
            {'name': 'Disable Windows Biometric', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config WbioSrvc start= disabled"]},
            {'name': 'Disable Bluetooth Support', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config bthserv start= disabled"]},
            {'name': 'Disable Tablet Input', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config TabletInputService start= disabled"]},
            {'name': 'Disable Windows Mobile Hotspot', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config icssvc start= disabled"]},
            {'name': 'Disable Diagnostic Services', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config DPS start= disabled", "sc config WdiServiceHost start= disabled", "sc config WdiSystemHost start= disabled"]},
            {'name': 'Disable Windows Time', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config W32Time start= disabled"]},
            {'name': 'Disable Geolocation Service', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config lfsvc start= disabled"]},
            {'name': 'Disable Retail Demo', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config RetailDemo start= disabled"]},
            {'name': 'Disable Phone Service', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config PhoneSvc start= disabled"]},
            {'name': 'Disable Sensor Services', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config SensrSvc start= disabled", "sc config SensorDataService start= disabled"]},
            {'name': 'Disable Windows Insider', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config wisvc start= disabled"]},
            {'name': 'Disable Parental Controls', 'category': 'SYSTEM', 'registry': [], 'commands': ["sc config WpcMonSvc start= disabled"]}
        ]
    
    def get_compatible_tweaks(self, category=None):
        """Retorna tweaks compatíveis"""
        all_tweaks = []
        for cat, tweaks in self.tweak_database.items():
            if category is None or cat.upper() == category.upper():
                all_tweaks.extend(tweaks)
        return all_tweaks
    
    def apply_compatible_tweaks(self, category=None):
        """Aplica tweaks compatíveis"""
        tweaks = self.get_compatible_tweaks(category)
        applied = 0
        errors = []
        
        for tweak in tweaks:
            try:
                # Aplicar registry
                for reg_path, name, value, reg_type in tweak.get('registry', []):
                    root = winreg.HKEY_LOCAL_MACHINE if "SYSTEM" in reg_path or "SOFTWARE" in reg_path else winreg.HKEY_CURRENT_USER
                    self.utils.safe_reg_write(root, reg_path, name, value, reg_type)
                
                # Executar comandos
                for cmd in tweak.get('commands', []):
                    if cmd:
                        self.utils.execute_cmd(cmd)
                
                applied += 1
                self.logger.log(f"✅ {tweak['name']}", "SUCCESS")
            except Exception as e:
                errors.append(str(e))
                self.logger.log(f"❌ {tweak['name']}: {e}", "ERROR")
        
        return applied, errors

# ========= INTERFACE PRINCIPAL =========
class KelvenOptimizerPRO:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{AdvancedConfig.APP_NAME} v{AdvancedConfig.VERSION}")
        self.root.geometry("1600x900")
        self.root.configure(bg=AdvancedConfig.COLORS['dark'])
        
        # Ícone
        try:
            icon_path = os.path.join(AdvancedConfig.BASE_DIR, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.utils = SystemUtils()
        self.logger = Logger.get_instance()
        self.logger.set_callback(self.update_terminal)
        self.hardware_detector = HardwareDetector()
        self.tweaks_engine = SmartTweaksEngine()
        self.system_manager = SystemManager()
        self.performance_monitor = PerformanceMonitor()
        
        self.config = {}
        self.metric_labels = {}
        
        for directory in [AdvancedConfig.BACKUP_DIR, AdvancedConfig.PROFILES_DIR, AdvancedConfig.UPDATE_DIR]:
            os.makedirs(directory, exist_ok=True)
        
        self.setup_ui()
        self.performance_monitor.register_callback(self.update_performance_data)
        self.performance_monitor.start()
        self.root.after(100, self.update_ui_loop)
        self.root.after(500, self.show_welcome_beta)
        self.root.after(3500, self.show_dashboard)
    
    def on_closing(self):
        """Tela de despedida ao fechar"""
        # Parar monitor de performance
        try:
            self.performance_monitor.stop()
        except:
            pass
        
        # Criar janela de despedida
        goodbye_window = tk.Toplevel(self.root)
        goodbye_window.title("Até logo!")
        goodbye_window.geometry("500x300")
        goodbye_window.configure(bg=AdvancedConfig.COLORS['dark'])
        goodbye_window.overrideredirect(True)
        
        # Centralizar
        goodbye_window.update_idletasks()
        x = (goodbye_window.winfo_screenwidth() // 2) - (250)
        y = (goodbye_window.winfo_screenheight() // 2) - (150)
        goodbye_window.geometry(f"500x300+{x}+{y}")
        
        # Logo
        tk.Label(goodbye_window, text="⚡", font=("Segoe UI", 64, "bold"),
                fg=AdvancedConfig.COLORS['neon_blue'], bg=goodbye_window['bg']).pack(pady=(40, 20))
        
        # Mensagem
        tk.Label(goodbye_window, text="Obrigado por usar!", font=("Segoe UI", 24, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=goodbye_window['bg']).pack(pady=(0, 10))
        
        tk.Label(goodbye_window, text="Kelven Optimizer PRO v2.0", font=("Segoe UI", 12),
                fg=AdvancedConfig.COLORS['text_secondary'], bg=goodbye_window['bg']).pack(pady=(0, 30))
        
        tk.Label(goodbye_window, text="💙 Desenvolvido por kelvenapk", font=("Segoe UI", 10),
                fg=AdvancedConfig.COLORS['primary'], bg=goodbye_window['bg']).pack()
        
        # Fechar após 2 segundos
        def close_all():
            try:
                goodbye_window.destroy()
            except:
                pass
            try:
                self.root.destroy()
            except:
                pass
        
        goodbye_window.after(2000, close_all)
        self.root.withdraw()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=AdvancedConfig.COLORS['dark'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_header(main_frame)
        self.create_sidebar(main_frame)
        self.create_content_area(main_frame)
        self.create_floating_action_buttons()
    
    def create_header(self, parent):
        self.header = tk.Frame(parent, bg=AdvancedConfig.COLORS['darker'], height=70)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        logo_frame = tk.Frame(self.header, bg=self.header['bg'])
        logo_frame.pack(side=tk.LEFT, padx=30)
        
        tk.Label(logo_frame, text="⚡", font=("Segoe UI", 28, "bold"), 
                fg=AdvancedConfig.COLORS['primary'], bg=logo_frame['bg']).pack(side=tk.LEFT)
        
        title_frame = tk.Frame(logo_frame, bg=logo_frame['bg'])
        title_frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(title_frame, text="KELVEN OPTIMIZER PRO", 
                font=("Segoe UI", 16, "bold"), 
                fg=AdvancedConfig.COLORS['text'], bg=logo_frame['bg']).pack(anchor=tk.W)
        
        tk.Label(title_frame, text=f"v{AdvancedConfig.VERSION} | Hardware Smart", 
                font=("Segoe UI", 9), 
                fg=AdvancedConfig.COLORS['text_secondary'], bg=logo_frame['bg']).pack(anchor=tk.W)
    
    def create_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=AdvancedConfig.COLORS['darker'], width=300, relief=tk.FLAT, bd=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Logo section com animação
        logo_section = tk.Frame(self.sidebar, bg=AdvancedConfig.COLORS['darker'], height=100)
        logo_section.pack(fill=tk.X, pady=(20, 30))
        logo_section.pack_propagate(False)
        
        self.sidebar_logo = tk.Label(logo_section, text="⚡", font=("Segoe UI", 48, "bold"),
                fg=AdvancedConfig.COLORS['neon_blue'], bg=logo_section['bg'])
        self.sidebar_logo.pack()
        self.animate_sidebar_logo()
        
        # Navigation items com ícones maiores e hover effect
        nav_items = [
            ("🏠 Início", self.show_dashboard, AdvancedConfig.COLORS['primary']),
            ("🔍 Hardware", self.show_hardware_info, AdvancedConfig.COLORS['success']),
            ("⚡ Tweaks", self.show_smart_tweaks, AdvancedConfig.COLORS['warning']),
            ("🎮 Gaming", self.show_gaming_mode, AdvancedConfig.COLORS['purple']),
            ("🧹 Limpeza", self.show_cleanup_pro, AdvancedConfig.COLORS['info']),
            ("🚀 Inicialização", self.show_startup_apps, AdvancedConfig.COLORS['orange']),
            ("🔄 Atualizações", self.show_updates, AdvancedConfig.COLORS['neon_blue']),
            ("⚙️ Configurações", self.show_settings, AdvancedConfig.COLORS['text_secondary']),
            ("ℹ️ Sobre", self.show_about, AdvancedConfig.COLORS['cyan'])
        ]
        
        for text, command, color in nav_items:
            btn_frame = tk.Frame(self.sidebar, bg=self.sidebar['bg'])
            btn_frame.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 12, "bold"), 
                          fg=AdvancedConfig.COLORS['text'], bg=self.sidebar['bg'],
                          bd=0, padx=30, pady=15, anchor=tk.W, cursor='hand2', 
                          command=command, relief=tk.FLAT, activebackground=AdvancedConfig.COLORS['hover'])
            btn.pack(fill=tk.X)
            
            # Hover effects com borda colorida
            def on_enter(e, b=btn, c=color, f=btn_frame):
                b.config(bg=AdvancedConfig.COLORS['hover'])
                indicator = tk.Frame(f, bg=c, width=4)
                indicator.place(x=0, y=0, relheight=1)
                b.indicator = indicator
            
            def on_leave(e, b=btn):
                b.config(bg=self.sidebar['bg'])
                if hasattr(b, 'indicator'):
                    b.indicator.destroy()
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        self.create_status_panel()
    
    def animate_sidebar_logo(self):
        """Anima o logo da sidebar"""
        if hasattr(self, 'sidebar_logo') and self.sidebar_logo.winfo_exists():
            colors = [AdvancedConfig.COLORS['neon_blue'], AdvancedConfig.COLORS['primary'], 
                     AdvancedConfig.COLORS['neon_green']]
            current_color = self.sidebar_logo.cget('fg')
            next_index = (colors.index(current_color) + 1) % len(colors) if current_color in colors else 0
            self.sidebar_logo.config(fg=colors[next_index])
            self.root.after(2000, self.animate_sidebar_logo)
    
    def create_status_panel(self):
        status_frame = tk.Frame(self.sidebar, bg=AdvancedConfig.COLORS['card'], padx=20, pady=20, relief=tk.FLAT, bd=0)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        tk.Label(status_frame, text="📊 System Status", font=("Segoe UI", 12, "bold"), 
                fg=AdvancedConfig.COLORS['neon_blue'], bg=status_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        # CPU com barra de progresso visual
        cpu_frame = tk.Frame(status_frame, bg=status_frame['bg'])
        cpu_frame.pack(fill=tk.X, pady=5)
        
        self.cpu_label = tk.Label(cpu_frame, text="CPU: 0%", font=("Segoe UI", 10, "bold"), 
                                 fg=AdvancedConfig.COLORS['text'], bg=cpu_frame['bg'])
        self.cpu_label.pack(side=tk.LEFT)
        
        self.cpu_bar = tk.Canvas(cpu_frame, height=6, bg=AdvancedConfig.COLORS['darker'], highlightthickness=0)
        self.cpu_bar.pack(fill=tk.X, pady=(5, 0))
        self.cpu_bar_rect = self.cpu_bar.create_rectangle(0, 0, 0, 6, fill=AdvancedConfig.COLORS['danger'], outline='')
        
        # RAM com barra de progresso visual
        ram_frame = tk.Frame(status_frame, bg=status_frame['bg'])
        ram_frame.pack(fill=tk.X, pady=5)
        
        self.ram_label = tk.Label(ram_frame, text="RAM: 0%", font=("Segoe UI", 10, "bold"), 
                                 fg=AdvancedConfig.COLORS['text'], bg=ram_frame['bg'])
        self.ram_label.pack(side=tk.LEFT)
        
        self.ram_bar = tk.Canvas(ram_frame, height=6, bg=AdvancedConfig.COLORS['darker'], highlightthickness=0)
        self.ram_bar.pack(fill=tk.X, pady=(5, 0))
        self.ram_bar_rect = self.ram_bar.create_rectangle(0, 0, 0, 6, fill=AdvancedConfig.COLORS['warning'], outline='')
        
        # Status indicator
        status_indicator = tk.Frame(status_frame, bg=AdvancedConfig.COLORS['neon_green'], height=3)
        status_indicator.pack(fill=tk.X, pady=(10, 0))
    
    def create_content_area(self, parent):
        self.content_frame = tk.Frame(parent, bg=AdvancedConfig.COLORS['dark'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        self.dynamic_content = tk.Frame(self.content_frame, bg=AdvancedConfig.COLORS['dark'])
        self.dynamic_content.pack(fill=tk.BOTH, expand=True)
    
    def create_floating_action_buttons(self):
        # Botão de limpeza
        self.fab_cleanup = tk.Button(self.root, text="🧹\nCleanup", font=("Segoe UI", 12, "bold"), 
                                    bg=AdvancedConfig.COLORS['primary'], fg=AdvancedConfig.COLORS['dark'], 
                                    bd=0, cursor='hand2', command=self.fab_cleanup_action,
                                    relief=tk.FLAT, padx=5, pady=5)
        self.fab_cleanup.place(relx=0.98, rely=0.95, anchor="se", width=80, height=80)
        
        # Botão gaming
        self.fab_gaming = tk.Button(self.root, text="🎮\nGaming", font=("Segoe UI", 12, "bold"), 
                                   bg=AdvancedConfig.COLORS['danger'], fg=AdvancedConfig.COLORS['dark'], 
                                   bd=0, cursor='hand2', command=self.fab_gaming_action,
                                   relief=tk.FLAT, padx=5, pady=5)
        self.fab_gaming.place(relx=0.98, rely=0.83, anchor="se", width=80, height=80)
        
        # Botão performance
        self.fab_performance = tk.Button(self.root, text="⚡\nTurbo", font=("Segoe UI", 12, "bold"), 
                                        bg=AdvancedConfig.COLORS['success'], fg=AdvancedConfig.COLORS['dark'], 
                                        bd=0, cursor='hand2', command=self.fab_performance_action,
                                        relief=tk.FLAT, padx=5, pady=5)
        self.fab_performance.place(relx=0.98, rely=0.71, anchor="se", width=80, height=80)
    
    def fab_gaming_action(self):
        """Ação do botão gaming"""
        self.fab_gaming.config(text="⏳", state="disabled")
        threading.Thread(target=self.run_gaming_boost, daemon=True).start()
    
    def fab_performance_action(self):
        """Ação do botão performance"""
        self.fab_performance.config(text="⏳", state="disabled")
        threading.Thread(target=self.run_performance_boost, daemon=True).start()
    
    def run_gaming_boost(self):
        """Executa boost de gaming"""
        self.tweaks_engine.apply_compatible_tweaks('gaming')
        self.tweaks_engine.apply_compatible_tweaks('network')
        self.root.after(0, lambda: self.fab_gaming.config(text="🎮\nGaming", state="normal"))
        self.root.after(0, lambda: messagebox.showinfo("✅ Gaming Boost", "Modo Gaming ativado com sucesso!"))
    
    def run_performance_boost(self):
        """Executa boost de performance"""
        self.tweaks_engine.apply_compatible_tweaks('cpu')
        self.tweaks_engine.apply_compatible_tweaks('memory')
        self.tweaks_engine.apply_compatible_tweaks('system')
        self.root.after(0, lambda: self.fab_performance.config(text="⚡\nTurbo", state="normal"))
        self.root.after(0, lambda: messagebox.showinfo("✅ Performance Boost", "Sistema otimizado com sucesso!"))
    
    def fab_cleanup_action(self):
        self.fab_cleanup.config(text="⏳", state="disabled")
        threading.Thread(target=self.run_cleanup_pro, daemon=True).start()
    
    def run_cleanup_pro(self):
        # Limpar RAM
        try:
            import ctypes
            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
        except:
            pass
        
        # Limpeza de arquivos
        results = self.system_manager.cleanup_pro("comprehensive")
        
        # Liberar memória
        freed_mb = 0
        try:
            import gc
            gc.collect()
            freed_mb = psutil.virtual_memory().available / (1024**2)
        except:
            pass
        
        self.root.after(0, lambda: self.fab_cleanup.config(text="🧹\nCleanup", state="normal"))
        self.root.after(0, lambda: messagebox.showinfo("✅ Limpeza Concluída", 
                                                       f"Arquivos removidos: {results['cleaned']}\nRAM disponível: {freed_mb:.0f}MB"))
    
    def clear_content(self):
        for widget in self.dynamic_content.winfo_children():
            widget.destroy()
        # Esconder FABs em todas as telas exceto dashboard
        self.hide_fabs()
    
    def show_fabs(self):
        """Mostra botões flutuantes"""
        if hasattr(self, 'fab_cleanup'):
            self.fab_cleanup.place(relx=0.98, rely=0.95, anchor="se", width=80, height=80)
            self.fab_gaming.place(relx=0.98, rely=0.83, anchor="se", width=80, height=80)
            self.fab_performance.place(relx=0.98, rely=0.71, anchor="se", width=80, height=80)
    
    def hide_fabs(self):
        """Esconde botões flutuantes"""
        if hasattr(self, 'fab_cleanup'):
            self.fab_cleanup.place_forget()
            self.fab_gaming.place_forget()
            self.fab_performance.place_forget()
    
    def show_dashboard(self):
        self.clear_content()
        self.show_fabs()  # Mostrar FABs apenas no dashboard
        
        # Header
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="🎯 Início", font=("Segoe UI", 32, "bold"), 
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Hardware Info Card
        hw_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        hw_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(hw_frame, text="💻 Hardware Detectado", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=hw_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        sys_info = self.utils.get_system_info()
        hw_data = [
            ("CPU:", f"{sys_info['cpu_brand']} - {sys_info['cpu_cores']} cores", sys_info['cpu_color']),
            ("RAM:", f"{sys_info['ram_total']}GB Total", AdvancedConfig.COLORS['info']),
            ("Disco:", f"{sys_info['disk_free']:.1f}GB Livre de {sys_info['disk_total']:.1f}GB", AdvancedConfig.COLORS['warning'])
        ]
        
        for label, value, color in hw_data:
            row = tk.Frame(hw_frame, bg=hw_frame['bg'])
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                    bg=row['bg'], width=15, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 10, "bold"), fg=color, bg=row['bg']).pack(side=tk.LEFT)
        
        # Métricas em tempo real SEM TEMPERATURA
        metrics_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        metrics_frame.pack(fill=tk.X, pady=(0, 15))
        
        metrics = [
            ("CPU", "cpu", "%", AdvancedConfig.COLORS['danger']),
            ("RAM", "ram", "%", AdvancedConfig.COLORS['warning']),
            ("Disco", "disk", "%", AdvancedConfig.COLORS['info'])
        ]
        
        self.dashboard_metrics = {}
        for i, (name, key, unit, color) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i == 0 else 10))
            
            tk.Label(card, text=name, font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                    bg=card['bg']).pack(anchor=tk.W)
            
            value_label = tk.Label(card, text=f"0{unit}", font=("Segoe UI", 24, "bold"), fg=color, bg=card['bg'])
            value_label.pack(anchor=tk.W)
            self.dashboard_metrics[key] = (value_label, unit)
            
            tk.Frame(card, height=4, bg=color).pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # Ações rápidas
        actions_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        actions = [
            ("🧹 Limpeza Rápida", self.fab_cleanup_action, AdvancedConfig.COLORS['primary']),
            ("⚡ Boost Performance", self.fab_performance_action, AdvancedConfig.COLORS['success']),
            ("🎮 Modo Gaming", self.fab_gaming_action, AdvancedConfig.COLORS['danger']),
            ("🔧 Ver Tweaks", self.show_smart_tweaks, AdvancedConfig.COLORS['warning'])
        ]
        
        for text, command, color in actions:
            btn = tk.Button(actions_frame, text=text, font=("Segoe UI", 11, "bold"),
                           fg=AdvancedConfig.COLORS['dark'], bg=color, bd=0, padx=20, pady=10,
                           cursor='hand2', command=command)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Logs recentes
        logs_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(logs_frame, text="📝 Logs Recentes", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=logs_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, bg=AdvancedConfig.COLORS['darker'],
                                                   fg=AdvancedConfig.COLORS['text'], font=("Consolas", 9),
                                                   height=8, padx=10, pady=10)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        for log in self.logger.get_recent_logs(10):
            self.logs_text.insert(tk.END, log + "\n")
        self.logs_text.config(state='disabled')
        
        # Atualizar métricas do dashboard
        self.update_dashboard_metrics()
    
    def show_hardware_info(self):
        self.clear_content()
        
        # Header
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="🔍 Hardware Information", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        sys_info = self.utils.get_system_info()
        
        # CPU Section
        cpu_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        cpu_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(cpu_frame, text="🧠 Processador (CPU)", font=("Segoe UI", 16, "bold"),
                fg=sys_info['cpu_color'], bg=cpu_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        cpu_data = [
            ("Nome:", sys_info['cpu_name']),
            ("Marca:", sys_info['cpu_brand']),
            ("Núcleos Físicos:", str(sys_info['cpu_cores'])),
            ("Threads:", str(sys_info['cpu_threads']))
        ]
        
        for label, value in cpu_data:
            row = tk.Frame(cpu_frame, bg=cpu_frame['bg'])
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                    bg=row['bg'], width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 10, "bold"), fg=AdvancedConfig.COLORS['text'],
                    bg=row['bg']).pack(side=tk.LEFT)
        
        # Memory Section
        mem_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        mem_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(mem_frame, text="💾 Memória (RAM)", font=("Segoe UI", 16, "bold"),
                fg=AdvancedConfig.COLORS['info'], bg=mem_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        mem_data = [
            ("Total:", f"{sys_info['ram_total']}GB"),
            ("Disponível:", f"{sys_info['ram_available']}GB"),
            ("Uso:", f"{sys_info['ram_total'] - sys_info['ram_available']:.1f}GB")
        ]
        
        for label, value in mem_data:
            row = tk.Frame(mem_frame, bg=mem_frame['bg'])
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                    bg=row['bg'], width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 10, "bold"), fg=AdvancedConfig.COLORS['text'],
                    bg=row['bg']).pack(side=tk.LEFT)
        
        # Disk Section
        disk_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        disk_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(disk_frame, text="💿 Armazenamento", font=("Segoe UI", 16, "bold"),
                fg=AdvancedConfig.COLORS['warning'], bg=disk_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        disk_data = [
            ("Total:", f"{sys_info['disk_total']:.1f}GB"),
            ("Livre:", f"{sys_info['disk_free']:.1f}GB"),
            ("Usado:", f"{sys_info['disk_total'] - sys_info['disk_free']:.1f}GB")
        ]
        
        for label, value in disk_data:
            row = tk.Frame(disk_frame, bg=disk_frame['bg'])
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                    bg=row['bg'], width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 10, "bold"), fg=AdvancedConfig.COLORS['text'],
                    bg=row['bg']).pack(side=tk.LEFT)
        
        # System Section
        sys_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        sys_frame.pack(fill=tk.X)
        
        tk.Label(sys_frame, text="⚙️ Sistema Operacional", font=("Segoe UI", 16, "bold"),
                fg=AdvancedConfig.COLORS['primary'], bg=sys_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(sys_frame, text=f"OS: {sys_info['os']}", font=("Segoe UI", 10),
                fg=AdvancedConfig.COLORS['text'], bg=sys_frame['bg']).pack(anchor=tk.W, pady=3)
    
    def show_smart_tweaks(self):
        self.clear_content()
        
        # Header
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="⚡ Smart Tweaks", font=("Segoe UI", 32, "bold"), 
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Botão aplicar todos
        tk.Button(header, text="🚀 APLICAR TODOS", font=("Segoe UI", 12, "bold"), 
                 fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['gold'], 
                 bd=0, padx=20, pady=8, cursor='hand2',
                 command=self.apply_all_tweaks).pack(side=tk.RIGHT)
        
        # Notebook com abas
        notebook = ttk.Notebook(self.dynamic_content)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Abas por categoria
        categories = [
            ('CPU', 'cpu', AdvancedConfig.COLORS['danger']),
            ('GPU', 'gpu', AdvancedConfig.COLORS['success']),
            ('NVIDIA', 'nvidia', AdvancedConfig.COLORS['nvidia_green']),
            ('AMD', 'amd', AdvancedConfig.COLORS['amd_red']),
            ('Memory', 'memory', AdvancedConfig.COLORS['warning']),
            ('Network', 'network', AdvancedConfig.COLORS['purple']),
            ('Gaming', 'gaming', AdvancedConfig.COLORS['orange']),
            ('System', 'system', AdvancedConfig.COLORS['cyan']),
            ('Debloat', 'debloat', AdvancedConfig.COLORS['danger']),
            ('Kernel', 'kernel', AdvancedConfig.COLORS['neon_pink'])
        ]
        
        for cat_name, cat_key, color in categories:
            tab_frame = tk.Frame(notebook, bg=AdvancedConfig.COLORS['dark'])
            notebook.add(tab_frame, text=f"  {cat_name}  ")
            
            # Scrollable frame
            canvas = tk.Canvas(tab_frame, bg=AdvancedConfig.COLORS['dark'], highlightthickness=0)
            scrollbar = tk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=AdvancedConfig.COLORS['dark'])
            
            scrollable_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Header da aba
            tab_header = tk.Frame(scrollable_frame, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
            tab_header.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(tab_header, text=f"{cat_name} Tweaks", font=("Segoe UI", 16, "bold"),
                    fg=color, bg=tab_header['bg']).pack(side=tk.LEFT)
            
            tweaks = self.tweaks_engine.get_compatible_tweaks(cat_key)
            tk.Label(tab_header, text=f"{len(tweaks)} disponíveis", font=("Segoe UI", 10),
                    fg=AdvancedConfig.COLORS['text_secondary'], bg=tab_header['bg']).pack(side=tk.LEFT, padx=10)
            
            tk.Button(tab_header, text=f"Aplicar Todos", font=("Segoe UI", 9, "bold"),
                     fg=AdvancedConfig.COLORS['dark'], bg=color, bd=0, padx=15, pady=5,
                     cursor='hand2', command=lambda c=cat_key: self.apply_category_tweaks(c)).pack(side=tk.RIGHT)
            
            # Lista de tweaks
            for tweak in tweaks:
                tweak_frame = tk.Frame(scrollable_frame, bg=AdvancedConfig.COLORS['card'], padx=20, pady=12)
                tweak_frame.pack(fill=tk.X, pady=2)
                
                tk.Label(tweak_frame, text=f"• {tweak['name']}", font=("Segoe UI", 10, "bold"),
                        fg=AdvancedConfig.COLORS['text'], bg=tweak_frame['bg']).pack(anchor=tk.W)
    
    def apply_all_tweaks(self):
        """Aplica todos os tweaks com seleção de GPU"""
        if messagebox.askyesno("Confirmar", "Aplicar TODOS os tweaks?\n\nIsso pode levar alguns minutos."):
            # Perguntar tipo de GPU
            gpu_type = self.ask_gpu_type()
            if gpu_type:
                self.show_progress_window()
                threading.Thread(target=lambda: self._apply_all_tweaks_thread(gpu_type), daemon=True).start()
    
    def ask_gpu_type(self):
        """Janela para selecionar tipo de GPU"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Selecione sua GPU")
        dialog.geometry("500x350")
        dialog.configure(bg=AdvancedConfig.COLORS['dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"500x350+{x}+{y}")
        
        result = {'gpu': None}
        
        # Header
        tk.Label(dialog, text="🎮 Selecione sua GPU", font=("Segoe UI", 20, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=dialog['bg']).pack(pady=(30, 10))
        
        tk.Label(dialog, text="Escolha o fabricante da sua placa de vídeo", font=("Segoe UI", 10),
                fg=AdvancedConfig.COLORS['text_secondary'], bg=dialog['bg']).pack(pady=(0, 30))
        
        # Botões de GPU
        def select_gpu(gpu_type):
            result['gpu'] = gpu_type
            dialog.destroy()
        
        # NVIDIA
        nvidia_btn = tk.Button(dialog, text="🟢 NVIDIA GeForce", font=("Segoe UI", 14, "bold"),
                              fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['nvidia_green'],
                              bd=0, padx=40, pady=20, cursor='hand2',
                              command=lambda: select_gpu('nvidia'))
        nvidia_btn.pack(fill=tk.X, padx=50, pady=10)
        
        # AMD
        amd_btn = tk.Button(dialog, text="🔴 AMD Radeon", font=("Segoe UI", 14, "bold"),
                           fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['amd_red'],
                           bd=0, padx=40, pady=20, cursor='hand2',
                           command=lambda: select_gpu('amd'))
        amd_btn.pack(fill=tk.X, padx=50, pady=10)
        
        # Intel/Outro
        other_btn = tk.Button(dialog, text="🔵 Intel / Outro", font=("Segoe UI", 14, "bold"),
                             fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['intel_blue'],
                             bd=0, padx=40, pady=20, cursor='hand2',
                             command=lambda: select_gpu('other'))
        other_btn.pack(fill=tk.X, padx=50, pady=10)
        
        dialog.wait_window()
        return result['gpu']
    
    def show_progress_window(self):
        """Mostra janela de progresso com animação"""
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Aplicando Tweaks")
        self.progress_window.geometry("600x300")
        self.progress_window.configure(bg=AdvancedConfig.COLORS['dark'])
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        # Centralizar
        self.progress_window.update_idletasks()
        x = (self.progress_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.progress_window.winfo_screenheight() // 2) - (300 // 2)
        self.progress_window.geometry(f"600x300+{x}+{y}")
        
        # Ícone animado
        self.progress_icon = tk.Label(self.progress_window, text="⚡", font=("Segoe UI", 48, "bold"),
                                      fg=AdvancedConfig.COLORS['neon_blue'], bg=self.progress_window['bg'])
        self.progress_icon.pack(pady=(30, 20))
        
        # Título
        tk.Label(self.progress_window, text="Aplicando Tweaks...", font=("Segoe UI", 16, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=self.progress_window['bg']).pack(pady=(0, 10))
        
        # Status
        self.progress_status = tk.Label(self.progress_window, text="Iniciando...", font=("Segoe UI", 10),
                                       fg=AdvancedConfig.COLORS['text_secondary'], bg=self.progress_window['bg'])
        self.progress_status.pack(pady=(0, 20))
        
        # Barra de progresso
        progress_frame = tk.Frame(self.progress_window, bg=AdvancedConfig.COLORS['darker'], height=30)
        progress_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        progress_frame.pack_propagate(False)
        
        self.progress_bar_fill = tk.Frame(progress_frame, bg=AdvancedConfig.COLORS['neon_blue'], height=30)
        self.progress_bar_fill.place(x=0, y=0, relheight=1, relwidth=0)
        
        # Percentual
        self.progress_percent = tk.Label(self.progress_window, text="0%", font=("Segoe UI", 12, "bold"),
                                        fg=AdvancedConfig.COLORS['neon_blue'], bg=self.progress_window['bg'])
        self.progress_percent.pack()
        
        # Animação do ícone
        self.animate_progress_icon()
    
    def animate_progress_icon(self):
        """Anima o ícone de progresso"""
        if hasattr(self, 'progress_icon') and self.progress_icon.winfo_exists():
            colors = [AdvancedConfig.COLORS['neon_blue'], AdvancedConfig.COLORS['neon_pink'], 
                     AdvancedConfig.COLORS['neon_green'], AdvancedConfig.COLORS['primary']]
            current_color = self.progress_icon.cget('fg')
            next_index = (colors.index(current_color) + 1) % len(colors) if current_color in colors else 0
            self.progress_icon.config(fg=colors[next_index])
            self.root.after(300, self.animate_progress_icon)
    
    def update_progress(self, percent, status):
        """Atualiza barra de progresso"""
        if hasattr(self, 'progress_bar_fill') and self.progress_bar_fill.winfo_exists():
            self.progress_bar_fill.place(relwidth=percent/100)
            self.progress_percent.config(text=f"{percent}%")
            self.progress_status.config(text=status)
    
    def close_progress_window(self):
        """Fecha janela de progresso"""
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()
    
    def _apply_all_tweaks_thread(self, gpu_type):
        """Thread para aplicar todos os tweaks com progresso"""
        categories = ['cpu', 'memory', 'network', 'gaming', 'system']
        
        # Adicionar categoria de GPU específica
        if gpu_type == 'nvidia':
            categories.insert(1, 'nvidia')
        elif gpu_type == 'amd':
            categories.insert(1, 'amd')
        else:
            categories.insert(1, 'gpu')
        
        total_categories = len(categories)
        applied_total = 0
        errors_total = []
        
        for i, category in enumerate(categories):
            percent = int((i / total_categories) * 100)
            self.root.after(0, lambda p=percent, c=category: self.update_progress(p, f"Aplicando {c.upper()}..."))
            
            applied, errors = self.tweaks_engine.apply_compatible_tweaks(category)
            applied_total += applied
            errors_total.extend(errors)
            
            time.sleep(0.5)
        
        self.root.after(0, lambda: self.update_progress(100, "Concluído!"))
        time.sleep(1)
        self.root.after(0, self.close_progress_window)
        self.root.after(0, lambda: messagebox.showinfo("✅ Concluído", 
                                                       f"Tweaks aplicados: {applied_total}\nErros: {len(errors_total)}\nGPU: {gpu_type.upper()}"))
    
    def apply_category_tweaks(self, category):
        """Aplica tweaks de uma categoria com seleção de GPU se necessário"""
        if category.lower() == 'gpu':
            gpu_type = self.ask_gpu_type()
            if not gpu_type:
                return
            if gpu_type == 'nvidia':
                category = 'nvidia'
            elif gpu_type == 'amd':
                category = 'amd'
        
        self.show_progress_window()
        threading.Thread(target=lambda: self._apply_category_thread(category), daemon=True).start()
    
    def _apply_category_thread(self, category):
        """Thread para aplicar tweaks de categoria com progresso"""
        self.root.after(0, lambda: self.update_progress(30, f"Aplicando {category.upper()}..."))
        applied, errors = self.tweaks_engine.apply_compatible_tweaks(category)
        self.root.after(0, lambda: self.update_progress(100, "Concluído!"))
        time.sleep(1)
        self.root.after(0, self.close_progress_window)
        self.root.after(0, lambda: messagebox.showinfo("✅ Concluído", 
                                                       f"Tweaks aplicados: {applied}\nCategoria: {category.upper()}"))
    
    def show_gaming_mode(self):
        self.clear_content()
        
        # Header
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="🎮 Gaming Mode", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Status Card
        status_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(status_frame, text="🟢 Status do Modo Gaming", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['success'], bg=status_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(status_frame, text="Otimizações de gaming prontas para serem aplicadas",
                font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                bg=status_frame['bg']).pack(anchor=tk.W)
        
        # Otimizações disponíveis
        optimizations = [
            ("🎯 Game Mode", "Ativa modo de jogo do Windows", AdvancedConfig.COLORS['success']),
            ("📺 Game Bar", "Desativa overlay do Game Bar", AdvancedConfig.COLORS['danger']),
            ("⚡ Prioridades", "Ajusta prioridades para jogos", AdvancedConfig.COLORS['warning']),
            ("🎮 GPU Priority", "Maximiza prioridade da GPU", AdvancedConfig.COLORS['info']),
            ("🌐 Network", "Reduz latência de rede", AdvancedConfig.COLORS['purple']),
            ("📡 TCP/IP", "Otimiza conexão TCP/IP", AdvancedConfig.COLORS['cyan'])
        ]
        
        for icon_text, desc, color in optimizations:
            opt_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
            opt_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(opt_frame, text=icon_text, font=("Segoe UI", 12, "bold"),
                    fg=color, bg=opt_frame['bg']).pack(side=tk.LEFT, padx=(0, 15))
            
            tk.Label(opt_frame, text=desc, font=("Segoe UI", 10),
                    fg=AdvancedConfig.COLORS['text_secondary'], bg=opt_frame['bg']).pack(side=tk.LEFT)
        
        # Botão de ativação
        btn_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        btn_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(btn_frame, text="🚀 ATIVAR MODO GAMING", font=("Segoe UI", 14, "bold"),
                 fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['danger'],
                 bd=0, padx=30, pady=15, cursor='hand2',
                 command=self.fab_gaming_action).pack()
        
        # Aviso
        warning_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['warning'], padx=20, pady=15)
        warning_frame.pack(fill=tk.X)
        
        tk.Label(warning_frame, text="⚠️ Aviso", font=("Segoe UI", 12, "bold"),
                fg=AdvancedConfig.COLORS['dark'], bg=warning_frame['bg']).pack(anchor=tk.W)
        tk.Label(warning_frame, text="Modo Gaming aplica tweaks de rede e prioridades. Recomendado para jogos online.",
                font=("Segoe UI", 9), fg=AdvancedConfig.COLORS['dark'],
                bg=warning_frame['bg']).pack(anchor=tk.W)
    
    def show_cleanup_pro(self):
        self.clear_content()
        
        # Header
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="🧹 Cleanup Pro", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Áreas de limpeza
        cleanup_areas = [
            ("📁 Arquivos Temporários", "Limpa arquivos temporários do sistema", AdvancedConfig.COLORS['primary']),
            ("🗑️ Lixeira", "Esvazia a lixeira do Windows", AdvancedConfig.COLORS['danger']),
            ("🌐 Cache DNS", "Limpa cache de DNS", AdvancedConfig.COLORS['info']),
            ("💾 Prefetch", "Remove arquivos de prefetch", AdvancedConfig.COLORS['warning']),
            ("📦 Windows Update", "Limpa cache de atualizações", AdvancedConfig.COLORS['success']),
            ("🌐 Navegadores", "Limpa cache dos navegadores", AdvancedConfig.COLORS['purple'])
        ]
        
        for icon_text, desc, color in cleanup_areas:
            area_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
            area_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(area_frame, text=icon_text, font=("Segoe UI", 12, "bold"),
                    fg=color, bg=area_frame['bg']).pack(side=tk.LEFT, padx=(0, 15))
            
            tk.Label(area_frame, text=desc, font=("Segoe UI", 10),
                    fg=AdvancedConfig.COLORS['text_secondary'], bg=area_frame['bg']).pack(side=tk.LEFT)
        
        # Modos de limpeza
        modes_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        modes_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(modes_frame, text="Selecione o modo de limpeza:", font=("Segoe UI", 12, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=modes_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        modes = [
            ("🟢 Rápida", "normal", AdvancedConfig.COLORS['success']),
            ("🟡 Completa", "comprehensive", AdvancedConfig.COLORS['warning']),
            ("🔴 Profunda", "deep", AdvancedConfig.COLORS['danger'])
        ]
        
        for text, mode, color in modes:
            btn = tk.Button(modes_frame, text=text, font=("Segoe UI", 11, "bold"),
                           fg=AdvancedConfig.COLORS['dark'], bg=color, bd=0, padx=25, pady=10,
                           cursor='hand2', command=lambda m=mode: self.run_cleanup_mode(m))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Compactação do Windows
        compact_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        compact_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(compact_frame, text="🗜️ Compactação do Windows", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=compact_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(compact_frame, text="Compacta o sistema operacional para liberar espaço em disco (pode levar vários minutos)",
                font=("Segoe UI", 9), fg=AdvancedConfig.COLORS['text_secondary'],
                bg=compact_frame['bg']).pack(anchor=tk.W, pady=(0, 15))
        
        tk.Button(compact_frame, text="🚀 COMPACTAR WINDOWS", font=("Segoe UI", 12, "bold"),
                 fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['purple'],
                 bd=0, padx=30, pady=12, cursor='hand2',
                 command=self.compact_windows).pack()
        
        # Estatísticas
        stats_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(stats_frame, text="📊 Estatísticas", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=stats_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        sys_info = self.utils.get_system_info()
        tk.Label(stats_frame, text=f"Espaço livre: {sys_info['disk_free']:.1f}GB de {sys_info['disk_total']:.1f}GB",
                font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['text_secondary'],
                bg=stats_frame['bg']).pack(anchor=tk.W)
    
    def compact_windows(self):
        """Compacta o Windows com barra de progresso"""
        if not messagebox.askyesno("⚠️ Confirmar Compactação", 
                                   "A compactação do Windows pode levar vários minutos.\n\nDeseja continuar?"):
            return
        
        # Criar janela de progresso
        self.compact_window = tk.Toplevel(self.root)
        self.compact_window.title("Compactando Windows")
        self.compact_window.geometry("600x250")
        self.compact_window.configure(bg=AdvancedConfig.COLORS['dark'])
        self.compact_window.transient(self.root)
        self.compact_window.grab_set()
        
        # Centralizar
        self.compact_window.update_idletasks()
        x = (self.compact_window.winfo_screenwidth() // 2) - (300)
        y = (self.compact_window.winfo_screenheight() // 2) - (125)
        self.compact_window.geometry(f"600x250+{x}+{y}")
        
        # Ícone
        tk.Label(self.compact_window, text="🗜️", font=("Segoe UI", 48, "bold"),
                fg=AdvancedConfig.COLORS['purple'], bg=self.compact_window['bg']).pack(pady=(30, 20))
        
        # Status
        self.compact_status = tk.Label(self.compact_window, text="Compactando sistema...", font=("Segoe UI", 12, "bold"),
                                      fg=AdvancedConfig.COLORS['text'], bg=self.compact_window['bg'])
        self.compact_status.pack(pady=(0, 20))
        
        # Barra de progresso
        progress_frame = tk.Frame(self.compact_window, bg=AdvancedConfig.COLORS['darker'], height=30)
        progress_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        progress_frame.pack_propagate(False)
        
        self.compact_bar = tk.Frame(progress_frame, bg=AdvancedConfig.COLORS['purple'], height=30)
        self.compact_bar.place(x=0, y=0, relheight=1, relwidth=0)
        
        # Iniciar compactação
        threading.Thread(target=self._compact_windows_thread, daemon=True).start()
    
    def _compact_windows_thread(self):
        """Thread de compactação do Windows"""
        try:
            # Atualizar progresso
            self.root.after(0, lambda: self._update_compact_progress(20, "Analisando sistema..."))
            time.sleep(1)
            
            self.root.after(0, lambda: self._update_compact_progress(40, "Compactando arquivos do sistema..."))
            # Compact OS
            subprocess.run("compact /compactos:always", shell=True, capture_output=True, timeout=300)
            
            self.root.after(0, lambda: self._update_compact_progress(70, "Compactando arquivos de usuário..."))
            time.sleep(1)
            
            self.root.after(0, lambda: self._update_compact_progress(90, "Finalizando..."))
            # Limpar WinSxS
            subprocess.run("Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase", 
                          shell=True, capture_output=True, timeout=300)
            
            self.root.after(0, lambda: self._update_compact_progress(100, "Concluído!"))
            time.sleep(1)
            
            self.root.after(0, self._close_compact_window)
            self.root.after(0, lambda: messagebox.showinfo("✅ Compactação Concluída", 
                                                          "Windows compactado com sucesso!\nReinicie o sistema para melhores resultados."))
        except subprocess.TimeoutExpired:
            self.root.after(0, self._close_compact_window)
            self.root.after(0, lambda: messagebox.showerror("❌ Erro", "Tempo limite excedido. Tente novamente."))
        except Exception as e:
            self.root.after(0, self._close_compact_window)
            self.root.after(0, lambda: messagebox.showerror("❌ Erro", f"Erro na compactação: {e}"))
    
    def _update_compact_progress(self, percent, status):
        """Atualiza progresso da compactação"""
        if hasattr(self, 'compact_bar') and self.compact_bar.winfo_exists():
            self.compact_bar.place(relwidth=percent/100)
            self.compact_status.config(text=status)
    
    def _close_compact_window(self):
        """Fecha janela de compactação"""
        if hasattr(self, 'compact_window') and self.compact_window.winfo_exists():
            self.compact_window.destroy()
    
    def run_cleanup_mode(self, mode):
        """Executa limpeza no modo especificado"""
        if messagebox.askyesno("Confirmar", f"Iniciar limpeza no modo {mode}?"):
            threading.Thread(target=lambda: self._cleanup_thread(mode), daemon=True).start()
    
    def _cleanup_thread(self, mode):
        """Thread de limpeza"""
        results = self.system_manager.cleanup_pro(mode)
        self.root.after(0, lambda: messagebox.showinfo("✅ Limpeza Concluída",
                                                       f"Itens removidos: {results['cleaned']}\nErros: {len(results['errors'])}"))
    
    def show_settings(self):
        self.clear_content()
        
        # Header
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="⚙️ Configurações", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Configurações gerais
        general_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        general_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(general_frame, text="🔧 Configurações Gerais", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=general_frame['bg']).pack(anchor=tk.W, pady=(0, 15))
        
        settings = [
            ("Iniciar com Windows", "auto_start"),
            ("Minimizar para bandeja", "minimize_tray"),
            ("Verificação automática de atualizações", "auto_update"),
            ("Criar backup antes de aplicar tweaks", "auto_backup"),
            ("Mostrar notificações", "show_notifications")
        ]
        
        for text, key in settings:
            row = tk.Frame(general_frame, bg=general_frame['bg'])
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=text, font=("Segoe UI", 10),
                    fg=AdvancedConfig.COLORS['text'], bg=row['bg']).pack(side=tk.LEFT)
            
            var = tk.BooleanVar(value=self.config.get(key, False))
            tk.Checkbutton(row, variable=var, bg=row['bg'], fg=AdvancedConfig.COLORS['text'],
                          selectcolor=AdvancedConfig.COLORS['success'],
                          command=lambda k=key, v=var: self.save_setting(k, v.get())).pack(side=tk.RIGHT)
        
        # Tema
        theme_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(theme_frame, text="🎨 Tema", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=theme_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(theme_frame, text="Tema Escuro (Padrão)", font=("Segoe UI", 10),
                fg=AdvancedConfig.COLORS['text_secondary'], bg=theme_frame['bg']).pack(anchor=tk.W)
        
        # Ações
        actions_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        actions_frame.pack(fill=tk.X, pady=20)
        
        actions = [
            ("💾 Criar Backup", self.create_backup, AdvancedConfig.COLORS['info']),
            ("🔄 Restaurar Backup", self.restore_backup, AdvancedConfig.COLORS['warning']),
            ("🗑️ Limpar Configurações", self.clear_settings, AdvancedConfig.COLORS['danger'])
        ]
        
        for text, command, color in actions:
            btn = tk.Button(actions_frame, text=text, font=("Segoe UI", 10, "bold"),
                           fg=AdvancedConfig.COLORS['dark'], bg=color, bd=0, padx=20, pady=8,
                           cursor='hand2', command=command)
            btn.pack(side=tk.LEFT, padx=5)
    
    def save_setting(self, key, value):
        """Salva configuração"""
        self.config[key] = value
        try:
            with open(AdvancedConfig.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except:
            pass
    
    def create_backup(self):
        messagebox.showinfo("Backup", "Funcionalidade de backup em desenvolvimento")
    
    def restore_backup(self):
        messagebox.showinfo("Restaurar", "Funcionalidade de restauração em desenvolvimento")
    
    def clear_settings(self):
        if messagebox.askyesno("Confirmar", "Limpar todas as configurações?"):
            self.config = {}
            try:
                if os.path.exists(AdvancedConfig.CONFIG_FILE):
                    os.remove(AdvancedConfig.CONFIG_FILE)
                messagebox.showinfo("✅ Sucesso", "Configurações limpas!")
            except:
                messagebox.showerror("❌ Erro", "Não foi possível limpar as configurações")
    
    def show_about(self):
        self.clear_content()
        
        # Header com logo
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['primary'], height=150)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⚡", font=("Segoe UI", 64, "bold"),
                fg=AdvancedConfig.COLORS['dark'], bg=header['bg']).pack(pady=20)
        
        # Info principal
        info_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=40, pady=30)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(info_frame, text="KELVEN OPTIMIZER PRO", font=("Segoe UI", 24, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=info_frame['bg']).pack(pady=(0, 5))
        
        tk.Label(info_frame, text=f"Versão {AdvancedConfig.VERSION}", font=("Segoe UI", 12),
                fg=AdvancedConfig.COLORS['text_secondary'], bg=info_frame['bg']).pack(pady=(0, 20))
        
        tk.Label(info_frame, text="Sistema Inteligente de Otimização", font=("Segoe UI", 11),
                fg=AdvancedConfig.COLORS['text'], bg=info_frame['bg']).pack(pady=5)
        
        tk.Label(info_frame, text="Detecção automática de hardware e aplicação de tweaks", font=("Segoe UI", 10),
                fg=AdvancedConfig.COLORS['text_secondary'], bg=info_frame['bg']).pack(pady=(0, 20))
        
        # Recursos
        features_frame = tk.Frame(info_frame, bg=info_frame['bg'])
        features_frame.pack(pady=20)
        
        features = [
            "✅ 150+ Tweaks Inteligentes",
            "✅ Detecção Automática de Hardware",
            "✅ Modo Gaming Otimizado",
            "✅ Limpeza Profissional",
            "✅ Monitor de Performance",
            "✅ Interface Moderna"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, font=("Segoe UI", 10),
                    fg=AdvancedConfig.COLORS['text'], bg=features_frame['bg']).pack(anchor=tk.W, pady=2)
        
        # Autor
        author_frame = tk.Frame(info_frame, bg=AdvancedConfig.COLORS['darker'], padx=20, pady=15)
        author_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(author_frame, text=f"👨‍💻 Desenvolvido por {AdvancedConfig.AUTHOR}", font=("Segoe UI", 10, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=author_frame['bg']).pack()
        
        # Links
        links_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        links_frame.pack(fill=tk.X, pady=20)
        
        links = [
            ("🐛 GitHub", AdvancedConfig.GITHUB, AdvancedConfig.COLORS['text']),
            ("💬 Discord", AdvancedConfig.DISCORD, AdvancedConfig.COLORS['primary']),
        ]
        
        for text, url, color in links:
            btn = tk.Button(links_frame, text=text, font=("Segoe UI", 10, "bold"),
                           fg=AdvancedConfig.COLORS['dark'], bg=color, bd=0, padx=20, pady=8,
                           cursor='hand2', command=lambda u=url: self.open_url(u))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Copyright
        tk.Label(self.dynamic_content, text=f"© 2024 {AdvancedConfig.AUTHOR}. Todos os direitos reservados.",
                font=("Segoe UI", 8), fg=AdvancedConfig.COLORS['text_secondary'],
                bg=AdvancedConfig.COLORS['dark']).pack(pady=10)
    
    def open_url(self, url):
        """Abre URL no navegador"""
        try:
            import webbrowser
            webbrowser.open(url)
        except:
            messagebox.showerror("Erro", "Não foi possível abrir o link")
    
    def update_terminal(self, message):
        pass
    
    def update_performance_data(self, data):
        try:
            if self.cpu_label.winfo_exists():
                cpu_val = list(data['cpu'])[-1] if data['cpu'] else 0
                self.cpu_label.config(text=f"CPU: {cpu_val:.1f}%")
                
                # Atualizar barra de CPU com animação
                if hasattr(self, 'cpu_bar_rect'):
                    bar_width = self.cpu_bar.winfo_width()
                    new_width = (cpu_val / 100) * bar_width
                    self.cpu_bar.coords(self.cpu_bar_rect, 0, 0, new_width, 6)
                
                ram_val = list(data['ram'])[-1] if data['ram'] else 0
                self.ram_label.config(text=f"RAM: {ram_val:.1f}%")
                
                # Atualizar barra de RAM com animação
                if hasattr(self, 'ram_bar_rect'):
                    bar_width = self.ram_bar.winfo_width()
                    new_width = (ram_val / 100) * bar_width
                    self.ram_bar.coords(self.ram_bar_rect, 0, 0, new_width, 6)
            
            # Atualizar dashboard se existir
            if hasattr(self, 'dashboard_metrics'):
                if 'cpu' in self.dashboard_metrics:
                    label, unit = self.dashboard_metrics['cpu']
                    if label.winfo_exists():
                        cpu_val = list(data['cpu'])[-1] if data['cpu'] else 0
                        label.config(text=f"{cpu_val:.1f}{unit}")
                
                if 'ram' in self.dashboard_metrics:
                    label, unit = self.dashboard_metrics['ram']
                    if label.winfo_exists():
                        ram_val = list(data['ram'])[-1] if data['ram'] else 0
                        label.config(text=f"{ram_val:.1f}{unit}")
                
                if 'disk' in self.dashboard_metrics:
                    label, unit = self.dashboard_metrics['disk']
                    if label.winfo_exists():
                        disk_val = data.get('disk', 0)
                        label.config(text=f"{disk_val:.1f}{unit}")
                
                if 'temp' in self.dashboard_metrics:
                    label, unit = self.dashboard_metrics['temp']
                    if label.winfo_exists():
                        temp_val = data.get('temp', 0)
                        if temp_val > 0:
                            label.config(text=f"{temp_val:.0f}{unit}")
                        else:
                            label.config(text="N/A")
        except:
            pass
    
    def update_dashboard_metrics(self):
        """Atualiza métricas do dashboard"""
        if hasattr(self, 'dashboard_metrics'):
            try:
                data = self.performance_monitor.data
                self.update_performance_data(data)
            except:
                pass
        self.root.after(1000, self.update_dashboard_metrics)
    
    def update_ui_loop(self):
        try:
            self.root.after(1000, self.update_ui_loop)
        except:
            pass
    
    def load_config(self):
        try:
            if os.path.exists(AdvancedConfig.CONFIG_FILE):
                with open(AdvancedConfig.CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def check_updates_background(self):
        pass
    
    def show_welcome_beta(self):
        """Tela de boas-vindas ao beta"""
        self.clear_content()
        self.hide_fabs()
        
        # Container centralizado
        container = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo grande
        tk.Label(container, text="⚡", font=("Segoe UI", 120, "bold"),
                fg=AdvancedConfig.COLORS['neon_blue'], bg=container['bg']).pack(pady=(0, 20))
        
        # Título
        tk.Label(container, text="BEM-VINDO AO BETA", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=container['bg']).pack(pady=(0, 10))
        
        # Versão
        tk.Label(container, text=f"Kelven Optimizer PRO v{AdvancedConfig.VERSION}", 
                font=("Segoe UI", 16),
                fg=AdvancedConfig.COLORS['primary'], bg=container['bg']).pack(pady=(0, 30))
        
        # Mensagem
        msg_frame = tk.Frame(container, bg=AdvancedConfig.COLORS['card'], padx=40, pady=30)
        msg_frame.pack()
        
        tk.Label(msg_frame, text="🎉 Obrigado por testar!", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['success'], bg=msg_frame['bg']).pack(pady=(0, 15))
        
        features = [
            "✨ Interface Moderna e Intuitiva",
            "🚀 84+ Tweaks Inteligentes",
            "🎮 Modo Gaming Otimizado",
            "🔄 Sistema de Atualizações Automático"
        ]
        
        for feature in features:
            tk.Label(msg_frame, text=feature, font=("Segoe UI", 11),
                    fg=AdvancedConfig.COLORS['text'], bg=msg_frame['bg']).pack(pady=3)
        
        # Loading
        tk.Label(container, text="Carregando...", font=("Segoe UI", 10),
                fg=AdvancedConfig.COLORS['text_secondary'], bg=container['bg']).pack(pady=(30, 0))
    
    def show_startup_apps(self):
        """Gerenciador de aplicativos de inicialização"""
        self.clear_content()
        
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="🚀 Startup Apps Manager", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Info
        info_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['warning'], padx=20, pady=15)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(info_frame, text="⚠️ Gerencie aplicativos que iniciam com o Windows",
                font=("Segoe UI", 10, "bold"), fg=AdvancedConfig.COLORS['dark'],
                bg=info_frame['bg']).pack()
        
        # Lista de apps
        apps_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
        apps_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(apps_frame, text="📝 Aplicativos de Inicialização", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=apps_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        # Obter apps de startup
        startup_apps = self.get_startup_apps()
        
        if not startup_apps:
            tk.Label(apps_frame, text="Nenhum aplicativo encontrado", font=("Segoe UI", 10),
                    fg=AdvancedConfig.COLORS['text_secondary'], bg=apps_frame['bg']).pack()
        else:
            for app_name, app_path, enabled in startup_apps:
                app_row = tk.Frame(apps_frame, bg=AdvancedConfig.COLORS['darker'], padx=15, pady=10)
                app_row.pack(fill=tk.X, pady=2)
                
                status_color = AdvancedConfig.COLORS['success'] if enabled else AdvancedConfig.COLORS['danger']
                tk.Label(app_row, text="●", font=("Segoe UI", 16), fg=status_color,
                        bg=app_row['bg']).pack(side=tk.LEFT, padx=(0, 10))
                
                info_frame = tk.Frame(app_row, bg=app_row['bg'])
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                tk.Label(info_frame, text=app_name, font=("Segoe UI", 10, "bold"),
                        fg=AdvancedConfig.COLORS['text'], bg=info_frame['bg']).pack(anchor=tk.W)
                tk.Label(info_frame, text=app_path[:60] + "..." if len(app_path) > 60 else app_path,
                        font=("Segoe UI", 8), fg=AdvancedConfig.COLORS['text_secondary'],
                        bg=info_frame['bg']).pack(anchor=tk.W)
                
                btn_text = "Desabilitar" if enabled else "Habilitar"
                btn_color = AdvancedConfig.COLORS['danger'] if enabled else AdvancedConfig.COLORS['success']
                tk.Button(app_row, text=btn_text, font=("Segoe UI", 9, "bold"),
                         fg=AdvancedConfig.COLORS['dark'], bg=btn_color, bd=0, padx=15, pady=5,
                         cursor='hand2', command=lambda n=app_name: self.toggle_startup_app(n)).pack(side=tk.RIGHT)
    
    def get_startup_apps(self):
        """Obtém lista de aplicativos de inicialização"""
        apps = []
        try:
            # Registry Run
            key_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
            ]
            
            for root, path in key_paths:
                try:
                    key = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            apps.append((name, value, True))
                            i += 1
                        except WindowsError:
                            break
                    winreg.CloseKey(key)
                except:
                    pass
        except:
            pass
        return apps[:20]  # Limitar a 20 apps
    
    def toggle_startup_app(self, app_name):
        """Habilita/desabilita app de startup"""
        messagebox.showinfo("Em Desenvolvimento", f"Funcionalidade para {app_name} em desenvolvimento")
    
    def show_updates(self):
        """Sistema de atualizações do GitHub"""
        self.clear_content()
        
        header = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="🔄 Sistema de Atualizações", font=("Segoe UI", 32, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=header['bg']).pack(side=tk.LEFT)
        
        # Status atual
        status_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(status_frame, text="💻 Versão Atual", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=status_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(status_frame, text=f"v{AdvancedConfig.VERSION}", font=("Segoe UI", 24, "bold"),
                fg=AdvancedConfig.COLORS['primary'], bg=status_frame['bg']).pack(anchor=tk.W)
        
        # Botão verificar
        btn_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['dark'])
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(btn_frame, text="🔍 VERIFICAR ATUALIZAÇÕES", font=("Segoe UI", 12, "bold"),
                 fg=AdvancedConfig.COLORS['dark'], bg=AdvancedConfig.COLORS['neon_blue'],
                 bd=0, padx=30, pady=12, cursor='hand2',
                 command=self.check_github_updates).pack()
        
        # Info do GitHub
        github_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=25, pady=20)
        github_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(github_frame, text="🐛 GitHub Repository", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=github_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(github_frame, text="https://github.com/kelven-optimizer/kelven-optimizer",
                font=("Segoe UI", 10), fg=AdvancedConfig.COLORS['neon_blue'],
                bg=github_frame['bg'], cursor='hand2').pack(anchor=tk.W)
        
        # Changelog
        changelog_frame = tk.Frame(self.dynamic_content, bg=AdvancedConfig.COLORS['card'], padx=20, pady=15)
        changelog_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(changelog_frame, text="📝 Changelog", font=("Segoe UI", 14, "bold"),
                fg=AdvancedConfig.COLORS['text'], bg=changelog_frame['bg']).pack(anchor=tk.W, pady=(0, 10))
        
        changelog_text = scrolledtext.ScrolledText(changelog_frame, bg=AdvancedConfig.COLORS['darker'],
                                                   fg=AdvancedConfig.COLORS['text'], font=("Consolas", 9),
                                                   height=10, padx=10, pady=10)
        changelog_text.pack(fill=tk.BOTH, expand=True)
        changelog_text.insert(tk.END, "Clique em 'VERIFICAR ATUALIZAÇÕES' para ver o changelog...")
        changelog_text.config(state='disabled')
    
    def check_github_updates(self):
        """Verifica atualizações no GitHub"""
        def check_thread():
            try:
                url = "https://api.github.com/repos/kelven-optimizer/kelven-optimizer/releases/latest"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['tag_name'].replace('v', '')
                    changelog = data.get('body', 'Sem informações')
                    download_url = data.get('html_url', '')
                    
                    self.root.after(0, lambda: self.show_update_info(latest_version, changelog, download_url))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Erro", "Não foi possível verificar atualizações"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao verificar: {e}"))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def show_update_info(self, latest_version, changelog, download_url):
        """Mostra informações da atualização"""
        current = AdvancedConfig.VERSION
        
        if latest_version > current:
            msg = f"Nova versão disponível!\n\nAtual: v{current}\nNova: v{latest_version}\n\nDeseja abrir a página de download?"
            if messagebox.askyesno("🎉 Atualização Disponível", msg):
                import webbrowser
                webbrowser.open(download_url)
        else:
            messagebox.showinfo("✅ Atualizado", f"Você já está na versão mais recente (v{current})")

# ========= MAIN =========
def main():
    if not SystemUtils.is_admin():
        messagebox.showwarning("Aviso", "Execute como Administrador para funcionalidade completa!")
    
    root = tk.Tk()
    app = KelvenOptimizerPRO(root)
    root.mainloop()

if __name__ == "__main__":
    main()
