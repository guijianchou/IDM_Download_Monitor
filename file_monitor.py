import hashlib
import os
import time
import platform
from datetime import datetime
from pathlib import Path


def calculate_sha1(file_path):
    """
    Calculate SHA1 hash value of a file

    Args:
        file_path (str): File path

    Returns:
        str: SHA1 hash value, returns None if file doesn't exist or can't be read
    """
    try:
        if not os.path.exists(file_path):
            return None

        sha1_hash = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1_hash.update(chunk)
        return sha1_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating SHA1 for {file_path}: {e}")
        return None


def get_file_timestamp(file_path):
    """
    Get the last modification timestamp of a file

    Args:
        file_path (str): File path

    Returns:
        str: Timestamp string in YY/MM/DD format
    """
    try:
        if not os.path.exists(file_path):
            return None

        timestamp = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%y/%m/%d")
    except Exception as e:
        print(f"Error getting timestamp for {file_path}: {e}")
        return None


def is_wsl2():
    """
    Check if running in WSL2 environment

    Returns:
        bool: True if running in WSL2, False otherwise
    """
    try:
        # Check for WSL2 specific indicators
        if os.path.exists("/proc/version"):
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    return True

        # Check environment variables
        if "WSL_DISTRO_NAME" in os.environ:
            return True

        return False
    except Exception:
        return False


