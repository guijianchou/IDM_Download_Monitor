#!/usr/bin/env python3
"""
Downloads folder monitoring main program
Monitor SHA1 and modification time of all files in Windows Downloads directory
Windows-only CLI version with configuration support
"""

import os
import sys
import time
import argparse
import logging
from typing import Optional, Dict, Any

from file_monitor import (
    scan_downloads_folder,
    load_from_csv,
    update_csv_data,
    save_to_csv,
    get_downloads_path,
    get_system_info,
)
from file_organizer import organize_downloads_folder
from config_manager import get_config, ConfigManager

# Import extensions (optional)
try:
    from extensions import create_extension_manager
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False


def setup_logging(config: ConfigManager) -> logging.Logger:
    """
    Configure logging for the application
    
    Args:
        config: Configuration manager instance
    
    Returns:
        Configured logger
    """
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file")
    console_enabled = config.get("logging.console", True)
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    # Simple format for console, detailed format for file
    console_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Console handler
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Failed to create log file: {e}")
    
    return logger


class DownloadsMonitor:
    """Main monitoring class for Downloads folder"""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Initialize Downloads monitor
        
        Args:
            config: Configuration manager (uses global config if None)
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        self.downloads_path = self.config.get_downloads_path()
        self.csv_path = self.config.get_csv_path()
        
        self.existing_data = []
        self.new_data = []
        self.updated_data = []
        
        self.enable_extensions = self.config.get("monitoring.enable_extensions", True) and EXTENSIONS_AVAILABLE
        self.extension_manager = None
        
        if self.enable_extensions:
            try:
                self.extension_manager = create_extension_manager()
                self.logger.info("Extensions loaded successfully")
            except Exception as e:
                self.logger.warning(f"Failed to load extensions: {e}")
                self.enable_extensions = False

    
    def initialize(self) -> bool:
        """Initialize the monitor with system information and paths"""
        self.logger.info("Initializing Downloads folder monitor...")
        
        # Display system information
        self._display_system_info()
        
        # Validate Downloads path
        if not self._validate_downloads_path():
            return False
        
        # Load existing data
        if not self._load_existing_data():
            return False
        
        self.logger.info("Initialization completed successfully")
        return True
    
    def _display_system_info(self) -> None:
        """Display system information"""
        self.logger.info("=== System Information ===")
        system_info = get_system_info()
        for key, value in system_info.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info(f"Extensions enabled: {self.enable_extensions}")
    
    def _validate_downloads_path(self) -> bool:
        """Validate Downloads folder path"""
        self.logger.info(f"Monitoring path: {self.downloads_path}")
        
        if not os.path.exists(self.downloads_path):
            self.logger.error(f"Downloads folder doesn't exist: {self.downloads_path}")
            self._show_troubleshooting()
            return False
        
        return True
    
    def _show_troubleshooting(self) -> None:
        """Show troubleshooting suggestions"""
        self.logger.info("Troubleshooting suggestions:")
        self.logger.info("1. Ensure Downloads folder exists and is accessible")
        self.logger.info("2. Check file permissions for the Downloads folder")
        self.logger.info("3. Verify Python has read/write access to the folder")
    
    def _load_existing_data(self) -> bool:
        """Load existing CSV data"""
        self.logger.info("Loading existing data...")
        self.existing_data = load_from_csv(self.csv_path)
        self.logger.info(f"Existing records: {len(self.existing_data)}")
        return True

    
    def scan_folder(self) -> bool:
        """Scan Downloads folder for files"""
        self.logger.info("Scanning Downloads folder...")
        
        # Get configuration
        excluded_files = self.config.get_excluded_files()
        categories = list(self.config.get_categories().keys())
        calculate_sha1 = self.config.get("monitoring.calculate_sha1", True)
        max_size_mb = self.config.get("performance.max_file_size_for_sha1_mb", 500)
        
        self.new_data = scan_downloads_folder(
            downloads_path=self.downloads_path,
            excluded_files=excluded_files,
            category_folders=categories,
            calculate_sha1_enabled=calculate_sha1,
            max_file_size_mb=max_size_mb if calculate_sha1 else None
        )
        
        self.logger.info(f"Files scanned: {len(self.new_data)}")
        
        if not self.new_data:
            self.logger.warning("No files scanned")
            return False
        
        return True
    
    def update_data(self) -> bool:
        """Update data with new scan results"""
        self.logger.info("Updating data...")
        excluded_files = self.config.get_excluded_files()
        self.updated_data = update_csv_data(self.existing_data, self.new_data, excluded_files)
        self.logger.info(f"Updated records: {len(self.updated_data)}")
        return True
    
    def save_data(self) -> bool:
        """Save updated data to CSV"""
        self.logger.info("Saving data to CSV...")
        return save_to_csv(self.updated_data, self.csv_path)
    
    def run_extensions(self) -> None:
        """Run extension analysis if available"""
        if not self.enable_extensions or not self.extension_manager:
            return
        
        self.logger.info("Running extensions...")
        try:
            self.extension_manager.run_all_extensions(self.updated_data, self.existing_data)
            self.extension_manager.display_all_results()
        except Exception as e:
            self.logger.error(f"Error running extensions: {e}")

    
    def display_statistics(self) -> None:
        """Display monitoring statistics"""
        self.logger.info("=== Statistics ===")
        self.logger.info(f"Downloads path: {self.downloads_path}")
        self.logger.info(f"Total files: {len(self.updated_data)}")
        
        # Group statistics by folder
        folder_stats = self._calculate_folder_statistics()
        self._display_folder_statistics(folder_stats)
    
    def _calculate_folder_statistics(self) -> Dict[str, int]:
        """Calculate folder distribution statistics"""
        folder_stats = {}
        for item in self.updated_data:
            folder = item["folder_name"] if item["folder_name"] else "Root Directory"
            if folder not in folder_stats:
                folder_stats[folder] = 0
            folder_stats[folder] += 1
        return folder_stats
    
    def _display_folder_statistics(self, folder_stats: Dict[str, int]) -> None:
        """Display folder distribution statistics"""
        self.logger.info("By folder distribution:")
        for folder, count in sorted(folder_stats.items()):
            self.logger.info(f"  {folder}: {count} files")
    
    def run_monitoring_cycle(self) -> bool:
        """Run a complete monitoring cycle"""
        self.logger.info("Starting Downloads folder monitoring...")
        
        if not self.initialize():
            return False
        
        # Organize files into categories
        if self.config.get("organization.auto_organize", True):
            self.logger.info("=== File Organization Phase ===")
            categories = self.config.get_categories()
            excluded_files = self.config.get_excluded_files()
            
            stats = organize_downloads_folder(
                self.downloads_path,
                category_folders=categories,
                excluded_files=excluded_files
            )
            
            self.logger.info(f"Organization stats: {stats}")
        
        if not self.scan_folder():
            return False
        
        if not self.update_data():
            return False
        
        if not self.save_data():
            return False
        
        # Run extensions
        self.run_extensions()
        
        # Display statistics
        self.display_statistics()
        self.logger.info("Monitoring completed!")
        return True



