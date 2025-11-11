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

    if os.path.exists(onedrive_path):
        print(f"Opening folder: {onedrive_path}")
        subprocess.run(["explorer", onedrive_path])
    else:
        print(f"Folder not found: {onedrive_path}")


if __name__ == "__main__":
    main()
