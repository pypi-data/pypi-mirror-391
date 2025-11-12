import requests
import sys

VERSION = 1
PYTHON_VERSION = "3.13.7"

if PYTHON_VERSION != str(sys.version.split()[0]):
    print(f"ArteLib [WARNING] - ArteLib is tested on Python 3.13.7! Current Version: {str(sys.version.split()[0])}")

try:
    response = requests.get("https://raw.githubusercontent.com/JustARocketGame/artelib_/refs/heads/main/version.txt")
    response.raise_for_status()
    
    content = response.text
    if VERSION < int(content):
        print(f"ArteLib [WARNING] - Please update ArteLib to new version! Current Version: {str(VERSION)} New Version: {content}")
    
except requests.exceptions.RequestException as e:
    print(f"ArteLib [ERROR] - {e}")