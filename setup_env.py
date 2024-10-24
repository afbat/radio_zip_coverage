# to automate setting up python env can use instead of requirements.txt

import os
import subprocess
import sys

def install_packages():
    packages = [
        "selenium",
        "pandas",
        "webdriver-manager",
        "pyautogui"
    ]
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()
