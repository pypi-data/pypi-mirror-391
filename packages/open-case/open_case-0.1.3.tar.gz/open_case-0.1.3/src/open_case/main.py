import argparse
import os
import subprocess
import getpass
from datetime import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", type=int, default=datetime.now().year)
    parser.add_argument("-c", "--case", type=int, default=1)
    args = parser.parse_args()

    year = args.year
    case = str(args.case).zfill(3)
    user = getpass.getuser()

    onedrive_path = rf"C:\Users\{user}\OneDrive\Documents\Forensic Reports\{year}\F-{year}-{case}"
    nas_path = rf"\\192.168.9.10\Case Archive\Case-Forensic\{year}\F-{year}-{case}"

    print("Choose the location to open the case folder:")
    print("1. OneDrive")
    print("2. NAS")
    choice = input("Enter 1 or 2: ")
    if choice == "1":
        target_path = onedrive_path
    elif choice == "2":
        target_path = nas_path
    else:
        print("Invalid choice. Exiting.")
        return
    if os.path.exists(target_path):
        print(f"Opening folder: {target_path}")
        subprocess.run(["explorer", target_path])
    else:
        print(f"Folder not found: {target_path}")


if __name__ == "__main__":
    main()
