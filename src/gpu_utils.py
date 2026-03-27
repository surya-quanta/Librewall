import os
import sys
import winreg
import subprocess
import time

def get_engine_path():
    """Resolves the absolute path to the engine executable/script."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        return os.path.join(base_dir, "engine.exe")
    else:
        # Absolute path ensures registry matches exactly (for python.exe)
        return os.path.abspath(sys.executable)

def get_gpu_info() -> list:
    """
    Uses a hidden PowerShell command to get the names of all Video Controllers.
    Intelligently sorts them so [0] is the iGPU (Power Saving) and [1] is the dGPU (High Performance).
    """
    try:
        cmd = [
            'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-Command',
            "(Get-CimInstance Win32_VideoController).Name"
        ]
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0 
        
        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW, timeout=3)
        
        names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        
        if len(names) == 2:
            igpu_idx = 0
            dgpu_idx = 1
            
            for i, name in enumerate(names):
                name_lower = name.lower()
                # Identify dGPU by common brand markers
                if any(brand in name_lower for brand in ['nvidia', 'geforce', 'rtx', 'gtx', 'dedicated']):
                    dgpu_idx = i
                    igpu_idx = 1 if i == 0 else 0
                # Distinguish AMD discrete (RX) from AMD integrated (Radeon Graphics)
                elif 'radeon' in name_lower and 'rx' in name_lower:
                    dgpu_idx = i
                    igpu_idx = 1 if i == 0 else 0
            
            return [names[igpu_idx], names[dgpu_idx]]
            
        return names if names else ["Unknown GPU"]
    except Exception as e:
        print(f"Error getting GPU names: {e}")
        return ["Unknown GPU"]

def get_gpu_preference() -> int:
    """Reads the current GPU preference from the Windows Registry."""
    engine_path = get_engine_path()
    reg_path = r"SOFTWARE\Microsoft\DirectX\UserGpuPreferences"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, engine_path)
        winreg.CloseKey(key)
        
        if "GpuPreference=1" in value: return 1
        elif "GpuPreference=2" in value: return 2
        return 0
    except (FileNotFoundError, OSError):
        return 0

def set_gpu_preference(level: int) -> bool:
    """Sets the GPU preference in the Windows Registry for the engine."""
    engine_path = get_engine_path()
    reg_path = r"SOFTWARE\Microsoft\DirectX\UserGpuPreferences"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
    except FileNotFoundError:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)

    try:
        if level == 0:
            try: winreg.DeleteValue(key, engine_path)
            except FileNotFoundError: pass
        else:
            value_str = f"GpuPreference={level};"
            winreg.SetValueEx(key, engine_path, 0, winreg.REG_SZ, value_str)
        return True
    except Exception as e:
        print(f"GPU Registry Error: {e}")
        return False
    finally:
        winreg.CloseKey(key)

def restart_librewall():
    """Kills LibreWall and restarts it (Supports both Source and Compiled)."""
    time.sleep(0.5) 
    
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        launcher_path = os.path.join(base_dir, "librewall.exe")
        cmd = f'ping 127.0.0.1 -n 2 > nul & taskkill /F /IM engine.exe /IM main.exe /IM librewall.exe & start "" "{launcher_path}"'
    else:
        launcher_py = os.path.abspath(sys.argv[0])
        cmd = f'ping 127.0.0.1 -n 2 > nul & taskkill /F /IM python.exe & start "" "{sys.executable}" "{launcher_py}"'
        
    subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    os._exit(0)