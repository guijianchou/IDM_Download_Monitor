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
        str: Timestamp string in ISO8601 format (YYYY-MM-DDTHH:MM:SS)
    """
    try:
        if not os.path.exists(file_path):
            return None

        timestamp = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        print(f"Error getting timestamp for {file_path}: {e}")
        return None


def get_file_timestamp_legacy(file_path):
    """
    Get the last modification timestamp of a file in legacy format
    
    Args:
        file_path (str): File path
    
    Returns:
        str: Timestamp string in YY/MM/DD format (for backward compatibility)
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


def get_downloads_path(override_path=None):
    """
    Get Downloads folder path based on system environment
    
    Args:
        override_path (str): Override path if specified

    Returns:
        str: Complete path to Downloads folder
    """
    # Use override path if provided
    if override_path:
        if os.path.exists(override_path):
            print(f"Using override path: {override_path}")
            return override_path
        else:
            print(f"Warning: Override path doesn't exist: {override_path}")
    
    # Check if running in WSL2
    if is_wsl2():
        print("WSL2 environment detected")
        
        # Check environment variable override first
        env_username = os.environ.get('MONITOR_WIN_USERNAME')
        if env_username:
            env_path = f"/mnt/c/Users/{env_username}/Downloads"
            if os.path.exists(env_path):
                print(f"Using environment username path: {env_path}")
                return env_path

        # Try to auto-detect by scanning /mnt/c/Users directory
        users_dir = "/mnt/c/Users"
        if os.path.exists(users_dir):
            try:
                for user_dir in os.listdir(users_dir):
                    if user_dir.lower() in ['public', 'default', 'all users']:
                        continue
                    downloads_candidate = os.path.join(users_dir, user_dir, "Downloads")
                    if os.path.exists(downloads_candidate) and os.access(downloads_candidate, os.R_OK):
                        print(f"Auto-detected WSL2 path: {downloads_candidate}")
                        return downloads_candidate
            except (PermissionError, OSError) as e:
                print(f"Error scanning users directory: {e}")
        
        # Fallback: Use WSL2 path with default username 'zen'
        wsl2_path = "/mnt/c/Users/zen/Downloads"
        if os.path.exists(wsl2_path):
            print(f"Using default WSL2 path: {wsl2_path}")
            return wsl2_path

        # Last resort: Try to get Windows username via cmd
        try:
            import subprocess
            result = subprocess.run(
                ["cmd.exe", "/c", "echo %USERNAME%"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                username = result.stdout.strip()
                if username and username != "%USERNAME%":
                    fallback_path = f"/mnt/c/Users/{username}/Downloads"
                    if os.path.exists(fallback_path):
                        print(f"Using cmd-detected username path: {fallback_path}")
                        return fallback_path
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"Failed to detect Windows username: {e}")

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


def compare_timestamps(ts1, ts2):
    """
    Compare two timestamps, handling both ISO8601 and legacy formats
    
    Args:
        ts1 (str): First timestamp
        ts2 (str): Second timestamp
    
    Returns:
        int: -1 if ts1 < ts2, 0 if equal, 1 if ts1 > ts2
    """
    try:
        # Try to parse as ISO8601 first
        if 'T' in ts1 and 'T' in ts2:
            dt1 = datetime.fromisoformat(ts1)
            dt2 = datetime.fromisoformat(ts2)
        else:
            # Fall back to legacy format parsing
            dt1 = datetime.strptime(ts1, "%y/%m/%d")
            dt2 = datetime.strptime(ts2, "%y/%m/%d")
        
        if dt1 < dt2:
            return -1
        elif dt1 > dt2:
            return 1
        else:
            return 0
    except (ValueError, TypeError):
        # If parsing fails, fall back to string comparison
        if ts1 < ts2:
            return -1
        elif ts1 > ts2:
            return 1
        else:
            return 0


def update_csv_data(existing_data, new_data):
    """
    Update CSV data with improved SHA1-based deduplication and better timestamp comparison

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
            
            # Find the most recent version (by timestamp) - prefer current scan
            most_recent = new_item
            for existing in existing_items:
                if compare_timestamps(existing["timestamp"], most_recent["timestamp"]) > 0:
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
    Save data to CSV file in Downloads folder with enhanced format

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
            fieldnames = ["path", "rel_path", "folder_name", "filename", "sha1sum", "timestamp", "mtime_iso"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in data:
                # Create path in format: ~\folder\name (backward compatibility)
                if item["folder_name"] == "~":
                    # Root directory files
                    path = f"~\\{item['filename']}"
                    rel_path = item['filename']
                else:
                    # Subfolder files
                    path = f"~\\{item['folder_name']}\\{item['filename']}"
                    rel_path = f"{item['folder_name']}/{item['filename']}"
                
                # Generate legacy timestamp for backward compatibility
                legacy_timestamp = get_file_timestamp_legacy(item.get('full_path', '')) if item.get('full_path') else item.get('timestamp', '')
                
                writer.writerow({
                    "path": path, 
                    "rel_path": rel_path,
                    "folder_name": item['folder_name'],
                    "filename": item['filename'],
                    "sha1sum": item["sha1"], 
                    "timestamp": legacy_timestamp or item.get('timestamp', ''),
                    "mtime_iso": item.get('timestamp', '')  # Now stores ISO8601 format
                })

        print(f"Data saved to {csv_path}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")


def load_from_csv(csv_path=None):
    """
    Load data from CSV file in Downloads folder with backward compatibility

    Args:
        csv_path (str): CSV file path (if None, loads from Downloads folder)

    Returns:
        list: Loaded data with reconstructed full_path
    """
    import csv

    # If no path specified, load from Downloads folder
    if csv_path is None:
        downloads_path = get_downloads_path()
        csv_path = os.path.join(downloads_path, "results.csv")

    data = []
    try:
        if os.path.exists(csv_path):
            downloads_path = get_downloads_path()
            with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Handle both old and new CSV formats
                    if "folder_name" in row and "filename" in row:
                        # New format - direct access
                        folder_name = row["folder_name"]
                        filename = row["filename"]
                        rel_path = row.get("rel_path", "")
                    else:
                        # Legacy format - parse from path
                        path = row["path"]
                        if path.startswith("~\\"):
                            path_parts = path[2:].split("\\")
                            if len(path_parts) == 1:
                                # Root directory file: ~\filename
                                folder_name = "~"
                                filename = path_parts[0]
                                rel_path = filename
                            else:
                                # Subfolder file: ~\folder\filename
                                folder_name = path_parts[0]
                                filename = path_parts[1]
                                rel_path = f"{folder_name}/{filename}"
                        else:
                            folder_name = "~"
                            filename = path
                            rel_path = filename
                    
                    # Reconstruct full_path
                    if folder_name == "~":
                        full_path = os.path.join(downloads_path, filename)
                    else:
                        full_path = os.path.join(downloads_path, folder_name, filename)
                    
                    # Use ISO timestamp if available, otherwise legacy timestamp
                    timestamp = row.get("mtime_iso", row.get("timestamp", ""))

                    data.append(
                        {
                            "root_dir": "~",
                            "folder_name": folder_name,
                            "filename": filename,
                            "full_path": full_path,  # Now reconstructed
                            "rel_path": rel_path,
                            "sha1": row["sha1sum"],
                            "timestamp": timestamp,
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
