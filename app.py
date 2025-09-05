1#!/usr/bin/env python3
"""
Downloads folder monitoring main program
Monitor SHA1 and modification time of all files and folders in Windows Downloads directory
Supports both Windows native and WSL2 environments
"""

import os
import sys
import time
from file_monitor import (
    scan_downloads_folder,
    load_from_csv,
    update_csv_data,
    save_to_csv,
    get_downloads_path,
    get_system_info,
    is_wsl2,
)
from file_organizer import organize_downloads_folder

# Import extensions (optional)
try:
    from extensions import create_extension_manager

    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False


class DownloadsMonitor:
    """Main monitoring class for Downloads folder"""

    def __init__(self, csv_path="results.csv", enable_extensions=True):
        self.csv_path = csv_path
        self.downloads_path = None
        self.existing_data = []
        self.new_data = []
        self.updated_data = []
        self.enable_extensions = enable_extensions and EXTENSIONS_AVAILABLE
        self.extension_manager = None

        if self.enable_extensions:
            try:
                self.extension_manager = create_extension_manager()
                print("Extensions loaded successfully")
            except Exception as e:
                print(f"Warning: Failed to load extensions: {e}")
                self.enable_extensions = False

    def initialize(self):
        """Initialize the monitor with system information and paths"""
        print("Initializing Downloads folder monitor...")

        # Display system information
        self._display_system_info()

        # Get and validate Downloads path
        self.downloads_path = get_downloads_path()
        if not self._validate_downloads_path():
            return False

        # Load existing data
        if not self._load_existing_data():
            return False

        print("Initialization completed successfully!")
        return True

    def _display_system_info(self):
        """Display system information"""
        print("\n=== System Information ===")
        system_info = get_system_info()
        print(f"Platform: {system_info['platform']}")
        print(f"Machine: {system_info['machine']}")
        print(f"Hostname: {system_info['node']}")
        print(f"WSL2 detected: {system_info['is_wsl2']}")
        print(f"Extensions enabled: {self.enable_extensions}")

    def _validate_downloads_path(self):
        """Validate Downloads folder path"""
        print(f"\nMonitoring path: {self.downloads_path}")

        if not os.path.exists(self.downloads_path):
            print(f"Error: Downloads folder doesn't exist: {self.downloads_path}")
            self._show_wsl2_troubleshooting()
            return False

        return True

    def _show_wsl2_troubleshooting(self):
        """Show WSL2 troubleshooting suggestions"""
        if is_wsl2():
            print("\nWSL2 troubleshooting suggestions:")
            print("1. Ensure Windows is accessible from WSL2")
            print("2. Check if /mnt/c is properly mounted")
            print("3. Verify Windows username in path: /mnt/c/Users/[Username]/Downloads")
            print("4. Try running: ls /mnt/c/Users/")

    def _load_existing_data(self):
        """Load existing CSV data"""
        print("Loading existing data...")
        self.existing_data = load_from_csv()  # Use default Downloads path
        print(f"Existing records: {len(self.existing_data)}")
        return True

    def scan_folder(self):
        """Scan Downloads folder for files"""
        print("Scanning Downloads folder...")
        self.new_data = scan_downloads_folder()
        print(f"Files scanned: {len(self.new_data)}")

        if not self.new_data:
            print("Warning: No files scanned")
            return False

        return True

    def update_data(self):
        """Update data with new scan results"""
        print("Updating data...")
        self.updated_data = update_csv_data(self.existing_data, self.new_data)
        print(f"Updated records: {len(self.updated_data)}")
        return True

    def save_data(self):
        """Save updated data to CSV"""
        print("Saving data to CSV...")
        save_to_csv(self.updated_data)  # Use default Downloads path
        return True

    def run_extensions(self):
        """Run extension analysis if available"""
        if not self.enable_extensions or not self.extension_manager:
            return

        print("\nRunning extensions...")
        try:
            # Run extensions on current data
            self.extension_manager.run_all_extensions(self.updated_data, self.existing_data)

            # Display extension results
            self.extension_manager.display_all_results()

        except Exception as e:
            print(f"Error running extensions: {e}")

    def display_statistics(self):
        """Display monitoring statistics"""
        print("\n=== Statistics ===")
        print(f"Downloads path: {self.downloads_path}")
        print(f"Total files: {len(self.updated_data)}")

        # Group statistics by folder
        folder_stats = self._calculate_folder_statistics()
        self._display_folder_statistics(folder_stats)

    def _calculate_folder_statistics(self):
        """Calculate folder distribution statistics"""
        folder_stats = {}
        for item in self.updated_data:
            folder = item["folder_name"] if item["folder_name"] else "Root Directory"
            if folder not in folder_stats:
                folder_stats[folder] = 0
            folder_stats[folder] += 1
        return folder_stats

    def _display_folder_statistics(self, folder_stats):
        """Display folder distribution statistics"""
        print("\nBy folder distribution:")
        for folder, count in sorted(folder_stats.items()):
            print(f"  {folder}: {count} files")

    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        print("Starting Downloads folder monitoring...")

        if not self.initialize():
            return False

        # First, organize files into categories
        print("\n=== File Organization Phase ===")
        organize_downloads_folder(self.downloads_path)

        if not self.scan_folder():
            return False

        if not self.update_data():
            return False

        if not self.save_data():
            return False

        # Run extensions for additional analysis
        self.run_extensions()

        # Display basic statistics
        self.display_statistics()
        print("\nMonitoring completed!")
        return True


