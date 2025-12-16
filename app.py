#!/usr/bin/env python3
"""Downloads folder monitoring main program - Windows-only CLI version"""

import time
import argparse
import logging
import platform
from pathlib import Path

from file_monitor import scan_downloads_folder, load_from_csv, update_csv_data, save_to_csv, get_system_info
from file_organizer import organize_downloads_folder
from config_manager import get_config, ConfigManager

try:
    from extensions import create_extension_manager
    from duplicate_detector import create_duplicate_detector
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False


def setup_logging(config: ConfigManager) -> logging.Logger:
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file")
    console_enabled = config.get("logging.console", True)
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()
    
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(console_handler)
    
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Failed to create log file: {e}")
    
    return logger


class DownloadsMonitor:
    """Main monitoring class for Downloads folder"""
    
    def __init__(self, config: ConfigManager = None):
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        self.downloads_path = self.config.get_downloads_path()
        self.csv_path = self.config.get_csv_path()
        self.existing_data = []
        self.new_data = []
        self.updated_data = []
        self.enable_extensions = self.config.get("monitoring.enable_extensions", True) and EXTENSIONS_AVAILABLE
        self.extension_manager = None
        self.duplicate_detector = None
        
        if self.enable_extensions:
            try:
                self.extension_manager = create_extension_manager()
                self.duplicate_detector = create_duplicate_detector()
                self.logger.info("Extensions loaded successfully")
            except Exception as e:
                self.logger.warning(f"Failed to load extensions: {e}")
                self.enable_extensions = False

    def initialize(self) -> bool:
        self.logger.info("Initializing Downloads folder monitor...")
        self._display_system_info()
        
        if not Path(self.downloads_path).exists():
            self.logger.error(f"Downloads folder doesn't exist: {self.downloads_path}")
            return False
        
        self.logger.info(f"Monitoring path: {self.downloads_path}")
        self.existing_data = load_from_csv(self.csv_path)
        self.logger.info(f"Existing records: {len(self.existing_data)}")
        return True
    
    def _display_system_info(self) -> None:
        self.logger.info("=== System Information ===")
        for key, value in {
            "platform": "Windows", "platform_version": platform.version(),
            "machine": platform.machine(), "hostname": platform.node(),
            "python_version": platform.python_version(), "downloads_path": self.downloads_path,
        }.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info(f"Extensions enabled: {self.enable_extensions}")
    
    def scan_folder(self) -> bool:
        self.logger.info("Scanning Downloads folder...")
        incremental = self.config.get("monitoring.incremental_scan", True)
        self.new_data = scan_downloads_folder(
            downloads_path=self.downloads_path,
            excluded_files=self.config.get_excluded_files(),
            category_folders=list(self.config.get_categories().keys()),
            calculate_sha1_enabled=self.config.get("monitoring.calculate_sha1", True),
            max_file_size_mb=self.config.get("performance.max_file_size_for_sha1_mb", 500),
            show_progress=self.logger.isEnabledFor(logging.INFO),
            existing_data=self.existing_data if incremental else None,
            incremental=incremental
        )
        self.logger.info(f"Files scanned: {len(self.new_data)}")
        return bool(self.new_data)
    
    def update_and_save(self) -> bool:
        self.logger.info("Updating data...")
        self.updated_data = update_csv_data(self.existing_data, self.new_data, self.config.get_excluded_files())
        self.logger.info(f"Updated records: {len(self.updated_data)}")
        self.logger.info("Saving data to CSV...")
        return save_to_csv(self.updated_data, self.csv_path)
    
    def run_extensions(self) -> None:
        if not self.enable_extensions or not self.extension_manager:
            return
        self.logger.info("Running extensions...")
        try:
            self.extension_manager.run_all_extensions(self.updated_data, self.existing_data)
            self.extension_manager.display_all_results()
            if self.duplicate_detector:
                self.duplicate_detector.find_duplicates(self.updated_data)
                self.duplicate_detector.display_duplicates()
        except Exception as e:
            self.logger.error(f"Error running extensions: {e}")
    
    def display_statistics(self) -> None:
        self.logger.info("=== Statistics ===")
        self.logger.info(f"Downloads path: {self.downloads_path}")
        self.logger.info(f"Total files: {len(self.updated_data)}")
        
        folder_stats = {}
        for item in self.updated_data:
            folder = item["folder_name"] if item["folder_name"] else "Root Directory"
            folder_stats[folder] = folder_stats.get(folder, 0) + 1
        
        self.logger.info("By folder distribution:")
        for folder, count in sorted(folder_stats.items()):
            self.logger.info(f"  {folder}: {count} files")
    
    def run_monitoring_cycle(self) -> bool:
        self.logger.info("Starting Downloads folder monitoring...")
        
        if not self.initialize():
            return False
        
        if self.config.get("organization.auto_organize", True):
            self.logger.info("=== File Organization Phase ===")
            stats = organize_downloads_folder(
                self.downloads_path,
                category_folders=self.config.get_categories(),
                excluded_files=self.config.get_excluded_files(),
                smart_rules=self.config.get_smart_rules()
            )
            self.logger.info(f"Organization stats: {stats}")
        
        if not self.scan_folder():
            self.logger.warning("No files scanned")
            return False
        
        if not self.update_and_save():
            return False
        
        self.run_extensions()
        self.display_statistics()
        self.logger.info("Monitoring completed!")
        return True


