#!/usr/bin/env python3
"""
File monitoring module for Windows Downloads folder
Handles file scanning, SHA1 calculation, and CSV data management
"""

import hashlib
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


def calculate_sha1(file_path: str, chunk_size: int = 8192, max_size_mb: Optional[int] = None) -> Optional[str]:
    """
    Calculate SHA1 hash value of a file
    
    Args:
        file_path: File path
        chunk_size: Size of chunks to read (default: 8192 bytes)
        max_size_mb: Maximum file size in MB to calculate SHA1 (None = no limit)
    
    Returns:
        SHA1 hash value, or None if file doesn't exist, can't be read, or exceeds size limit
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not os.path.exists(file_path):
            return None
        
        # Check file size if limit is set
        if max_size_mb is not None:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                logger.debug(f"Skipping SHA1 for large file: {file_path} ({file_size / 1024 / 1024:.1f} MB)")
                return "SKIPPED_TOO_LARGE"
        
        sha1_hash = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha1_hash.update(chunk)
        return sha1_hash.hexdigest()
        
    except PermissionError:
        logger.warning(f"Permission denied: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error calculating SHA1 for {file_path}: {e}")
        return None


def get_file_timestamp(file_path: str, legacy_format: bool = False) -> Optional[str]:
    """
    Get the last modification timestamp of a file
    
    Args:
        file_path: File path
        legacy_format: If True, return YY/MM/DD format; otherwise ISO8601 format
    
    Returns:
        Timestamp string, or None if file doesn't exist or error occurs
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not os.path.exists(file_path):
            return None
        
        timestamp = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(timestamp)
        
        if legacy_format:
            return dt.strftime("%y/%m/%d")
        else:
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
            
    except Exception as e:
        logger.error(f"Error getting timestamp for {file_path}: {e}")
        return None


def get_downloads_path(override_path: Optional[str] = None) -> str:
    """
    Get Downloads folder path for Windows system
    
    Args:
        override_path: Override path if specified
    
    Returns:
        Complete path to Downloads folder
    """
    logger = logging.getLogger(__name__)
    
    # Use override path if provided
    if override_path:
        if os.path.exists(override_path):
            logger.info(f"Using override path: {override_path}")
            return override_path
        else:
            logger.warning(f"Override path doesn't exist: {override_path}")
    
    # Windows Downloads folder
    user_profile = os.path.expanduser("~")
    downloads_path = os.path.join(user_profile, "Downloads")
    return downloads_path


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging
    
    Returns:
        System information dictionary
    """
    import platform
    
    info = {
        "platform": "Windows",
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "downloads_path": get_downloads_path(),
    }
    
    return info


def scan_downloads_folder(
    downloads_path: Optional[str] = None,
    excluded_files: Optional[List[str]] = None,
    category_folders: Optional[List[str]] = None,
    calculate_sha1_enabled: bool = True,
    max_file_size_mb: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Scan Downloads folder to get information about all files
    
    Args:
        downloads_path: Path to Downloads folder (uses default if None)
        excluded_files: List of filenames to exclude
        category_folders: List of category folder names
        calculate_sha1_enabled: Whether to calculate SHA1 hashes
        max_file_size_mb: Maximum file size for SHA1 calculation
    
    Returns:
        List of dictionaries containing file information
    """
    logger = logging.getLogger(__name__)
    
    if downloads_path is None:
        downloads_path = get_downloads_path()
    
    if not os.path.exists(downloads_path):
        logger.error(f"Downloads folder doesn't exist: {downloads_path}")
        return []
    
    if excluded_files is None:
        excluded_files = ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"]
    
    if category_folders is None:
        category_folders = ["Programs", "Compressed", "Documents", "Pictures", "Music", "Video"]
    
    files_info = []
    
    # Scan files in root directory
    try:
        for item in os.listdir(downloads_path):
            # Skip excluded files and category folders
            if item in excluded_files or item in category_folders:
                continue
            
            item_path = os.path.join(downloads_path, item)
            
            if os.path.isfile(item_path):
                file_info = _create_file_info(
                    item_path, "~", item, 
                    calculate_sha1_enabled, max_file_size_mb
                )
                if file_info:
                    files_info.append(file_info)
    except PermissionError:
        logger.error(f"Permission denied accessing: {downloads_path}")
        return []
    
    # Scan category folders
    for category in category_folders:
        category_path = os.path.join(downloads_path, category)
        if not os.path.exists(category_path) or not os.path.isdir(category_path):
            continue
        
        try:
            for item in os.listdir(category_path):
                if item in excluded_files:
                    continue
                
                item_path = os.path.join(category_path, item)
                
                if os.path.isfile(item_path):
                    file_info = _create_file_info(
                        item_path, category, item,
                        calculate_sha1_enabled, max_file_size_mb
                    )
                    if file_info:
                        files_info.append(file_info)
        except PermissionError:
            logger.warning(f"Permission denied accessing: {category_path}")
            continue
    
    logger.info(f"Scanned {len(files_info)} files in {downloads_path}")
    return files_info


