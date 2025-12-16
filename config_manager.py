#!/usr/bin/env python3
"""Configuration management for Downloads Monitor"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigManager:
    """Manage application configuration"""

    DEFAULT_CONFIG = {
        "downloads_path": None,
        "csv_path": "results.csv",
        "monitoring": {
            "interval_seconds": 60,
            "enable_extensions": True,
            "calculate_sha1": True,
            "incremental_scan": True
        },
        "organization": {
            "auto_organize": True,
            "categories": {
                "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".csv", ".xls", ".xlsx", ".ppt", ".pptx", ".epub", ".mobi", ".azw", ".azw3", ".py", ".js", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sql", ".sh", ".php", ".java", ".cpp", ".c", ".h"],
                "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif", ".ttf", ".otf", ".woff", ".woff2", ".eot"],
                "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
                "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".torrent"],
                "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]
            },
            "excluded_files": ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"],
            "smart_rules": [
                {"pattern": "screenshot*", "category": "Pictures"},
                {"pattern": "Screen Shot*", "category": "Pictures"},
                {"pattern": "IMG_*", "category": "Pictures"},
                {"pattern": "DSC_*", "category": "Pictures"},
                {"pattern": "wallpaper*", "category": "Pictures"},
                {"pattern": "*setup*", "category": "Programs"},
                {"pattern": "*installer*", "category": "Programs"},
                {"pattern": "*portable*", "category": "Programs"}
            ]
        },
        "performance": {"max_file_size_for_sha1_mb": 500, "chunk_size_bytes": 32768},
        "logging": {"level": "INFO", "file": None, "console": True}
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config_path = Path(self.config_path)
        if config_path.exists():
            try:
                with config_path.open('r', encoding='utf-8') as f:
                    config = json.load(f)
                merged = self._merge_with_defaults(config)
                errors = self._validate_config(merged)
                if errors:
                    self.logger.warning("Configuration validation errors:")
                    for error in errors:
                        self.logger.warning(f"  - {error}")
                return merged
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        def merge(default: Dict, custom: Dict) -> Dict:
            result = default.copy()
            for key, value in custom.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge(result[key], value)
                else:
                    result[key] = value
            return result
        return merge(self.DEFAULT_CONFIG, config)

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        try:
            with Path(self.config_path).open('w', encoding='utf-8') as f:
                json.dump(config or self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            config = config.setdefault(key, {})
        config[keys[-1]] = value

    def get_downloads_path(self) -> str:
        config_path = self.get("downloads_path")
        if config_path and Path(config_path).exists():
            return config_path
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            downloads_path, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
            winreg.CloseKey(key)
            return downloads_path
        except (ImportError, FileNotFoundError, OSError):
            return str(Path.home() / "Downloads")

    def get_csv_path(self) -> str:
        csv_path = Path(self.get("csv_path", "results.csv"))
        return str(csv_path) if csv_path.is_absolute() else str(Path(self.get_downloads_path()) / csv_path)

    def get_excluded_files(self) -> list:
        return self.get("organization.excluded_files", [])

    def get_categories(self) -> Dict[str, list]:
        return self.get("organization.categories", {})

    def get_smart_rules(self) -> List[Dict[str, str]]:
        return self.get("organization.smart_rules", [])

    def _validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        try:
            all_extensions = []
            for category, extensions in config.get("organization", {}).get("categories", {}).items():
                for ext in extensions:
                    if ext in all_extensions:
                        errors.append(f"Duplicate extension '{ext}' in multiple categories")
                    all_extensions.append(ext)
            perf = config.get("performance", {})
            if perf.get("max_file_size_for_sha1_mb", 500) < 1:
                errors.append("max_file_size_for_sha1_mb must be at least 1")
            if perf.get("chunk_size_bytes", 32768) < 1024:
                errors.append("chunk_size_bytes should be at least 1024")
            if config.get("monitoring", {}).get("interval_seconds", 60) < 5:
                errors.append("interval_seconds should be at least 5")
            downloads_path = config.get("downloads_path")
            if downloads_path and not Path(downloads_path).exists():
                errors.append(f"downloads_path does not exist: {downloads_path}")
        except Exception as e:
            errors.append(f"Validation error: {e}")
        return errors


_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


def reload_config() -> ConfigManager:
    global _config_instance
    _config_instance = ConfigManager()
    return _config_instance