class ContinuousMonitor:
    """Continuous monitoring implementation"""
    
    def __init__(self, monitor: DownloadsMonitor, interval: int):
        self.monitor = monitor
        self.interval = interval
        self.logger = logging.getLogger(__name__)
        self.is_running = False
    
    def start(self) -> None:
        self.is_running = True
        self.logger.info(f"Starting continuous monitoring (interval: {self.interval}s)")
        
        try:
            while self.is_running:
                self.logger.info("Running monitoring cycle...")
                if not self.monitor.run_monitoring_cycle():
                    self.logger.warning("Monitoring cycle failed, continuing...")
                self.logger.info(f"Waiting {self.interval} seconds until next cycle...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.logger.info("Continuous monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in continuous monitoring: {e}")
        finally:
            self.is_running = False


def show_system_info() -> None:
    print("=== System Information ===")
    for key, value in get_system_info().items():
        print(f"{key}: {value}")


def show_cleanup_suggestions(config: ConfigManager) -> bool:
    logger = logging.getLogger(__name__)
    logger.info("Analyzing files for cleanup suggestions...")
    
    existing_data = load_from_csv(config.get_csv_path())
    if not existing_data:
        logger.error("No existing data found. Run monitoring first.")
        return False
    
    try:
        detector = create_duplicate_detector()
        duplicates = detector.find_duplicates(existing_data)
        
        if not duplicates:
            logger.info("No duplicate files found. Your Downloads folder is clean!")
            return True
        
        detector.display_duplicates()
        suggestions = detector.suggest_cleanup()
        
        logger.info("=== Cleanup Suggestions ===")
        delete_count = sum(1 for s in suggestions if s["action"] == "delete")
        keep_count = sum(1 for s in suggestions if s["action"] == "keep")
        
        logger.info(f"Files to keep: {keep_count}, Files to delete: {delete_count}")
        
        if delete_count > 0:
            logger.info("Files suggested for deletion:")
            for s in suggestions:
                if s["action"] == "delete":
                    f = s["file"]
                    logger.info(f"  {f.get('folder_name', '~')}/{f.get('filename', 'unknown')} - {s['reason']}")
        return True
    except Exception as e:
        logger.error(f"Error analyzing cleanup suggestions: {e}")
        return False


def run_extensions_only(config: ConfigManager) -> bool:
    logger = logging.getLogger(__name__)
    
    if not EXTENSIONS_AVAILABLE:
        logger.error("Extensions module not available")
        return False
    
    logger.info("Running extensions on existing data...")
    existing_data = load_from_csv(config.get_csv_path())
    
    if not existing_data:
        logger.error("No existing data found. Run monitoring first.")
        return False
    
    try:
        manager = create_extension_manager()
        manager.run_all_extensions(existing_data)
        manager.display_all_results()
        return True
    except Exception as e:
        logger.error(f"Error running extensions: {e}")
        return False


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Downloads folder monitoring tool - Windows-only version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                    # Execute monitoring once
  %(prog)s -c                 # Continuous monitoring, 60s interval  
  %(prog)s -c 30              # Continuous monitoring, 30s interval
  %(prog)s --info             # Show system information
  %(prog)s --cleanup          # Show cleanup suggestions"""
    )
    
    parser.add_argument("-c", "--continuous", nargs="?", const=60, type=int, metavar="SECONDS",
                        help="Enable continuous monitoring with optional interval (default: 60)")
    parser.add_argument("--dry-run", action="store_true", help="Preview organization without moving files")
    parser.add_argument("--no-ext", action="store_true", help="Disable extensions")
    parser.add_argument("--ext-only", action="store_true", help="Run only extensions")
    parser.add_argument("--downloads-path", type=str, help="Override Downloads folder path")
    parser.add_argument("--csv-path", type=str, help="Override CSV output file path")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Set logging level")
    parser.add_argument("--log-file", type=str, help="Write logs to file")
    parser.add_argument("--info", "-i", action="store_true", help="Show system information")
    parser.add_argument("--cleanup", action="store_true", help="Show cleanup suggestions")
    
    return parser


def main() -> int:
    parser = create_argument_parser()
    args = parser.parse_args()
    
    config = ConfigManager(args.config)
    
    # Override config with command line arguments
    if args.log_level:
        config.set("logging.level", args.log_level)
    if args.log_file:
        config.set("logging.file", args.log_file)
    if args.downloads_path:
        config.set("downloads_path", args.downloads_path)
    if args.csv_path:
        config.set("csv_path", args.csv_path)
    if args.no_ext:
        config.set("monitoring.enable_extensions", False)
    
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    try:
        if args.info:
            show_system_info()
            return 0
        elif args.ext_only:
            return 0 if run_extensions_only(config) else 1
        elif args.cleanup:
            return 0 if show_cleanup_suggestions(config) else 1
        elif args.continuous is not None:
            logger.info(f"Starting continuous monitoring with {args.continuous}s interval")
            monitor = DownloadsMonitor(config)
            ContinuousMonitor(monitor, args.continuous).start()
            return 0
        else:
            return 0 if DownloadsMonitor(config).run_monitoring_cycle() else 1
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    main()