def _create_file_info(
    file_path: str,
    folder_name: str,
    filename: str,
    calculate_sha1_enabled: bool,
    max_file_size_mb: Optional[int]
) -> Optional[Dict[str, Any]]:
    """
    Create file information dictionary
    
    Args:
        file_path: Full path to file
        folder_name: Folder name (or '~' for root)
        filename: File name
        calculate_sha1_enabled: Whether to calculate SHA1
        max_file_size_mb: Maximum file size for SHA1
    
    Returns:
        File information dictionary, or None if error
    """
    try:
        sha1 = None
        if calculate_sha1_enabled:
            sha1 = calculate_sha1(file_path, max_size_mb=max_file_size_mb)
        
        return {
            "root_dir": "~",
            "folder_name": folder_name,
            "filename": filename,
            "full_path": file_path,
            "sha1": sha1,
            "timestamp": get_file_timestamp(file_path),
        }
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating file info for {file_path}: {e}")
        return None


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


def update_csv_data(existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]], excluded_files: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Update CSV data with SHA1-based deduplication
    
    Args:
        existing_data: Existing CSV data
        new_data: Newly scanned data
        excluded_files: List of filenames to exclude
    
    Returns:
        Updated data with duplicates removed
    """
    logger = logging.getLogger(__name__)
    
    if excluded_files is None:
        excluded_files = ["desktop.ini", "Thumbs.db", ".DS_Store"]
    
    # Create SHA1-based index
    sha1_index: Dict[str, List[Dict[str, Any]]] = {}
    
    # Process existing data
    for item in existing_data:
        if item["filename"] in excluded_files:
            continue
        
        sha1 = item.get("sha1")
        if not sha1 or sha1 == "SKIPPED_TOO_LARGE":
            # For files without SHA1, use path as key
            sha1 = f"PATH:{item['folder_name']}/{item['filename']}"
        
        if sha1 not in sha1_index:
            sha1_index[sha1] = []
        sha1_index[sha1].append(item)
    
    # Process new data
    updated_data = []
    processed_keys = set()
    
    for new_item in new_data:
        if new_item["filename"] in excluded_files:
            continue
        
        sha1 = new_item.get("sha1")
        if not sha1 or sha1 == "SKIPPED_TOO_LARGE":
            sha1 = f"PATH:{new_item['folder_name']}/{new_item['filename']}"
        
        if sha1 in processed_keys:
            continue
        
        if sha1 in sha1_index:
            # Found existing file - keep most recent
            existing_items = sha1_index[sha1]
            most_recent = new_item
            
            for existing in existing_items:
                if compare_timestamps(existing["timestamp"], most_recent["timestamp"]) > 0:
                    most_recent = existing
            
            updated_data.append(most_recent)
            processed_keys.add(sha1)
            
            if len(existing_items) > 1 or most_recent != new_item:
                logger.debug(f"Deduplicated: {new_item['filename']} (kept version in {most_recent['folder_name']})")
        else:
            # New file
            updated_data.append(new_item)
            processed_keys.add(sha1)
    
    logger.info(f"Updated data: {len(updated_data)} unique files")
    return updated_data


def save_to_csv(data: List[Dict[str, Any]], csv_path: Optional[str] = None, create_backup: bool = False) -> bool:
    """
    Save data to CSV file
    
    Args:
        data: Data to save
        csv_path: CSV file path (if None, saves to Downloads folder)
        create_backup: Whether to create backup of existing file (disabled by default)
    
    Returns:
        True if successful, False otherwise
    """
    import csv
    
    logger = logging.getLogger(__name__)
    
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
                # Create path in format: ~\folder\name
                if item["folder_name"] == "~":
                    path = f"~\\{item['filename']}"
                    rel_path = item['filename']
                else:
                    path = f"~\\{item['folder_name']}\\{item['filename']}"
                    rel_path = f"{item['folder_name']}/{item['filename']}"
                
                # Generate legacy timestamp for backward compatibility
                legacy_timestamp = get_file_timestamp(item.get('full_path', ''), legacy_format=True) if item.get('full_path') else item.get('timestamp', '')
                
                writer.writerow({
                    "path": path,
                    "rel_path": rel_path,
                    "folder_name": item['folder_name'],
                    "filename": item['filename'],
                    "sha1sum": item.get("sha1", ""),
                    "timestamp": legacy_timestamp or item.get('timestamp', ''),
                    "mtime_iso": item.get('timestamp', '')
                })
        
        logger.info(f"Data saved to {csv_path} ({len(data)} records)")
        return True
        
    except PermissionError:
        logger.error(f"Permission denied writing to: {csv_path}")
        return False
    except Exception as e:
        logger.error(f"Error saving CSV file: {e}")
        return False


def load_from_csv(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load data from CSV file with backward compatibility
    
    Args:
        csv_path: CSV file path (if None, loads from Downloads folder)
    
    Returns:
        Loaded data with reconstructed full_path
    """
    import csv
    
    logger = logging.getLogger(__name__)
    
    # If no path specified, load from Downloads folder
    if csv_path is None:
        downloads_path = get_downloads_path()
        csv_path = os.path.join(downloads_path, "results.csv")
    
    if not os.path.exists(csv_path):
        logger.info(f"CSV file not found: {csv_path}")
        return []
    
    data = []
    try:
        downloads_path = get_downloads_path()
        with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Handle both old and new CSV formats
                if "folder_name" in row and "filename" in row:
                    folder_name = row["folder_name"]
                    filename = row["filename"]
                    rel_path = row.get("rel_path", "")
                else:
                    # Legacy format - parse from path
                    path = row["path"]
                    if path.startswith("~\\"):
                        path_parts = path[2:].split("\\")
                        if len(path_parts) == 1:
                            folder_name = "~"
                            filename = path_parts[0]
                            rel_path = filename
                        else:
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
                
                data.append({
                    "root_dir": "~",
                    "folder_name": folder_name,
                    "filename": filename,
                    "full_path": full_path,
                    "rel_path": rel_path,
                    "sha1": row.get("sha1sum", ""),
                    "timestamp": timestamp,
                })
        
        logger.info(f"Loaded {len(data)} records from {csv_path}")
        
    except PermissionError:
        logger.error(f"Permission denied reading: {csv_path}")
    except Exception as e:
        logger.error(f"Error loading CSV file: {e}")
    
    return data


def clean_duplicate_sha1s(csv_path: Optional[str] = None) -> bool:
    """
    Clean up duplicate SHA1 entries in existing CSV file
    
    Args:
        csv_path: CSV file path (if None, uses Downloads folder)
    
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Cleaning up duplicate SHA1 entries...")
        
        existing_data = load_from_csv(csv_path)
        if not existing_data:
            logger.info("No existing data to clean")
            return True
        
        logger.info(f"Found {len(existing_data)} existing records")
        
        # Deduplicate
        cleaned_data = update_csv_data(existing_data, existing_data)
        
        logger.info(f"After deduplication: {len(cleaned_data)} records")
        
        # Save cleaned data
        if save_to_csv(cleaned_data, csv_path):
            logger.info("Duplicate SHA1 entries cleaned successfully")
            return True
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error cleaning duplicate SHA1 entries: {e}")
        return False
