#!/usr/bin/env python3
"""
Configuration management for Downloads Monitor
Handles loading and saving configuration from config.json
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manage application configuration"""

    DEFAULT_CONFIG = {
        "downloads_path": None,
        "csv_path": "results.csv",
        "monitoring": {
            "interval_seconds": 60,
            "enable_extensions": True,
            "calculate_sha1": True
        },
        "organization": {
            "auto_organize": True,
            "categories": {
                "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
                "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".csv", ".xls", ".xlsx", ".ppt", ".pptx"],
                "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
                "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]
            },
            "excluded_files": ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"]
        },
        "performance": {
            "max_file_size_for_sha1_mb": 500,
            "chunk_size_bytes": 8192,
            "enable_multithreading": False
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "console": True
        }
    }

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_with_defaults(config)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to ensure all keys exist"""
        def merge_dict(default: Dict, custom: Dict) -> Dict:
            result = default.copy()
            for key, value in custom.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_dict(self.DEFAULT_CONFIG, config)

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration to save (uses current config if None)
            
        Returns:
            True if successful, False otherwise
        """
        if config is None:
            config = self.config
            
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config to {self.config_path}: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path
        
        Args:
            key_path: Dot-separated path (e.g., "monitoring.interval_seconds")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value by dot-separated key path
        
        Args:
            key_path: Dot-separated path (e.g., "monitoring.interval_seconds")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value

    def get_downloads_path(self) -> str:
        """Get Downloads folder path (from config or system default)"""
        config_path = self.get("downloads_path")
        if config_path and os.path.exists(config_path):
            return config_path
        
        # Use Windows default Downloads folder
        return os.path.join(os.path.expanduser("~"), "Downloads")

    def get_csv_path(self) -> str:
        """Get CSV file path (absolute or relative to Downloads folder)"""
        csv_path = self.get("csv_path", "results.csv")
        
        if os.path.isabs(csv_path):
            return csv_path
        else:
            # Relative to Downloads folder
            return os.path.join(self.get_downloads_path(), csv_path)

    def get_excluded_files(self) -> list:
        """Get list of files to exclude from monitoring"""
        return self.get("organization.excluded_files", [])

    def get_categories(self) -> Dict[str, list]:
        """Get file organization categories"""
        return self.get("organization.categories", {})

    def should_calculate_sha1(self, file_size_bytes: int) -> bool:
        """
        Check if SHA1 should be calculated for a file based on size
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            True if SHA1 should be calculated
        """
        if not self.get("monitoring.calculate_sha1", True):
            return False
            
        max_size_mb = self.get("performance.max_file_size_for_sha1_mb", 500)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        return file_size_bytes <= max_size_bytes


# Global config instance
_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reload_config() -> ConfigManager:
    """Reload configuration from file"""
    global _config_instance
    _config_instance = ConfigManager()
    return _config_instance
