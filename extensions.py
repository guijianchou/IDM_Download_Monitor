#!/usr/bin/env python3
"""
Extensions module for Downloads folder monitoring tool
This module demonstrates how to add new functionality in a modular way
"""

import os
import json
from datetime import datetime
from pathlib import Path


class FileTypeAnalyzer:
    """Analyze file types in Downloads folder"""

    def __init__(self):
        self.file_types = {}
        self.total_files = 0

    def analyze_files(self, files_data):
        """Analyze file types from monitoring data"""
        self.file_types.clear()
        self.total_files = len(files_data)

        for file_info in files_data:
            filename = file_info.get("filename", "")
            if filename:
                file_ext = self._get_file_extension(filename)
                if file_ext not in self.file_types:
                    self.file_types[file_ext] = 0
                self.file_types[file_ext] += 1

    def _get_file_extension(self, filename):
        """Get file extension from filename"""
        return Path(filename).suffix.lower() or "No Extension"

    def get_statistics(self):
        """Get file type statistics"""
        return {
            "total_files": self.total_files,
            "file_types": self.file_types.copy(),
            "unique_extensions": len(self.file_types),
        }

    def display_statistics(self):
        """Display file type statistics"""
        print("\n=== File Type Analysis ===")
        print(f"Total files: {self.total_files}")
        print(f"Unique extensions: {len(self.file_types)}")

        if self.file_types:
            print("\nFile type distribution:")
            sorted_types = sorted(self.file_types.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_types[:10]:  # Show top 10
                percentage = (count / self.total_files) * 100
                print(f"  {ext}: {count} files ({percentage:.1f}%)")


class FileSizeAnalyzer:
    """Analyze file sizes in Downloads folder"""

    def __init__(self):
        self.size_categories = {
            "Tiny (< 1KB)": 0,
            "Small (1KB - 1MB)": 0,
            "Medium (1MB - 100MB)": 0,
            "Large (100MB - 1GB)": 0,
            "Huge (> 1GB)": 0,
        }
        self.total_size = 0

    def analyze_files(self, files_data):
        """Analyze file sizes from monitoring data"""
        # Reset counters
        for category in self.size_categories:
            self.size_categories[category] = 0
        self.total_size = 0

        for file_info in files_data:
            file_path = file_info.get("full_path", "")
            if file_path and os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                    self.total_size += file_size
                    self._categorize_file_size(file_size)
                except OSError:
                    continue

    def _categorize_file_size(self, size_bytes):
        """Categorize file by size"""
        if size_bytes < 1024:  # < 1KB
            self.size_categories["Tiny (< 1KB)"] += 1
        elif size_bytes < 1024 * 1024:  # < 1MB
            self.size_categories["Small (1MB - 1MB)"] += 1
        elif size_bytes < 100 * 1024 * 1024:  # < 100MB
            self.size_categories["Medium (1MB - 100MB)"] += 1
        elif size_bytes < 1024 * 1024 * 1024:  # < 1GB
            self.size_categories["Large (100MB - 1GB)"] += 1
        else:  # >= 1GB
            self.size_categories["Huge (> 1GB)"] += 1

    def get_statistics(self):
        """Get file size statistics"""
        return {
            "total_size": self.total_size,
            "size_categories": self.size_categories.copy(),
            "total_files": sum(self.size_categories.values()),
        }

    def display_statistics(self):
        """Display file size statistics"""
        print("\n=== File Size Analysis ===")
        print(f"Total size: {self._format_size(self.total_size)}")
        print(f"Total files: {sum(self.size_categories.values())}")

        print("\nSize distribution:")
        for category, count in self.size_categories.items():
            if count > 0:
                print(f"  {category}: {count} files")

    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class ChangeDetector:
    """Detect changes in Downloads folder"""

    def __init__(self):
        self.previous_data = {}
        self.changes = {"new_files": [], "modified_files": [], "deleted_files": []}

    def set_previous_data(self, files_data):
        """Set previous monitoring data for comparison"""
        self.previous_data.clear()
        for file_info in files_data:
            key = (file_info["root_dir"], file_info["folder_name"], file_info["filename"])
            self.previous_data[key] = file_info

    def detect_changes(self, current_data):
        """Detect changes between previous and current data"""
        self.changes = {"new_files": [], "modified_files": [], "deleted_files": []}

        current_keys = set()

        # Check current files
        for file_info in current_data:
            key = (file_info["root_dir"], file_info["folder_name"], file_info["filename"])
            current_keys.add(key)

            if key in self.previous_data:
                # File exists in both, check for modifications
                prev_info = self.previous_data[key]
                if file_info["sha1"] != prev_info["sha1"] or file_info["timestamp"] != prev_info["timestamp"]:
                    self.changes["modified_files"].append({"file": file_info, "previous": prev_info})
            else:
                # New file
                self.changes["new_files"].append(file_info)

        # Check for deleted files
        for key in self.previous_data:
            if key not in current_keys:
                self.changes["deleted_files"].append(self.previous_data[key])

    def get_changes_summary(self):
        """Get summary of detected changes"""
        return {
            "new_files_count": len(self.changes["new_files"]),
            "modified_files_count": len(self.changes["modified_files"]),
            "deleted_files_count": len(self.changes["deleted_files"]),
            "total_changes": (
                len(self.changes["new_files"])
                + len(self.changes["modified_files"])
                + len(self.changes["deleted_files"])
            ),
        }

    def display_changes(self):
        """Display detected changes"""
        summary = self.get_changes_summary()

        print("\n=== Change Detection ===")
        print(f"New files: {summary['new_files_count']}")
        print(f"Modified files: {summary['modified_files_count']}")
        print(f"Deleted files: {summary['deleted_files_count']}")
        print(f"Total changes: {summary['total_changes']}")

        if summary["total_changes"] > 0:
            if self.changes["new_files"]:
                print("\nNew files:")
                for file_info in self.changes["new_files"][:5]:  # Show first 5
                    print(f"  + {file_info['filename']}")

            if self.changes["modified_files"]:
                print("\nModified files:")
                for change in self.changes["modified_files"][:5]:  # Show first 5
                    file_info = change["file"]
                    print(f"  * {file_info['filename']}")

            if self.changes["deleted_files"]:
                print("\nDeleted files:")
                for file_info in self.changes["deleted_files"][:5]:  # Show first 5
                    print(f"  - {file_info['filename']}")


class ExtensionManager:
    """Manager for all extensions"""

    def __init__(self):
        self.extensions = {}
        self._register_default_extensions()

    def _register_default_extensions(self):
        """Register default extensions"""
        self.register_extension("file_type_analyzer", FileTypeAnalyzer())
        self.register_extension("file_size_analyzer", FileSizeAnalyzer())
        self.register_extension("change_detector", ChangeDetector())

    def register_extension(self, name, extension_instance):
        """Register a new extension"""
        self.extensions[name] = extension_instance

    def get_extension(self, name):
        """Get extension by name"""
        return self.extensions.get(name)

    def run_all_extensions(self, files_data, previous_data=None):
        """Run all registered extensions"""
        results = {}

        for name, extension in self.extensions.items():
            try:
                if hasattr(extension, "analyze_files"):
                    extension.analyze_files(files_data)

                if hasattr(extension, "set_previous_data") and previous_data:
                    extension.set_previous_data(previous_data)

                if hasattr(extension, "detect_changes"):
                    extension.detect_changes(files_data)

                results[name] = extension
            except Exception as e:
                print(f"Error running extension {name}: {e}")
                results[name] = None

        return results

    def display_all_results(self):
        """Display results from all extensions"""
        for name, extension in self.extensions.items():
            if extension and hasattr(extension, "display_statistics"):
                extension.display_statistics()
            elif extension and hasattr(extension, "display_changes"):
                extension.display_changes()


# Example usage functions
def create_extension_manager():
    """Create and return an extension manager instance"""
    return ExtensionManager()


def run_extensions_on_data(files_data, previous_data=None):
    """Run all extensions on the given data"""
    manager = create_extension_manager()
    results = manager.run_all_extensions(files_data, previous_data)
    manager.display_all_results()
    return results
