#!/usr/bin/env python3
"""
File organizer module for Windows Downloads folder
Automatically categorizes and organizes files into folders
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional


class FileOrganizer:
    """Organize files in Downloads folder into categorized subdirectories"""

    def __init__(
        self,
        downloads_path: str,
        category_folders: Optional[Dict[str, List[str]]] = None,
        excluded_files: Optional[List[str]] = None
    ):
        """
        Initialize file organizer
        
        Args:
            downloads_path: Path to Downloads folder
            category_folders: Dictionary of category names to file extensions
            excluded_files: List of filenames to exclude from organization
        """
        self.downloads_path = downloads_path
        self.logger = logging.getLogger(__name__)
        
        if category_folders is None:
            self.category_folders = {
                "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
                "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".csv", ".xls", ".xlsx", ".ppt", ".pptx"],
                "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif"],
                "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
                "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            }
        else:
            self.category_folders = category_folders
        
        if excluded_files is None:
            self.excluded_files = ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"]
        else:
            self.excluded_files = excluded_files

    def create_category_folders(self) -> None:
        """Create category folders if they don't exist"""
        for folder_name in self.category_folders.keys():
            folder_path = os.path.join(self.downloads_path, folder_name)
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                    self.logger.info(f"Created folder: {folder_name}")
                except Exception as e:
                    self.logger.error(f"Failed to create folder {folder_name}: {e}")

    def get_file_category(self, filename: str) -> Optional[str]:
        """
        Determine which category a file belongs to based on its extension
        
        Args:
            filename: Name of the file
        
        Returns:
            Category name, or None if no category found
        """
        file_ext = Path(filename).suffix.lower()
        
        for category, extensions in self.category_folders.items():
            if file_ext in extensions:
                return category
        
        return None

    def organize_files(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Organize files in Downloads root directory into category folders
        
        Args:
            dry_run: If True, only simulate organization without moving files
        
        Returns:
            Dictionary with organization statistics
        """
        self.logger.info("Starting file organization...")
        
        stats = {
            "total_files": 0,
            "organized": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Create category folders
        if not dry_run:
            self.create_category_folders()
        
        # Get files in root directory
        try:
            items = os.listdir(self.downloads_path)
        except PermissionError:
            self.logger.error(f"Permission denied accessing: {self.downloads_path}")
            return stats
        
        files_to_organize = []
        for item in items:
            item_path = os.path.join(self.downloads_path, item)
            
            # Skip directories and excluded files
            if os.path.isdir(item_path) or item in self.excluded_files:
                continue
            
            # Skip category folders
            if item in self.category_folders.keys():
                continue
            
            files_to_organize.append(item)
        
        stats["total_files"] = len(files_to_organize)
        
        if not files_to_organize:
            self.logger.info("No files to organize in root directory")
            return stats
        
        self.logger.info(f"Found {len(files_to_organize)} files to organize")
        
        # Organize each file
        for filename in files_to_organize:
            category = self.get_file_category(filename)
            
            if category:
                source_path = os.path.join(self.downloads_path, filename)
                dest_folder = os.path.join(self.downloads_path, category)
                dest_path = os.path.join(dest_folder, filename)
                
                # Check if destination file already exists
                if os.path.exists(dest_path):
                    # Generate unique filename
                    base_name = Path(filename).stem
                    extension = Path(filename).suffix
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base_name}_{counter}{extension}"
                        dest_path = os.path.join(dest_folder, new_filename)
                        counter += 1
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would move '{filename}' to '{category}/'")
                    stats["organized"] += 1
                else:
                    try:
                        shutil.move(source_path, dest_path)
                        self.logger.info(f"Moved '{filename}' to '{category}/'")
                        stats["organized"] += 1
                    except PermissionError:
                        self.logger.error(f"Permission denied moving '{filename}'")
                        stats["errors"] += 1
                    except Exception as e:
                        self.logger.error(f"Error moving '{filename}': {e}")
                        stats["errors"] += 1
            else:
                self.logger.debug(f"No category for '{filename}' - leaving in root")
                stats["skipped"] += 1
        
        self.logger.info(f"Organization completed: {stats['organized']} organized, {stats['skipped']} skipped, {stats['errors']} errors")
        return stats

    def get_organized_file_paths(self):
        """Get all file paths after organization for monitoring"""
        all_files = []

        # Scan root directory (remaining unorganized files)
        for item in os.listdir(self.downloads_path):
            item_path = os.path.join(self.downloads_path, item)

            if os.path.isfile(item_path) and item not in self.excluded_files:
                all_files.append({"path": item_path, "folder": "~", "filename": item})

        # Scan category folders
        for category in self.category_folders.keys():
            category_path = os.path.join(self.downloads_path, category)
            if os.path.exists(category_path):
                for item in os.listdir(category_path):
                    item_path = os.path.join(category_path, item)

                    if os.path.isfile(item_path):
                        all_files.append({"path": item_path, "folder": category, "filename": item})

        return all_files


def organize_downloads_folder(
    downloads_path: str,
    category_folders: Optional[Dict[str, List[str]]] = None,
    excluded_files: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Convenience function to organize Downloads folder
    
    Args:
        downloads_path: Path to Downloads folder
        category_folders: Dictionary of category names to file extensions
        excluded_files: List of filenames to exclude
        dry_run: If True, only simulate organization
    
    Returns:
        Dictionary with organization statistics
    """
    organizer = FileOrganizer(downloads_path, category_folders, excluded_files)
    return organizer.organize_files(dry_run=dry_run)
