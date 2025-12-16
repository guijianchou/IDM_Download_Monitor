#!/usr/bin/env python3
"""File monitoring module for Windows Downloads folder"""

import csv
import hashlib
import logging
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


def calculate_sha1(file_path: str, chunk_size: int = 8192, max_size_mb: Optional[int] = None) -> Optional[str]:
    """Calculate SHA1 hash value of a file with optimized performance."""
    logger = logging.getLogger(__name__)
    path = Path(file_path)

    try:
        if not path.exists():
            return None

        file_size = path.stat().st_size
        
        if max_size_mb is not None and file_size > max_size_mb * 1024 * 1024:
            logger.debug(f"Skipping SHA1 for large file: {file_path} ({file_size / 1024 / 1024:.1f} MB)")
            return "SKIPPED_TOO_LARGE"

        # Optimize chunk size based on file size
        if file_size > 100 * 1024 * 1024:
            chunk_size = max(chunk_size, 65536)
        elif file_size > 10 * 1024 * 1024:
            chunk_size = max(chunk_size, 32768)

        sha1_hash = hashlib.sha1()
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                sha1_hash.update(chunk)
        
        return sha1_hash.hexdigest()

    except PermissionError:
        logger.warning(f"Permission denied: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error calculating SHA1 for {file_path}: {e}")
        return None


def get_file_timestamp(file_path: str) -> Optional[str]:
    """Get the last modification timestamp of a file in ISO8601 format."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        logging.getLogger(__name__).error(f"Error getting timestamp for {file_path}: {e}")
        return None


def scan_downloads_folder(downloads_path: Optional[str] = None, excluded_files: Optional[List[str]] = None,
                          category_folders: Optional[List[str]] = None, calculate_sha1_enabled: bool = True,
                          max_file_size_mb: Optional[int] = None, show_progress: bool = False,
                          existing_data: Optional[List[Dict[str, Any]]] = None, 
                          incremental: bool = False) -> List[Dict[str, Any]]:
    """Scan Downloads folder to get information about all files.
    
    Args:
        incremental: If True, only recalculate SHA1 for new/modified files
        existing_data: Previous scan data for incremental comparison
    """
    logger = logging.getLogger(__name__)

    if downloads_path is None:
        from config_manager import get_config
        downloads_path = get_config().get_downloads_path()
    
    path = Path(downloads_path)
    if not path.exists():
        logger.error(f"Downloads folder doesn't exist: {path}")
        return []

    excluded_files = excluded_files or ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"]
    category_folders = category_folders or ["Programs", "Documents", "Pictures", "Videos", "Compressed", "Music"]

    # Build index from existing data for incremental scan
    existing_index: Dict[str, Dict[str, Any]] = {}
    if incremental and existing_data:
        for item in existing_data:
            key = f"{item['folder_name']}/{item['filename']}"
            existing_index[key] = item
        logger.info(f"Incremental scan enabled, {len(existing_index)} existing records indexed")

    files_info = []
    progress_tracker = None
    skipped_count = 0
    
    try:
        # Collect all valid files
        all_files = []
        for item_path in path.rglob('*'):
            if not item_path.is_file() or item_path.name in excluded_files:
                continue
            
            try:
                relative_path = item_path.relative_to(path)
                if len(relative_path.parts) > 2 and relative_path.parts[0] in category_folders:
                    continue
                folder_name = relative_path.parts[0] if len(relative_path.parts) > 1 and relative_path.parts[0] in category_folders else '~'
                all_files.append((item_path, folder_name))
            except ValueError:
                continue
        
        if show_progress and logger.isEnabledFor(logging.INFO):
            try:
                from progress_tracker import create_progress_tracker
                progress_tracker = create_progress_tracker(len(all_files), "Scanning files")
            except ImportError:
                pass
        
        # Process files
        for item_path, folder_name in all_files:
            try:
                file_key = f"{folder_name}/{item_path.name}"
                current_timestamp = get_file_timestamp(str(item_path))
                
                # Incremental scan: reuse SHA1 if file unchanged
                sha1 = None
                if calculate_sha1_enabled:
                    if incremental and file_key in existing_index:
                        existing = existing_index[file_key]
                        # File unchanged if timestamp matches
                        if existing.get("timestamp") == current_timestamp and existing.get("sha1"):
                            sha1 = existing["sha1"]
                            skipped_count += 1
                        else:
                            sha1 = calculate_sha1(str(item_path), max_size_mb=max_file_size_mb)
                    else:
                        sha1 = calculate_sha1(str(item_path), max_size_mb=max_file_size_mb)
                
                files_info.append({
                    "root_dir": "~",
                    "folder_name": folder_name,
                    "filename": item_path.name,
                    "full_path": str(item_path),
                    "sha1": sha1,
                    "timestamp": current_timestamp,
                })
            except Exception as e:
                logger.error(f"Error creating file info for {item_path}: {e}")
            
            if progress_tracker:
                progress_tracker.update(1, item_path.name)
        
        if progress_tracker:
            progress_tracker.finish(f"Scanned {len(files_info)} files")

    except PermissionError:
        logger.error(f"Permission denied accessing: {path}")
        return []
    
    if incremental and skipped_count > 0:
        logger.info(f"Incremental scan: {skipped_count} unchanged files skipped SHA1 calculation")
    logger.info(f"Scanned {len(files_info)} files in {path}")
    return files_info


def update_csv_data(existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]], 
                    excluded_files: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Update CSV data with SHA1-based deduplication."""
    logger = logging.getLogger(__name__)
    excluded_files = excluded_files or ["desktop.ini", "Thumbs.db", ".DS_Store"]
    
    def get_key(item):
        sha1 = item.get("sha1")
        if not sha1 or sha1 == "SKIPPED_TOO_LARGE":
            return f"PATH:{item['folder_name']}/{item['filename']}"
        return sha1
    
    # Build index from existing data
    sha1_index: Dict[str, List[Dict[str, Any]]] = {}
    for item in existing_data:
        if item["filename"] not in excluded_files:
            key = get_key(item)
            sha1_index.setdefault(key, []).append(item)
    
    # Process new data
    updated_data = []
    processed_keys = set()
    
    for new_item in new_data:
        if new_item["filename"] in excluded_files:
            continue
        
        key = get_key(new_item)
        if key in processed_keys:
            continue
        
        if key in sha1_index:
            # Keep most recent version
            most_recent = new_item
            for existing in sha1_index[key]:
                if existing["timestamp"] > most_recent["timestamp"]:
                    most_recent = existing
            updated_data.append(most_recent)
        else:
            updated_data.append(new_item)
        
        processed_keys.add(key)
    
    logger.info(f"Updated data: {len(updated_data)} unique files")
    return updated_data


