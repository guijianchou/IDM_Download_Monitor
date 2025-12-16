#!/usr/bin/env python3
"""File organizer module for Windows Downloads folder"""

import fnmatch
import logging
from pathlib import Path
from typing import Dict, List, Optional


class FileOrganizer:
    """Organize files in Downloads folder into categorized subdirectories."""

    DEFAULT_CATEGORIES = {
        "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".csv", ".xls", ".xlsx", ".ppt", ".pptx", ".epub", ".mobi", ".azw", ".azw3", ".py", ".js", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sql", ".sh", ".php", ".java", ".cpp", ".c", ".h"],
        "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif", ".ttf", ".otf", ".woff", ".woff2", ".eot"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".torrent"],
        "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]
    }
    DEFAULT_EXCLUDED = ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"]

    def __init__(self, downloads_path: str, category_folders: Optional[Dict[str, List[str]]] = None,
                 excluded_files: Optional[List[str]] = None, smart_rules: Optional[List[Dict[str, str]]] = None):
        self.downloads_path = Path(downloads_path)
        self.logger = logging.getLogger(__name__)
        self.category_folders = category_folders or self.DEFAULT_CATEGORIES
        self.excluded_files = excluded_files or self.DEFAULT_EXCLUDED
        self.smart_rules = smart_rules or []
        
        # Build extension to category mapping
        self._ext_to_category = {}
        for category, extensions in self.category_folders.items():
            for ext in extensions:
                self._ext_to_category[ext] = category
    
    def _match_smart_rules(self, filename: str) -> Optional[str]:
        """Match filename against smart rules (pattern-based classification)"""
        filename_lower = filename.lower()
        for rule in self.smart_rules:
            pattern = rule.get("pattern", "").lower()
            category = rule.get("category")
            if pattern and category and category in self.category_folders:
                if fnmatch.fnmatch(filename_lower, pattern):
                    self.logger.debug(f"Smart rule matched: '{filename}' -> {category} (pattern: {pattern})")
                    return category
        return None

    def organize_files(self, dry_run: bool = False) -> Dict[str, int]:
        self.logger.info("Starting file organization...")
        stats = {"total_files": 0, "organized": 0, "skipped": 0, "errors": 0}
        
        if not dry_run:
            for folder_name in self.category_folders:
                folder_path = self.downloads_path / folder_name
                if not folder_path.exists():
                    try:
                        folder_path.mkdir(parents=True, exist_ok=True)
                        self.logger.info(f"Created folder: {folder_name}")
                    except Exception as e:
                        self.logger.error(f"Failed to create folder {folder_name}: {e}")
        
        try:
            files_to_organize = [f for f in self.downloads_path.iterdir() 
                                 if f.is_file() and f.name not in self.excluded_files]
        except PermissionError:
            self.logger.error(f"Permission denied accessing: {self.downloads_path}")
            return stats
        
        stats["total_files"] = len(files_to_organize)
        
        if not files_to_organize:
            self.logger.info("No files to organize in root directory")
            return stats
        
        self.logger.info(f"Found {len(files_to_organize)} files to organize")
        
        for source_path in files_to_organize:
            # 优先使用智能规则匹配，其次使用扩展名匹配
            category = self._match_smart_rules(source_path.name) or self._ext_to_category.get(source_path.suffix.lower())
            
            if category:
                dest_folder = self.downloads_path / category
                
                # Security check
                if not dest_folder.resolve().is_relative_to(self.downloads_path.resolve()):
                    self.logger.error(f"Destination outside downloads path. Skipping '{source_path.name}'.")
                    stats["errors"] += 1
                    continue

                dest_path = dest_folder / source_path.name
                
                # Handle filename conflicts
                if dest_path.exists():
                    counter = 1
                    while dest_path.exists():
                        dest_path = dest_folder / f"{source_path.stem}_{counter}{source_path.suffix}"
                        counter += 1
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would move '{source_path.name}' to '{category}/'")
                    stats["organized"] += 1
                else:
                    try:
                        source_path.rename(dest_path)
                        self.logger.info(f"Moved '{source_path.name}' to '{category}/'")
                        stats["organized"] += 1
                    except PermissionError:
                        self.logger.error(f"Permission denied moving '{source_path.name}'")
                        stats["errors"] += 1
                    except Exception as e:
                        self.logger.error(f"Error moving '{source_path.name}': {e}")
                        stats["errors"] += 1
            else:
                self.logger.debug(f"No category for '{source_path.name}' - leaving in root")
                stats["skipped"] += 1
        
        self.logger.info(f"Organization completed: {stats['organized']} organized, {stats['skipped']} skipped, {stats['errors']} errors")
        return stats


def organize_downloads_folder(downloads_path: str, category_folders: Optional[Dict[str, List[str]]] = None,
                              excluded_files: Optional[List[str]] = None, smart_rules: Optional[List[Dict[str, str]]] = None,
                              dry_run: bool = False) -> Dict[str, int]:
    organizer = FileOrganizer(downloads_path, category_folders, excluded_files, smart_rules)
    return organizer.organize_files(dry_run=dry_run)
