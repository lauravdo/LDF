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
    c = wmi.WMI()
    apparaten = []
    
    for disk in c.Win32_DiskDrive():
        if "USB" in disk.InterfaceType:
            model = disk.Model
            device_id = disk.DeviceID
            size_gb = round(int(disk.Size) / (1024 ** 3), 2) if disk.Size else "Onbekend"

            # Koppel de disk aan een schijfletter
            schijfletter = "N/A"
            for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    schijfletter = logical_disk.DeviceID

            apparaten.append({
                "Model": model,
                "DeviceID": device_id,
                "Size": size_gb,
                "Schijfletter": schijfletter
            })

    if not apparaten:
        return "Geen USB-opslagapparaten gevonden"

    uitvoer = []
    for apparaat in apparaten:
        uitvoer.append(
            f"Model: {apparaat['Model']}\n"
            f"DeviceID: {apparaat['DeviceID']}\n"
            f"Size: {apparaat['Size']} GB\n"
            f"Drive letter: {apparaat['Schijfletter']}\n"
            + "-" * 40
        )
    
    # Return de samengevoegde string
    return "\n".join(uitvoer)