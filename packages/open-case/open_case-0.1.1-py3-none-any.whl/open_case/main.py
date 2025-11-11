import argparse
import os
import subprocess
import getpass
from datetime import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", default=datetime.now().year)
    parser.add_argument("-c", "--case", default="001")
    args = parser.parse_args()
    year = args.year
    case = args.case

    user = getpass.getuser()
    onedrive_path = rf"C:\Users\{user}\OneDrive\Documents\Forensic Reports\{year}\F-{year}-{case}"

    if os.path.exists(onedrive_path):
        print(f"Opening folder: {onedrive_path}")
        subprocess.run(["explorer", onedrive_path])
    else:
        print(f"Folder not found: {onedrive_path}")


if __name__ == "__main__":
    main()