def save_to_csv(data: List[Dict[str, Any]], csv_path: Optional[str] = None) -> bool:
    """Save data to CSV file."""
    logger = logging.getLogger(__name__)
    from config_manager import get_config
    downloads_path = Path(get_config().get_downloads_path())

    if csv_path is None:
        csv_file = downloads_path / "results.csv"
    else:
        csv_file = Path(csv_path) if Path(csv_path).is_absolute() else downloads_path / csv_path

    try:
        with csv_file.open("w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["path", "rel_path", "folder_name", "filename", "sha1sum", "timestamp", "mtime_iso"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            rows = []
            for item in data:
                folder_name = item["folder_name"]
                filename = item['filename']
                timestamp = item.get('timestamp', '')
                
                if folder_name == "~":
                    path_str, rel_path = f"~\\{filename}", filename
                else:
                    path_str, rel_path = f"~\\{folder_name}\\{filename}", f"{folder_name}/{filename}"
                
                legacy_timestamp = timestamp[:8].replace('-', '/')[2:] if timestamp else ''
                
                rows.append({
                    "path": path_str, "rel_path": rel_path, "folder_name": folder_name,
                    "filename": filename, "sha1sum": item.get("sha1", ""),
                    "timestamp": legacy_timestamp, "mtime_iso": timestamp
                })
            
            writer.writerows(rows)
        
        logger.info(f"Data saved to {csv_file} ({len(data)} records)")
        return True
        
    except PermissionError:
        logger.error(f"Permission denied writing to: {csv_file}")
        return False
    except Exception as e:
        logger.error(f"Error saving CSV file: {e}")
        return False


def load_from_csv(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load data from CSV file with backward compatibility."""
    logger = logging.getLogger(__name__)
    from config_manager import get_config
    downloads_path = Path(get_config().get_downloads_path())

    csv_file = Path(csv_path) if csv_path else downloads_path / "results.csv"

    if not csv_file.exists():
        logger.info(f"CSV file not found: {csv_file}")
        return []

    data = []
    downloads_path_str = str(downloads_path)
    
    try:
        with csv_file.open("r", newline="", encoding="utf-8") as csvfile:
            for row in csv.DictReader(csvfile):
                if "folder_name" in row and "filename" in row:
                    folder_name, filename = row["folder_name"], row["filename"]
                    rel_path = row.get("rel_path", "")
                else:
                    # Legacy format
                    row_path = row["path"]
                    if row_path.startswith("~\\"):
                        parts = row_path[2:].split("\\")
                        folder_name = "~" if len(parts) == 1 else parts[0]
                        filename = parts[0] if len(parts) == 1 else parts[1]
                        rel_path = filename if folder_name == "~" else f"{folder_name}/{filename}"
                    else:
                        folder_name, filename, rel_path = "~", row_path, row_path

                full_path = f"{downloads_path_str}\\{filename}" if folder_name == "~" else f"{downloads_path_str}\\{folder_name}\\{filename}"
                
                data.append({
                    "root_dir": "~", "folder_name": folder_name, "filename": filename,
                    "full_path": full_path, "rel_path": rel_path,
                    "sha1": row.get("sha1sum", ""),
                    "timestamp": row.get("mtime_iso") or row.get("timestamp", ""),
                })
        
        logger.info(f"Loaded {len(data)} records from {csv_file}")
        
    except PermissionError:
        logger.error(f"Permission denied reading: {csv_file}")
    except Exception as e:
        logger.error(f"Error loading CSV file: {e}")
    
    return data


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    from config_manager import get_config
    return {
        "platform": "Windows",
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "downloads_path": get_config().get_downloads_path(),
    }