class ContinuousMonitor:
    """Continuous monitoring class"""

    def __init__(self, monitor_instance, interval=60):
        self.monitor = monitor_instance
        self.interval = interval
        self.running = False

    def start(self):
        """Start continuous monitoring"""
        print(f"Starting continuous monitoring, interval: {self.interval} seconds")
        print("Press Ctrl+C to stop monitoring")

        self.running = True
        try:
            while self.running:
                print(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
                self.monitor.run_monitoring_cycle()
                print(f"Waiting {self.interval} seconds for next monitoring...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop continuous monitoring"""
        self.running = False
        print("\nMonitoring stopped")


def show_system_info():
    """Display detailed system information"""
    print("=== System Information ===")
    system_info = get_system_info()

    for key, value in system_info.items():
        if key == "env_vars":
            print(f"{key}:")
            for env_key, env_value in value.items():
                print(f"  {env_key}: {env_value}")
        else:
            print(f"{key}: {value}")


def show_help():
    """Display help information"""
    print("Downloads folder monitoring tool")
    print("\nUsage:")
    print("  python app.py              # Execute monitoring once")
    print("  python app.py -c           # Continuous monitoring, default 60s interval")
    print("  python app.py -c 30        # Continuous monitoring, 30s interval")
    print("  python app.py --help       # Show help information")
    print("  python app.py --info       # Show system information")
    print("  python app.py --no-ext     # Disable extensions")
    print("  python app.py --ext-only   # Run only extensions (requires previous data)")


def run_extensions_only():
    """Run only extensions on existing data"""
    if not EXTENSIONS_AVAILABLE:
        print("Error: Extensions module not available")
        return False

    print("Running extensions on existing data...")

    # Load existing data
    existing_data = load_from_csv()
    if not existing_data:
        print("Error: No existing data found. Run monitoring first.")
        return False

    # Create and run extensions
    try:
        extension_manager = create_extension_manager()
        extension_manager.run_all_extensions(existing_data)
        extension_manager.display_all_results()
        return True
    except Exception as e:
        print(f"Error running extensions: {e}")
        return False


def main():
    """Main function: Execute monitoring once"""
    monitor = DownloadsMonitor()
    return monitor.run_monitoring_cycle()


def monitor_once():
    """Execute monitoring once"""
    return main()


def monitor_continuous(interval=60):
    """Start continuous monitoring"""
    monitor = DownloadsMonitor()
    continuous_monitor = ContinuousMonitor(monitor, interval)
    continuous_monitor.start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous" or sys.argv[1] == "-c":
            interval = 60
            if len(sys.argv) > 2:
                try:
                    interval = int(sys.argv[2])
                except ValueError:
                    print("Error: Interval time must be an integer")
                    sys.exit(1)
            monitor_continuous(interval)
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            show_help()
        elif sys.argv[1] == "--info" or sys.argv[1] == "-i":
            show_system_info()
        elif sys.argv[1] == "--no-ext":
            monitor = DownloadsMonitor(enable_extensions=False)
            monitor.run_monitoring_cycle()
        elif sys.argv[1] == "--ext-only":
            run_extensions_only()
        else:
            print(f"Unknown parameter: {sys.argv[1]}")
            print("Use --help to see help information")
    else:
        # Default: execute monitoring once
        main()
