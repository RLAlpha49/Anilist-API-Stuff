import subprocess
import sys

def install_packages(packages):
    for package in packages:
        try:
            print("\nInstalling " + package + "...\n")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
        except FileNotFoundError:
            print("Python or pip is not installed on this system.")
            input("Please install Python and pip and try again. Press enter to exit...")
            break

# List of packages to install
packages = ["requests"]
print("Installing packages...\n")

install_packages(packages)
input("\nInstallation complete. Press enter to exit.")