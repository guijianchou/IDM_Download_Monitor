#!/usr/bin/env python3
"""Duplicate file detection module"""

import logging
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class DuplicateDetector:
    """Detect and manage duplicate files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.duplicates: Dict[str, List[Dict[str, Any]]] = {}
        self.total_duplicates = 0
        self.wasted_space = 0
    
    def find_duplicates(self, files_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        self.duplicates.clear()
        self.total_duplicates = 0
        self.wasted_space = 0
        
        hash_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        for file_info in files_data:
            sha1 = file_info.get("sha1")
            if sha1 and sha1 != "SKIPPED_TOO_LARGE":
                hash_groups[sha1].append(file_info)
        
        for sha1, files in hash_groups.items():
            if len(files) > 1:
                self.duplicates[sha1] = files
                self.total_duplicates += len(files) - 1
                
                if files[0].get("full_path"):
                    try:
                        file_size = Path(files[0]["full_path"]).stat().st_size
                        self.wasted_space += file_size * (len(files) - 1)
                    except (OSError, FileNotFoundError):
                        pass
        
        return self.duplicates
    
    def display_duplicates(self, max_groups: int = 10) -> None:
        if not self.duplicates:
            self.logger.info("=== Duplicate Detection ===")
            self.logger.info("No duplicate files found")
            return
        
        self.logger.info("=== Duplicate Detection ===")
        self.logger.info(f"Duplicate groups: {len(self.duplicates)}, Total duplicates: {self.total_duplicates}")
        self.logger.info(f"Wasted space: {self.wasted_space / (1024 * 1024):.1f} MB")
        
        self.logger.info("Top duplicate groups:")
        sorted_groups = sorted(self.duplicates.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (sha1, files) in enumerate(sorted_groups[:max_groups]):
            self.logger.info(f"  Group {i+1} ({len(files)} files):")
            for f in files:
                self.logger.info(f"    {f.get('folder_name', '~')}/{f.get('filename', 'unknown')}")
    
    def suggest_cleanup(self) -> List[Dict[str, Any]]:
        suggestions = []
        
        for sha1, files in self.duplicates.items():
            if len(files) <= 1:
                continue
            
            # Prefer files in organized folders over root
            sorted_files = sorted(files, key=lambda f: 0 if f.get("folder_name") == "~" else 1, reverse=True)
            
            suggestions.append({
                "action": "keep",
                "file": sorted_files[0],
                "reason": f"Best location: {sorted_files[0].get('folder_name', '~')}"
            })
            
            for f in sorted_files[1:]:
                suggestions.append({"action": "delete", "file": f, "reason": "Duplicate file"})
        
        return suggestions


def create_duplicate_detector() -> DuplicateDetector:
    return DuplicateDetector()
