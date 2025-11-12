import argparse
import os
import subprocess
import getpass
import string
from datetime import datetime


def open_folder(path: str):
    print(f"Opening folder: {path}")
    subprocess.run(["explorer", path])


def ensure_folder_exists(path: str):
    if not os.path.exists(path):
        print(f"Folder not found: {path}")
        create_choice = input("Do you want to create it? (y/n): ").strip().lower()
        if create_choice == "y":
            try:
                os.makedirs(path, exist_ok=True)
                print(f"Created folder: {path}")
            except Exception as e:
                print(f"Error creating folder: {e}")
                return False
        else:
            print("Exiting without creating folder.")
            return False
    return True


def open_onedrive(year: int, case: str, user: str):
    path = rf"C:\Users\{user}\OneDrive\Documents\Forensic Reports\{year}\F-{year}-{case}"
    if ensure_folder_exists(path):
        open_folder(path)


def open_nas(year: int, case: str):
    path = rf"\\192.168.9.10\Case Archive\Case-Forensic\{year}\F-{year}-{case}"
    if ensure_folder_exists(path):
        open_folder(path)


def find_case_in_drives(year: int, case: str):
    found_paths = []
    target_name = f"F-{year}-{case}"

    for drive in string.ascii_uppercase:
        drive_path = f"{drive}:\\"
        if os.path.exists(drive_path) and not drive_path.lower().startswith("c"):
            try:
                for root, dirs, _ in os.walk(drive_path):
                    if target_name in dirs:
                        found_paths.append(os.path.join(root, target_name))
                        break
            except PermissionError:
                continue
    return found_paths


def open_external(year: int, case: str):
    print("Scanning external drives...")
    found_paths = find_case_in_drives(year, case)

    if not found_paths:
        print(f"No drives found containing F-{year}-{case}.")
        return
    elif len(found_paths) == 1:
        print(f"Found and opening: {found_paths[0]}")
        open_folder(found_paths[0])
        return

    print("Multiple matches found:")
    for i, path in enumerate(found_paths, start=1):
        print(f"{i}. {path}")

    try:
        sel = int(input("Choose which to open: ").strip())
        if 1 <= sel <= len(found_paths):
            open_folder(found_paths[sel - 1])
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", nargs="?", type=int, default=1, help="Case number (e.g. 12)")
    parser.add_argument("-y", "--year", type=int, default=datetime.now().year, help="Year (default: current year)")
    args = parser.parse_args()

    year = args.year
    case = str(args.case).zfill(3)
    user = getpass.getuser()

    print("1. OneDrive")
    print("2. NAS")
    print("3. External Drive Scan")
    choice = input("Choose the location to open the case folder: ").strip()

    if choice == "1":
        open_onedrive(year, case, user)
    elif choice == "2":
        open_nas(year, case)
    elif choice == "3":
        open_external(year, case)
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()
