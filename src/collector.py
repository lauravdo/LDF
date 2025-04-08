import os
import platform
import getpass
import socket
import datetime
import subprocess
import logging
import winreg
import psutil
import win32api
import win32con
import win32security
import pywintypes
import wmi
import sqlite3


def verzamel_systeeminfo():
    info = []
    tijd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tijdzone = datetime.datetime.now().astimezone().tzinfo
    gebruiker = getpass.getuser()
    hostnaam = socket.gethostname()
    ip_adres = socket.gethostbyname(hostnaam)
    os_versie = platform.platform()
    architectuur = platform.machine()

    info.append(f"Datum en tijd start script: {tijd}")
    info.append(f"Tijdzone: {tijdzone}")
    info.append(f"Gebruiker: {gebruiker}")
    info.append(f"Hostnaam: {hostnaam}")
    info.append(f"IP-adres: {ip_adres}")
    info.append(f"OS-versie: {os_versie}")
    info.append(f"Architectuur: {architectuur}")

    return "\n".join(info)


def gebruikers_info():
    gebruikersinfo = []
    huidigegebruiker = getpass.getuser()
    huidigesessie = os.getlogin()
    output = subprocess.check_output("whoami", shell=True).decode()
    usernames = [line.split()[0] for line in output.splitlines()]
    num_users = len(usernames)
    gebruikersinfo.append(f"Aantal gebruikers: {num_users}")
    gebruikersinfo.append(f"Huidige gebruiker: {huidigesessie}")
    gebruikersinfo.append(f"Actieve gebruiker: {huidigegebruiker}")

    return "\n".join(gebruikersinfo)


def geinstalleerde_software():
    register_paden = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    geinstalleerde_programmas = []
    for pad in register_paden:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, pad) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            naam, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            geinstalleerde_programmas.append(naam)
                    except FileNotFoundError:
                        continue
                    except OSError:
                        continue
        except FileNotFoundError:
            continue

    return "\n".join(geinstalleerde_programmas)


def actieve_processen():
    actieve_processen = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            info = proc.info
            actieve_processen.append(f"PID: {info['pid']}, Naam: {info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return "\n".join(actieve_processen)


def netwerk_config():
    netwerk_configuratie = []
    hostname = socket.gethostname()
    ipadres = socket.gethostbyname(socket.gethostbyname(hostname))
    netwerk_configuratie.append(f"Hostname: {hostname}")
    netwerk_configuratie.append(f"IP-adres: {ipadres}")
    return "\n".join(netwerk_configuratie)


def usb_info():
    # Get currently connected USB storage devices
    c = wmi.WMI()
    apparaten = []
    
    # Check for currently connected USB drives
    for disk in c.Win32_DiskDrive():
        if "USB" in disk.InterfaceType or (disk.MediaType and "Removable" in disk.MediaType):
            model = disk.Model
            device_id = disk.DeviceID
            size_gb = round(int(disk.Size) / (1024 ** 3), 2) if disk.Size else "Unknown"

            # Link the disk to a drive letter
            schijfletter = "N/A"
            for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    schijfletter = logical_disk.DeviceID

            apparaten.append({
                "Model": model,
                "DeviceID": device_id,
                "Size": size_gb,
                "Drive_Letter": schijfletter,
                "Status": "Currently Connected"
            })
    
    # Get previously connected USB devices from registry
    try:
        # Open registry key where USB device history is stored
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                "SYSTEM\\CurrentControlSet\\Enum\\USBSTOR")
        
        
        subkey_count = winreg.QueryInfoKey(reg_key)[0]
        
        
        for i in range(subkey_count):
            device_key_name = winreg.EnumKey(reg_key, i)
            device_key = winreg.OpenKey(reg_key, device_key_name)
            
            # Try to get device info
            try:
                subkey_count_device = winreg.QueryInfoKey(device_key)[0]
                
                for j in range(subkey_count_device):
                    try:
                        instance_key_name = winreg.EnumKey(device_key, j)
                        instance_key = winreg.OpenKey(device_key, instance_key_name)
                        
                        # Parse device information from key name
                        parts = device_key_name.split('&')
                        if len(parts) >= 2:
                            model = parts[1].replace('_', ' ')
                            
                            # Check if this device is already in our list
                            if not any(d['Model'] == model for d in apparaten):
                                apparaten.append({
                                    "Model": model,
                                    "DeviceID": instance_key_name,
                                    "Size": "Unknown",
                                    "Drive_Letter": "N/A",
                                    "Status": "Previously Connected"
                                })
                        
                        winreg.CloseKey(instance_key)
                    except WindowsError:
                        continue
                    
            except WindowsError:
                continue
                
            winreg.CloseKey(device_key)
                
        winreg.CloseKey(reg_key)
    except WindowsError:
        pass
    
    # If no devices found, return a message
    if not apparaten:
        return ["No USB storage devices found (current or previous)"]

    # Collect output
    uitvoer = []
    for apparaat in apparaten:
        uitvoer.append(
            f"Model: {apparaat['Model']}\n"
            f"DeviceID: {apparaat['DeviceID']}\n"
            f"Size: {apparaat['Size']} GB\n"
            f"Drive letter: {apparaat['Drive_Letter']}\n"
            f"Status: {apparaat['Status']}\n"
            + "-" * 40
        )

    # Return the combined information as a string
    return "\n".join(uitvoer)



def recente_bestanden():
    recent_map = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Recent")
    bestanden = []
    for bestand in os.listdir(recent_map):
        bestandspad = os.path.join(recent_map, bestand)
        bestanden.append(bestandspad)
    return "\n".join(bestanden)
  
def browsergeschiedenis():
    browsers = {
        "Chrome": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History"),
        "Edge": os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\History"),
        "Firefox": os.path.expanduser(r"~\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\places.sqlite")
    }
    
    geschiedenis = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 5")
            for row in cursor.fetchall():
                geschiedenis.append(f"Browser: {browser}, URL: {row[0]}, Titel: {row[1]}, Aantal bezoeken: {row[2]}")
            conn.close()
    
    return "\n".join(geschiedenis)

def geinstalleerde_remote_tools():
    remote_tools = ["TeamViewer", "AnyDesk"]
    geïnstalleerde_tools = []
    for programma in geinstalleerde_software():  
        for tool in remote_tools:
            if tool in programma:
                geïnstalleerde_tools.append(programma)
    else:
        geïnstalleerde_tools.append(f"{programma} Geen remote tooling software gevonden")
    return "\n".join(geïnstalleerde_tools)