def get_downloads_path():
    """
    Get Downloads folder path based on system environment

    Returns:
        str: Complete path to Downloads folder
    """
    # Check if running in WSL2
    if is_wsl2():
        print("WSL2 environment detected")

        # Use WSL2 path with default username 'zen'
        wsl2_path = "/mnt/c/Users/zen/Downloads"
        if os.path.exists(wsl2_path):
            print(f"Using WSL2 path: {wsl2_path}")
            return wsl2_path

        # If default path not found, try to get Windows username
        try:
            import subprocess

            result = subprocess.run(["cmd.exe", "/c", "echo %USERNAME%"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                username = result.stdout.strip().lower()
                if username:
                    fallback_path = f"/mnt/c/Users/{username}/Downloads"
                    if os.path.exists(fallback_path):
                        print(f"Using detected username path: {fallback_path}")
                        return fallback_path
        except Exception:
            pass

        print("WSL2 detected but Downloads path not found, falling back to Windows path")

    # Windows native path
    user_profile = os.path.expanduser("~")
    downloads_path = os.path.join(user_profile, "Downloads")
    return downloads_path


def get_system_info():
    """
    Get system information for debugging

    Returns:
        dict: System information dictionary
    """
    info = {
        "platform": platform.system(),
        "machine": platform.machine(),
        "node": platform.node(),
        "is_wsl2": is_wsl2(),
        "downloads_path": get_downloads_path(),
        "env_vars": {k: v for k, v in os.environ.items() if "WSL" in k or "MICROSOFT" in k},
    }

    return info


def scan_downloads_folder():
    """
    Scan Downloads folder to get information about all files and folders

    Returns:
        list: List of dictionaries containing file information
    """
    downloads_path = get_downloads_path()
    if not os.path.exists(downloads_path):
        print(f"Downloads folder doesn't exist: {downloads_path}")
        return []

    files_info = []

    # Define category folders
    category_folders = ["Programs", "Compressed", "Documents", "Music", "Video"]

    # Scan files in root directory (unorganized files)
    for item in os.listdir(downloads_path):
        item_path = os.path.join(downloads_path, item)

        # Skip results.csv file, desktop.ini file, and category folders
        if item == "results.csv" or item == "desktop.ini" or item in category_folders:
            continue

        if os.path.isfile(item_path):
            # Files in root directory (unorganized)
            file_info = {
                "root_dir": "~",
                "folder_name": "~",  # Root directory files get '~' as folder_name
                "filename": item,
                "full_path": item_path,
                "sha1": calculate_sha1(item_path),
                "timestamp": get_file_timestamp(item_path),
            }
            files_info.append(file_info)

    # Scan category folders
    for category in category_folders:
        category_path = os.path.join(downloads_path, category)
        if os.path.exists(category_path) and os.path.isdir(category_path):
            for item in os.listdir(category_path):
                item_path = os.path.join(category_path, item)

                if os.path.isfile(item_path):
                    # Skip desktop.ini files
                    if item == "desktop.ini":
                        continue

                    file_info = {
                        "root_dir": "~",
                        "folder_name": category,
                        "filename": item,
                        "full_path": item_path,
                        "sha1": calculate_sha1(item_path),
                        "timestamp": get_file_timestamp(item_path),
                    }
                    files_info.append(file_info)

    return files_info


def update_csv_data(existing_data, new_data):
    """
    Update CSV data with improved SHA1-based deduplication

    Args:
        existing_data (list): Existing CSV data
        new_data (list): Newly scanned data

    Returns:
        list: Updated data with duplicates removed
    """
    # Create SHA1-based index for existing data
    sha1_index = {}
    
    # Process existing data
    for item in existing_data:
        # Skip desktop.ini files
        if item["filename"] == "desktop.ini":
            continue
            
        sha1 = item["sha1"]
        
        # Store by SHA1 (for deduplication)
        if sha1 not in sha1_index:
            sha1_index[sha1] = []
        sha1_index[sha1].append(item)

    # Process new data
    updated_data = []
    processed_sha1s = set()
    
    for new_item in new_data:
        # Skip desktop.ini files
        if new_item["filename"] == "desktop.ini":
            continue
            
        sha1 = new_item["sha1"]
        
        if sha1 in processed_sha1s:
            # This SHA1 has already been processed, skip
            continue
            
        if sha1 in sha1_index:
            # Found existing file with same SHA1
            existing_items = sha1_index[sha1]
            
            # Find the most recent version (by timestamp)
            most_recent = new_item
            for existing in existing_items:
                if existing["timestamp"] > most_recent["timestamp"]:
                    most_recent = existing
            
            # Add the most recent version
            updated_data.append(most_recent)
            processed_sha1s.add(sha1)
            
            print(f"Updated file: {new_item['filename']} (SHA1: {sha1[:8]}...) - kept version in {most_recent['folder_name']}")
            
        else:
            # New file, add it
            updated_data.append(new_item)
            processed_sha1s.add(sha1)

    return updated_data


def save_to_csv(data, csv_path=None):
    """
    Save data to CSV file in Downloads folder

    Args:
        data (list): Data to save
        csv_path (str): CSV file path (if None, saves to Downloads folder)
    """
    import csv

    # If no path specified, save to Downloads folder
    if csv_path is None:
        downloads_path = get_downloads_path()
        csv_path = os.path.join(downloads_path, "results.csv")

    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["path", "sha1sum", "timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in data:
                # Create path in format: ~\folder\name
                if item["folder_name"] == "~":
                    # Root directory files
                    path = f"~\\{item['filename']}"
                else:
                    # Subfolder files
                    path = f"~\\{item['folder_name']}\\{item['filename']}"

                writer.writerow({"path": path, "sha1sum": item["sha1"], "timestamp": item["timestamp"]})

        print(f"Data saved to {csv_path}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")


def load_from_csv(csv_path=None):
    """
    Load data from CSV file in Downloads folder

    Args:
        csv_path (str): CSV file path (if None, loads from Downloads folder)

    Returns:
        list: Loaded data
    """
    import csv

    # If no path specified, load from Downloads folder
    if csv_path is None:
        downloads_path = get_downloads_path()
        csv_path = os.path.join(downloads_path, "results.csv")

    data = []
    try:
        if os.path.exists(csv_path):
            with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Parse path to extract folder_name and filename
                    path = row["path"]
                    if path.startswith("~\\"):
                        path_parts = path[2:].split("\\")
                        if len(path_parts) == 1:
                            # Root directory file: ~\filename
                            folder_name = "~"
                            filename = path_parts[0]
                        else:
                            # Subfolder file: ~\folder\filename
                            folder_name = path_parts[0]
                            filename = path_parts[1]
                    else:
                        folder_name = "~"
                        filename = path

                    data.append(
                        {
                            "root_dir": "~",
                            "folder_name": folder_name,
                            "filename": filename,
                            "full_path": "",  # Full path not stored in CSV
                            "sha1": row["sha1sum"],
                            "timestamp": row["timestamp"],
                        }
                    )
    except Exception as e:
        print(f"Error loading CSV file: {e}")

    return data


def clean_duplicate_sha1s(csv_path=None):
    """
    Clean up duplicate SHA1 entries in existing CSV file
    
    Args:
        csv_path (str): CSV file path (if None, uses Downloads folder)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("Cleaning up duplicate SHA1 entries...")
        
        # Load existing data
        existing_data = load_from_csv(csv_path)
        if not existing_data:
            print("No existing data to clean")
            return True
            
        print(f"Found {len(existing_data)} existing records")
        
        # Use the improved update logic to deduplicate
        cleaned_data = update_csv_data(existing_data, existing_data)
        
        print(f"After deduplication: {len(cleaned_data)} records")
        
        # Save cleaned data
        save_to_csv(cleaned_data, csv_path)
        
        print("Duplicate SHA1 entries cleaned successfully")
        return True
        
    except Exception as e:
        print(f"Error cleaning duplicate SHA1 entries: {e}")
        return False


if __name__ == "__main__":
    # Test the improved deduplication
    print("Testing improved SHA1 deduplication...")
    
    # Load and clean existing data
    if clean_duplicate_sha1s():
        print("✅ Deduplication test completed successfully")
    else:
        print("❌ Deduplication test failed")
