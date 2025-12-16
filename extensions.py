#!/usr/bin/env python3
"""Extensions module for Downloads folder monitoring tool"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class FileTypeAnalyzer:
    """Analyze file types in Downloads folder"""
    
    def __init__(self):
        self.file_types: Dict[str, int] = {}
        self.total_files: int = 0
        self.logger = logging.getLogger(__name__)
    
    def analyze_files(self, files_data: List[Dict[str, Any]]) -> None:
        self.file_types.clear()
        self.total_files = len(files_data)
        
        for file_info in files_data:
            filename = file_info.get("filename", "")
            if filename:
                ext = Path(filename).suffix.lower() or "No Extension"
                self.file_types[ext] = self.file_types.get(ext, 0) + 1
    
    def display_statistics(self) -> None:
        self.logger.info("=== File Type Analysis ===")
        self.logger.info(f"Total files: {self.total_files}, Unique extensions: {len(self.file_types)}")
        
        if self.file_types:
            self.logger.info("File type distribution:")
            sorted_types = sorted(self.file_types.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_types[:10]:
                percentage = (count / self.total_files) * 100
                self.logger.info(f"  {ext}: {count} files ({percentage:.1f}%)")


class FileSizeAnalyzer:
    """Analyze file sizes in Downloads folder"""
    
    SIZE_CATEGORIES = [
        ("Tiny (< 1KB)", 1024),
        ("Small (1KB - 1MB)", 1024 * 1024),
        ("Medium (1MB - 100MB)", 100 * 1024 * 1024),
        ("Large (100MB - 1GB)", 1024 * 1024 * 1024),
        ("Huge (> 1GB)", float('inf')),
    ]
    
    def __init__(self):
        self.size_counts: Dict[str, int] = {cat[0]: 0 for cat in self.SIZE_CATEGORIES}
        self.total_size: int = 0
        self.logger = logging.getLogger(__name__)

    def analyze_files(self, files_data: List[Dict[str, Any]]) -> None:
        for cat in self.size_counts:
            self.size_counts[cat] = 0
        self.total_size = 0

        for file_info in files_data:
            file_path = file_info.get("full_path")
            if not file_path:
                continue
            try:
                file_size = Path(file_path).stat().st_size
                self.total_size += file_size
                for cat_name, threshold in self.SIZE_CATEGORIES:
                    if file_size < threshold:
                        self.size_counts[cat_name] += 1
                        break
            except OSError:
                continue

    def display_statistics(self) -> None:
        self.logger.info("=== File Size Analysis ===")
        
        # Format size
        size = float(self.total_size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                size_str = f"{size:.1f} {unit}"
                break
            size /= 1024.0
        else:
            size_str = f"{size:.1f} PB"
        
        self.logger.info(f"Total size: {size_str}, Total files: {sum(self.size_counts.values())}")
        self.logger.info("Size distribution:")
        for category, count in self.size_counts.items():
            if count > 0:
                self.logger.info(f"  {category}: {count} files")


class ChangeDetector:
    """Detect changes in Downloads folder"""
    
    def __init__(self):
        self.previous_data: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self.changes: Dict[str, List[Any]] = {"new_files": [], "modified_files": [], "deleted_files": []}
        self.logger = logging.getLogger(__name__)

    def set_previous_data(self, files_data: List[Dict[str, Any]]) -> None:
        self.previous_data = {
            (f["root_dir"], f["folder_name"], f["filename"]): f for f in files_data
        }

    def detect_changes(self, current_data: List[Dict[str, Any]]) -> None:
        self.changes = {"new_files": [], "modified_files": [], "deleted_files": []}
        current_keys = set()

        for file_info in current_data:
            key = (file_info["root_dir"], file_info["folder_name"], file_info["filename"])
            current_keys.add(key)

            if key in self.previous_data:
                prev = self.previous_data[key]
                if file_info["sha1"] != prev["sha1"] or file_info["timestamp"] != prev["timestamp"]:
                    self.changes["modified_files"].append({"file": file_info, "previous": prev})
            else:
                self.changes["new_files"].append(file_info)

        for key in self.previous_data:
            if key not in current_keys:
                self.changes["deleted_files"].append(self.previous_data[key])

    def display_changes(self) -> None:
        new_count = len(self.changes["new_files"])
        mod_count = len(self.changes["modified_files"])
        del_count = len(self.changes["deleted_files"])
        total = new_count + mod_count + del_count
        
        self.logger.info("=== Change Detection ===")
        self.logger.info(f"New: {new_count}, Modified: {mod_count}, Deleted: {del_count}, Total: {total}")
        
        if total > 0:
            for label, key, prefix in [("New files:", "new_files", "+"), 
                                        ("Modified files:", "modified_files", "*"),
                                        ("Deleted files:", "deleted_files", "-")]:
                items = self.changes[key]
                if items:
                    self.logger.info(label)
                    for item in items[:5]:
                        f = item["file"] if isinstance(item, dict) and "file" in item else item
                        self.logger.info(f"  {prefix} {f['filename']}")


class ExtensionManager:
    """Manager for all extensions"""

    def __init__(self):
        self.extensions = {
            "file_type_analyzer": FileTypeAnalyzer(),
            "file_size_analyzer": FileSizeAnalyzer(),
            "change_detector": ChangeDetector(),
        }

    def run_all_extensions(self, files_data: List[Dict[str, Any]], previous_data: Optional[List[Dict[str, Any]]] = None) -> None:
        for name, ext in self.extensions.items():
            try:
                if hasattr(ext, "analyze_files"):
                    ext.analyze_files(files_data)
                if hasattr(ext, "set_previous_data") and previous_data:
                    ext.set_previous_data(previous_data)
                if hasattr(ext, "detect_changes"):
                    ext.detect_changes(files_data)
            except Exception as e:
                logging.getLogger(__name__).error(f"Error running extension {name}: {e}")

    def display_all_results(self) -> None:
        for ext in self.extensions.values():
            if hasattr(ext, "display_statistics"):
                ext.display_statistics()
            elif hasattr(ext, "display_changes"):
                ext.display_changes()


def create_extension_manager() -> ExtensionManager:
    return ExtensionManager()