class ContinuousMonitor:
    """Continuous monitoring class"""
    
    def __init__(self, monitor_instance: DownloadsMonitor, interval: int = 60):
        """
        Initialize continuous monitor
        
        Args:
            monitor_instance: DownloadsMonitor instance
            interval: Monitoring interval in seconds
        """
        self.monitor = monitor_instance
        self.interval = interval
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """Start continuous monitoring"""
        self.logger.info(f"Starting continuous monitoring, interval: {self.interval} seconds")
        self.logger.info("Press Ctrl+C to stop monitoring")
        
        self.running = True
        try:
            while self.running:
                self.logger.info(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
                self.monitor.run_monitoring_cycle()
                self.logger.info(f"Waiting {self.interval} seconds for next monitoring...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self) -> None:
        """Stop continuous monitoring"""
        self.running = False
        self.logger.info("Monitoring stopped")


def show_system_info() -> None:
    """Display detailed system information"""
    print("=== System Information ===")
    system_info = get_system_info()
    
    for key, value in system_info.items():
        print(f"{key}: {value}")


def run_extensions_only(config: ConfigManager) -> bool:
    """
    Run only extensions on existing data
    
    Args:
        config: Configuration manager
    
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    if not EXTENSIONS_AVAILABLE:
        logger.error("Extensions module not available")
        return False
    
    logger.info("Running extensions on existing data...")
    
    # Load existing data
    csv_path = config.get_csv_path()
    existing_data = load_from_csv(csv_path)
    
    if not existing_data:
        logger.error("No existing data found. Run monitoring first.")
        return False
    
    # Create and run extensions
    try:
        extension_manager = create_extension_manager()
        extension_manager.run_all_extensions(existing_data)
        extension_manager.display_all_results()
        return True
    except Exception as e:
        logger.error(f"Error running extensions: {e}")
        return False



def create_argument_parser() -> argparse.ArgumentParser:
    """Create and return command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Downloads folder monitoring tool - Windows-only version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                    # Execute monitoring once
  %(prog)s -c                 # Continuous monitoring, 60s interval  
  %(prog)s -c 30              # Continuous monitoring, 30s interval
  %(prog)s --info             # Show system information
  %(prog)s --no-ext           # Disable extensions
  %(prog)s --ext-only         # Run only extensions
  %(prog)s --dry-run          # Preview organization without moving files"""
    )
    
    parser.add_argument(
        "-c", "--continuous",
        nargs="?",
        const=60,
        type=int,
        metavar="SECONDS",
        help="Enable continuous monitoring with optional interval in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="Show system information"
    )
    
    parser.add_argument(
        "--no-ext",
        action="store_true",
        help="Disable extensions"
    )
    
    parser.add_argument(
        "--ext-only",
        action="store_true",
        help="Run only extensions (requires previous data)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview file organization without moving files"
    )
    
    parser.add_argument(
        "--downloads-path",
        type=str,
        help="Override Downloads folder path"
    )
    
    parser.add_argument(
        "--csv-path",
        type=str,
        help="Override CSV output file path"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level (overrides config)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Write logs to file (overrides config)"
    )
    
    return parser


def main() -> int:
    """
    Main function
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Set up proper encoding for console output
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Load configuration
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
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Handle different command modes
    try:
        if args.info:
            show_system_info()
            return 0
        
        elif args.ext_only:
            success = run_extensions_only(config)
            return 0 if success else 1
        
        elif args.continuous is not None:
            # Continuous monitoring mode
            interval = args.continuous
            logger.info(f"Starting continuous monitoring with {interval}s interval")
            monitor = DownloadsMonitor(config)
            continuous_monitor = ContinuousMonitor(monitor, interval)
            continuous_monitor.start()
            return 0
        
        else:
            # Default: execute monitoring once
            monitor = DownloadsMonitor(config)
            success = monitor.run_monitoring_cycle()
            return 0 if success else 1
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
