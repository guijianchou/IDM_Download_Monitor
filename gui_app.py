#!/usr/bin/env python3
"""
GUI Application for Downloads Folder Monitor
A modern Tkinter-based interface for monitoring and organizing downloads
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import sys
from datetime import datetime
import time
import json

# Import our existing monitoring classes
from file_monitor import (
    get_downloads_path,
    get_system_info,
    scan_downloads_folder,
    load_from_csv,
    update_csv_data,
    save_to_csv
)
from file_organizer import organize_downloads_folder
from app import DownloadsMonitor

try:
    from extensions import create_extension_manager
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False


class MonitorGUI:
    """Main GUI Application for Downloads Monitor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Downloads Monitor - GUI")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)
        
        # Application state
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitor = None
        self.settings = self.load_settings()
        
        # GUI Components
        self.status_var = tk.StringVar(value="Ready")
        self.files_count_var = tk.StringVar(value="0")
        self.last_scan_var = tk.StringVar(value="Never")
        
        self.setup_gui()
        self.update_status("Application initialized")
        
        # Clear the file display after startup scan
        self.root.after(100, self.clear_startup_display)
        
    def load_settings(self):
        """Load settings from config file"""
        default_settings = {
            'downloads_path': get_downloads_path(),
            'csv_path': '',  # Will be set based on downloads_path
            'continuous_monitoring': False,
            'monitoring_interval': 60,
            'enable_extensions': True,
            'log_level': 'INFO',
            'auto_organize': True
        }
        
        try:
            if os.path.exists('gui_config.json'):
                with open('gui_config.json', 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            with open('gui_config.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Configure style
        self.setup_styles()
        
        # Create main menu
        self.create_menu()
        
        # Create main layout
        self.create_main_layout()
        
        # Create status bar
        self.create_status_bar()
        
        # Initialize with current settings
        self.refresh_system_info()
        
    def setup_styles(self):
        """Configure ttk styles for modern clean appearance"""
        style = ttk.Style()
        
        # Use modern theme
        try:
            style.theme_use('winnative')
        except:
            style.theme_use('default')
        
        # Clean modern color palette
        colors = {
            'primary': '#2563eb',      # Clean blue
            'success': '#10b981',      # Clean green
            'warning': '#f59e0b',      # Clean orange
            'danger': '#ef4444',       # Clean red
            'text_primary': '#1f2937', # Dark gray
            'text_secondary': '#6b7280' # Medium gray
        }
        
        # Configure clean fonts
        self.fonts = {
            'title': ('Segoe UI', 13, 'bold'),
            'heading': ('Segoe UI', 11, 'bold'),
            'body': ('Segoe UI', 10),
            'small': ('Segoe UI', 9)
        }
        
        # Configure simple, clean styles
        style.configure('Title.TLabel', 
                       font=self.fonts['title'])
        
        style.configure('Heading.TLabel', 
                       font=self.fonts['heading'])
        
        style.configure('Status.TLabel', 
                       font=self.fonts['body'],
                       foreground=colors['primary'])
        
        style.configure('Success.TLabel', 
                       font=self.fonts['body'],
                       foreground=colors['success'])
        
        style.configure('Error.TLabel', 
                       font=self.fonts['body'],
                       foreground=colors['danger'])
        
        style.configure('Warning.TLabel', 
                       font=self.fonts['body'],
                       foreground=colors['warning'])
        
        # Store colors for later use
        self.colors = colors
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Downloads Folder", command=self.open_downloads_folder)
        file_menu.add_command(label="Open CSV File", command=self.open_csv_file)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Monitor menu
        monitor_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Monitor", menu=monitor_menu)
        monitor_menu.add_command(label="Start Monitoring", command=self.start_monitoring)
        monitor_menu.add_command(label="Stop Monitoring", command=self.stop_monitoring)
        monitor_menu.add_command(label="Scan Once", command=self.scan_once)
        monitor_menu.add_separator()
        monitor_menu.add_command(label="Organize Files", command=self.organize_files)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs with better styling (reordered)
        self.create_monitor_tab()
        self.create_file_details_tab()
        self.create_statistics_tab()
        self.create_logs_tab()
        
        # Add some padding to notebook
        self.notebook.pack_configure(pady=(5, 0))
    
    def create_monitor_tab(self):
        """Create the main monitoring tab"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="🔍 Monitor")
        
        # Top section - System Info and Controls
        top_frame = ttk.LabelFrame(monitor_frame, text="System Information", padding=15)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # System info in grid layout
        info_grid = ttk.Frame(top_frame)
        info_grid.pack(fill=tk.X)
        
        # System info labels
        ttk.Label(info_grid, text="Downloads Path:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.downloads_path_label = ttk.Label(info_grid, text=self.settings['downloads_path'])
        self.downloads_path_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_grid, text="Status:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.status_label = ttk.Label(info_grid, textvariable=self.status_var, style='Status.TLabel')
        self.status_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(info_grid, text="Files Count:", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(info_grid, textvariable=self.files_count_var).grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(info_grid, text="Last Scan:", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(info_grid, textvariable=self.last_scan_var).grid(row=3, column=1, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.LabelFrame(monitor_frame, text="Controls", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack()
        
        self.start_btn = ttk.Button(buttons_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(buttons_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.scan_btn = ttk.Button(buttons_frame, text="Scan Once", command=self.scan_once)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.organize_btn = ttk.Button(buttons_frame, text="Organize Files", command=self.organize_files)
        self.organize_btn.pack(side=tk.LEFT, padx=5)
        
        # Add separator
        ttk.Separator(buttons_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        self.custom_folder_btn = ttk.Button(buttons_frame, text="Custom Folder", command=self.manage_custom_folder)
        self.custom_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Progress label
        self.progress_label = ttk.Label(control_frame, text="Ready", font=self.fonts['small'])
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))
        
        # File list frame
        files_frame = ttk.LabelFrame(monitor_frame, text="Recent Files", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame to contain treeview and scrollbars
        tree_container = ttk.Frame(files_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for file list
        columns = ('Filename', 'Folder', 'Size', 'Modified')
        self.file_tree = ttk.Treeview(tree_container, columns=columns, show='tree headings', height=10)
        
        # Configure columns with better width distribution
        self.file_tree.heading('#0', text='Path')
        self.file_tree.column('#0', width=250, minwidth=150)
        
        # Set specific widths for each column
        column_widths = {
            'Filename': 200,
            'Folder': 120, 
            'Size': 100,
            'Modified': 140
        }
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            width = column_widths.get(col, 120)
            self.file_tree.column(col, width=width, minwidth=80)
        
        # Add scrollbars
        file_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.file_tree.yview)
        file_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=file_scroll_y.set, xscrollcommand=file_scroll_x.set)
        
        # Grid layout for proper scrollbar positioning
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        file_scroll_y.grid(row=0, column=1, sticky='ns')
        file_scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
    
    def create_statistics_tab(self):
        """Create the statistics tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistics")
        
        # Top controls
        stats_controls = ttk.Frame(stats_frame)
        stats_controls.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        ttk.Label(stats_controls, text="File Analysis", style='Heading.TLabel').pack(side=tk.LEFT)
        refresh_stats_btn = ttk.Button(stats_controls, text="Refresh Statistics", command=self.refresh_statistics)
        refresh_stats_btn.pack(side=tk.RIGHT)
        
        # Statistics content in a nice frame
        stats_content_frame = ttk.LabelFrame(stats_frame, text="Analysis Results", padding=10)
        stats_content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.stats_text = scrolledtext.ScrolledText(stats_content_frame, height=20, font=self.fonts['body'])
        self.stats_text.pack(fill=tk.BOTH, expand=True)
    
    def create_logs_tab(self):
        """Create the logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 Logs")
        
        # Top controls
        logs_top_controls = ttk.Frame(logs_frame)
        logs_top_controls.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        ttk.Label(logs_top_controls, text="Application Logs", style='Heading.TLabel').pack(side=tk.LEFT)
        
        # Log controls on the right
        log_controls = ttk.Frame(logs_top_controls)
        log_controls.pack(side=tk.RIGHT)
        
        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(side=tk.LEFT)
        
        # Logs content in a nice frame
        logs_content_frame = ttk.LabelFrame(logs_frame, text="Activity Log", padding=10)
        logs_content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.logs_text = scrolledtext.ScrolledText(logs_content_frame, height=20, font=self.fonts['body'])
        self.logs_text.pack(fill=tk.BOTH, expand=True)
    
    def create_file_details_tab(self):
        """Create the file details tab"""
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="📄 File Details")
        
        # Top controls frame
        details_top_controls = ttk.Frame(details_frame)
        details_top_controls.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        ttk.Label(details_top_controls, text="CSV File Analysis", style='Heading.TLabel').pack(side=tk.LEFT)
        
        # Control buttons on the right
        details_controls = ttk.Frame(details_top_controls)
        details_controls.pack(side=tk.RIGHT)
        
        ttk.Button(details_controls, text="Refresh Details", command=self.refresh_file_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(details_controls, text="Open CSV File", command=self.open_csv_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(details_controls, text="Export Details", command=self.export_file_details).pack(side=tk.LEFT)
        
        # Create notebook for different detail views with padding
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 15))
        
        # CSV Content tab
        self.create_csv_content_tab()
        
        # File Summary tab
        self.create_file_summary_tab()
        
        # Recent Changes tab
        self.create_recent_changes_tab()
    
    def create_csv_content_tab(self):
        """Create CSV content display tab"""
        csv_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(csv_frame, text="CSV Content")
        
        # CSV content display with treeview for better formatting
        columns = ('Path', 'Rel Path', 'Folder', 'Filename', 'SHA1', 'Timestamp', 'Modified ISO')
        self.csv_tree = ttk.Treeview(csv_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.csv_tree.heading(col, text=col)
            if col == 'SHA1':
                self.csv_tree.column(col, width=100)  # Shorter for SHA1
            elif col == 'Path':
                self.csv_tree.column(col, width=200)  # Longer for path
            else:
                self.csv_tree.column(col, width=120)
        
        # Add scrollbars
        csv_scroll_y = ttk.Scrollbar(csv_frame, orient=tk.VERTICAL, command=self.csv_tree.yview)
        csv_scroll_x = ttk.Scrollbar(csv_frame, orient=tk.HORIZONTAL, command=self.csv_tree.xview)
        self.csv_tree.configure(yscrollcommand=csv_scroll_y.set, xscrollcommand=csv_scroll_x.set)
        
        # Pack treeview and scrollbars
        self.csv_tree.grid(row=0, column=0, sticky='nsew')
        csv_scroll_y.grid(row=0, column=1, sticky='ns')
        csv_scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        csv_frame.grid_rowconfigure(0, weight=1)
        csv_frame.grid_columnconfigure(0, weight=1)
        
        # Status label
        self.csv_status_label = ttk.Label(csv_frame, text="Click 'Refresh Details' to load CSV content")
        self.csv_status_label.grid(row=2, column=0, columnspan=2, pady=5)
    
    def create_file_summary_tab(self):
        """Create file summary tab"""
        summary_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(summary_frame, text="Summary")
        
        # Summary text display
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=20, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize with placeholder text
        self.summary_text.insert(tk.END, "File summary will appear here after refreshing details...")
    
    def create_recent_changes_tab(self):
        """Create recent changes tab"""
        changes_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(changes_frame, text="Recent Changes")
        
        # Changes display
        self.changes_text = scrolledtext.ScrolledText(changes_frame, height=20, wrap=tk.WORD)
        self.changes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize with placeholder text
        self.changes_text.insert(tk.END, "Recent changes will appear here after monitoring...")
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add time display
        self.time_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN)
        self.time_label.pack(side=tk.RIGHT)
        
        self.update_time()
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Update every second
    
    def log_message(self, message, level="INFO"):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.logs_text.insert(tk.END, formatted_message)
        self.logs_text.see(tk.END)
        
        # Also update status bar for important messages
        if level in ["INFO", "SUCCESS", "ERROR"]:
            self.status_bar.config(text=message)
    
    def update_status(self, message, level="INFO"):
        """Update status display"""
        self.log_message(message, level)
        
        # Update status variable
        if level == "ERROR":
            self.status_var.set(f"Error: {message}")
            self.status_label.config(style='Error.TLabel')
        elif level == "SUCCESS":
            self.status_var.set(message)
            self.status_label.config(style='Success.TLabel')
        else:
            self.status_var.set(message)
            self.status_label.config(style='Status.TLabel')
    
    def refresh_system_info(self):
        """Refresh system information display"""
        self.downloads_path_label.config(text=self.settings['downloads_path'])
    
    # Menu and button handlers
    def open_downloads_folder(self):
        """Open downloads folder in file explorer"""
        try:
            os.startfile(self.settings['downloads_path'])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder: {e}")
    
    def open_csv_file(self):
        """Open CSV file in default application"""
        csv_path = os.path.join(self.settings['downloads_path'], 'results.csv')
        try:
            if os.path.exists(csv_path):
                os.startfile(csv_path)
            else:
                messagebox.showwarning("Warning", "CSV file not found. Run a scan first.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open CSV file: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        self.open_settings_window()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Downloads Monitor GUI v1.0
        
A Windows-native GUI for monitoring and organizing downloads.

Features:
• Real-time file monitoring
• Automatic file organization  
• SHA1 hash tracking
• Statistics and analysis
• Extensible architecture

Built with Python and Tkinter"""
        
        messagebox.showinfo("About Downloads Monitor", about_text)
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start(10)
        self.progress_label.config(text="Continuous monitoring active...")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.update_status("Monitoring started", "SUCCESS")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.progress_label.config(text="Monitoring stopped")
        
        self.update_status("Monitoring stopped", "INFO")
    
    def scan_once(self):
        """Perform a single scan"""
        if self.is_monitoring:
            messagebox.showwarning("Warning", "Please stop continuous monitoring first")
            return
            
        # Start progress indicator for single scan
        self.progress.start(10)
        self.progress_label.config(text="Scanning files...")
        self.scan_btn.config(state=tk.DISABLED)
        
        # Run scan in separate thread
        threading.Thread(target=self.perform_single_scan, daemon=True).start()
    
    def organize_files(self):
        """Organize files in downloads folder"""
        threading.Thread(target=self.perform_organization, daemon=True).start()
    
    def manage_custom_folder(self):
        """Open custom folder management dialog"""
        self.open_custom_folder_dialog()
    
    def monitoring_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        while self.is_monitoring:
            try:
                self.perform_scan()
                time.sleep(self.settings['monitoring_interval'])
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Monitoring error: {e}", "ERROR"))
                break
    
    def perform_scan(self):
        """Perform actual scan operation (for continuous monitoring)"""
        try:
            self.root.after(0, lambda: self.update_status("Scanning files...", "INFO"))
            
            # Create monitor instance
            monitor = DownloadsMonitor(
                csv_path=os.path.join(self.settings['downloads_path'], 'results.csv'),
                enable_extensions=self.settings['enable_extensions']
            )
            
            # Run monitoring cycle
            success = monitor.run_monitoring_cycle()
            
            if success:
                # Update GUI with results
                self.root.after(0, lambda: self.update_scan_results(monitor))
            else:
                self.root.after(0, lambda: self.update_status("Scan failed", "ERROR"))
                
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Scan error: {e}", "ERROR"))
    
    def perform_single_scan(self):
        """Perform a single scan operation"""
        try:
            self.root.after(0, lambda: self.update_status("Scanning files...", "INFO"))
            
            # Create monitor instance
            monitor = DownloadsMonitor(
                csv_path=os.path.join(self.settings['downloads_path'], 'results.csv'),
                enable_extensions=self.settings['enable_extensions']
            )
            
            # Run monitoring cycle
            success = monitor.run_monitoring_cycle()
            
            if success:
                # Update GUI with results
                self.root.after(0, lambda: self.update_single_scan_results(monitor))
            else:
                self.root.after(0, lambda: self.finish_single_scan("Scan failed", "ERROR"))
                
        except Exception as e:
            self.root.after(0, lambda: self.finish_single_scan(f"Scan error: {e}", "ERROR"))
    
    def perform_organization(self):
        """Perform file organization"""
        try:
            self.root.after(0, lambda: self.update_status("Organizing files...", "INFO"))
            
            organize_downloads_folder(self.settings['downloads_path'])
            
            self.root.after(0, lambda: self.update_status("Files organized successfully", "SUCCESS"))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Organization error: {e}", "ERROR"))
    
    def update_scan_results(self, monitor):
        """Update GUI with scan results (for continuous monitoring)"""
        # Update file count
        if hasattr(monitor, 'updated_data'):
            self.files_count_var.set(str(len(monitor.updated_data)))
            
            # Update file tree
            self.update_file_tree(monitor.updated_data)
        
        # Update last scan time
        self.last_scan_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        self.update_status("Scan completed successfully", "SUCCESS")
    
    def update_single_scan_results(self, monitor):
        """Update GUI with single scan results and stop progress"""
        # Update file count
        if hasattr(monitor, 'updated_data'):
            self.files_count_var.set(str(len(monitor.updated_data)))
            
            # Update file tree
            self.update_file_tree(monitor.updated_data)
        
        # Update last scan time
        self.last_scan_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        self.finish_single_scan("Single scan completed successfully", "SUCCESS")
    
    def finish_single_scan(self, message, level="INFO"):
        """Finish single scan operation and stop progress"""
        # Stop progress bar and re-enable button
        self.progress.stop()
        self.progress_label.config(text="Scan completed")
        self.scan_btn.config(state=tk.NORMAL)
        
        # Update status
        self.update_status(message, level)
    
    def update_file_tree(self, file_data):
        """Update the file tree with new data"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Check if file_data is empty
        if not file_data:
            # Add placeholder for empty folder
            self.file_tree.insert('', tk.END, 
                                text="No files found",
                                values=("Folder is empty or no matching files", "", "", ""))
            return
        
        # Add new items (limit to recent 100 files for performance)
        for item in file_data[-100:]:
            try:
                filename = item.get('filename', 'Unknown')
                folder = item.get('folder_name', 'Root')
                rel_path = item.get('rel_path', '')
                path = item.get('path', '')
                mtime_iso = item.get('mtime_iso', '')
                
                # Use the best available path for display
                if rel_path:
                    display_path = rel_path
                elif folder and folder != 'Root' and folder != '~':
                    display_path = f"{folder}/{filename}"
                elif path:
                    display_path = path
                    if display_path.startswith('~\\'):
                        display_path = display_path[2:]  # Remove ~\ prefix
                else:
                    display_path = filename
                
                # Format modification time
                if mtime_iso:
                    try:
                        # Parse ISO format and convert to readable format
                        dt = datetime.fromisoformat(mtime_iso.replace('T', ' '))
                        mtime_display = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        mtime_display = mtime_iso
                else:
                    mtime_display = 'Unknown'
                
                # Get file size
                file_size = self.get_file_size(item, filename, folder)
                
                # Insert into tree
                self.file_tree.insert('', tk.END, 
                                    text=display_path,
                                    values=(filename, folder, file_size, mtime_display))
            except Exception as e:
                print(f"Error updating tree item: {e}")
    
    def get_file_size(self, item_data, filename, folder):
        """Get file size for display"""
        try:
            downloads_path = self.settings['downloads_path']
            
            # Try multiple possible paths
            possible_paths = []
            
            # 1. If folder is specified and not root
            if folder and folder != 'Root' and folder != '~':
                possible_paths.append(os.path.join(downloads_path, folder, filename))
            
            # 2. Root downloads folder
            possible_paths.append(os.path.join(downloads_path, filename))
            
            # 3. If there's a rel_path in item_data, try using that
            rel_path = item_data.get('rel_path', '')
            if rel_path:
                # Convert forward slashes to backslashes for Windows
                windows_path = rel_path.replace('/', os.sep)
                possible_paths.append(os.path.join(downloads_path, windows_path))
            
            # Try each possible path
            for full_path in possible_paths:
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    size_bytes = os.path.getsize(full_path)
                    return self.format_file_size(size_bytes)
            
            # If no file found, return appropriate message
            return 'Not found'
            
        except Exception as e:
            return 'Error'
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return '0 B'
        
        size_names = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def refresh_statistics(self):
        """Refresh statistics display"""
        try:
            # Load CSV data if exists
            csv_path = os.path.join(self.settings['downloads_path'], 'results.csv')
            if os.path.exists(csv_path):
                # Simple statistics generation
                stats_text = self.generate_statistics(csv_path)
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, stats_text)
            else:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, "No data available. Run a scan first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh statistics: {e}")
    
    def generate_statistics(self, csv_path):
        """Generate statistics text from CSV data"""
        try:
            import csv
            
            stats = {
                'total_files': 0,
                'folders': {},
                'file_types': {},
            }
            
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    stats['total_files'] += 1
                    
                    # Count by folder
                    folder = row.get('folder_name', 'Root')
                    stats['folders'][folder] = stats['folders'].get(folder, 0) + 1
                    
                    # Count by file extension
                    filename = row.get('filename', '')
                    if '.' in filename:
                        ext = filename.split('.')[-1].lower()
                        stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
            
            # Generate statistics text
            text = f"Total Files: {stats['total_files']}\n\n"
            
            text += "Files by Folder:\n"
            text += "-" * 30 + "\n"
            for folder, count in sorted(stats['folders'].items()):
                text += f"{folder}: {count} files\n"
            
            text += "\nFiles by Type:\n"
            text += "-" * 30 + "\n"
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:20]:
                text += f".{ext}: {count} files\n"
            
            return text
            
        except Exception as e:
            return f"Error generating statistics: {e}"
    
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.delete(1.0, tk.END)
        self.log_message("Logs cleared")
    
    def save_logs(self):
        """Save logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Logs saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def refresh_file_details(self):
        """Refresh file details from CSV"""
        try:
            csv_path = os.path.join(self.settings['downloads_path'], 'results.csv')
            if not os.path.exists(csv_path):
                self.csv_status_label.config(text="CSV file not found. Run a scan first.")
                return
            
            # Load CSV data
            self.load_csv_content(csv_path)
            self.generate_file_summary(csv_path)
            
            self.csv_status_label.config(text=f"CSV loaded: {self.csv_tree.get_children().__len__()} records")
            self.update_status("File details refreshed", "SUCCESS")
            
        except Exception as e:
            self.csv_status_label.config(text=f"Error loading CSV: {e}")
            self.update_status(f"Failed to refresh file details: {e}", "ERROR")
    
    def load_csv_content(self, csv_path):
        """Load CSV content into treeview"""
        import csv
        
        # Clear existing content
        for item in self.csv_tree.get_children():
            self.csv_tree.delete(item)
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Truncate SHA1 for display
                    sha1_display = row.get('sha1sum', '')[:12] + '...' if len(row.get('sha1sum', '')) > 12 else row.get('sha1sum', '')
                    
                    values = (
                        row.get('path', ''),
                        row.get('rel_path', ''),
                        row.get('folder_name', ''),
                        row.get('filename', ''),
                        sha1_display,
                        row.get('timestamp', ''),
                        row.get('mtime_iso', '')
                    )
                    self.csv_tree.insert('', tk.END, values=values)
        except Exception as e:
            raise Exception(f"Error reading CSV: {e}")
    
    def generate_file_summary(self, csv_path):
        """Generate file summary statistics"""
        import csv
        from collections import defaultdict
        
        try:
            # Clear existing summary
            self.summary_text.delete(1.0, tk.END)
            
            stats = {
                'total_files': 0,
                'folders': defaultdict(int),
                'extensions': defaultdict(int),
                'sizes': defaultdict(int),
                'dates': defaultdict(int)
            }
            
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    stats['total_files'] += 1
                    
                    # Folder distribution
                    folder = row.get('folder_name', 'Root')
                    stats['folders'][folder] += 1
                    
                    # File extension distribution
                    filename = row.get('filename', '')
                    if '.' in filename:
                        ext = filename.split('.')[-1].lower()
                        stats['extensions'][ext] += 1
                    
                    # Date distribution
                    mtime = row.get('mtime_iso', '')
                    if mtime:
                        date = mtime.split('T')[0]  # Get date part
                        stats['dates'][date] += 1
            
            # Generate summary text
            summary = f"📊 File Details Summary\n"
            summary += f"{'='*50}\n\n"
            
            summary += f"📁 Overview:\n"
            summary += f"   Total Files: {stats['total_files']}\n"
            summary += f"   Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += f"   CSV Path: {csv_path}\n\n"
            
            summary += f"📂 Files by Folder:\n"
            for folder, count in sorted(stats['folders'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_files']) * 100
                summary += f"   {folder}: {count} files ({percentage:.1f}%)\n"
            
            summary += f"\n📄 Files by Extension (Top 10):\n"
            for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (count / stats['total_files']) * 100
                summary += f"   .{ext}: {count} files ({percentage:.1f}%)\n"
            
            summary += f"\n📅 Files by Date (Recent 7 days):\n"
            for date, count in sorted(stats['dates'].items(), reverse=True)[:7]:
                summary += f"   {date}: {count} files\n"
            
            # Additional insights
            summary += f"\n🔍 Insights:\n"
            if stats['folders']:
                most_common_folder = max(stats['folders'].items(), key=lambda x: x[1])
                summary += f"   Most files in: {most_common_folder[0]} ({most_common_folder[1]} files)\n"
            
            if stats['extensions']:
                most_common_ext = max(stats['extensions'].items(), key=lambda x: x[1])
                summary += f"   Most common type: .{most_common_ext[0]} ({most_common_ext[1]} files)\n"
            
            self.summary_text.insert(1.0, summary)
            
        except Exception as e:
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, f"Error generating summary: {e}")
    
    def export_file_details(self):
        """Export file details to a report file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("HTML files", "*.html"), ("All files", "*.*")]
            )
            if filename:
                # Get summary content
                summary_content = self.summary_text.get(1.0, tk.END)
                
                # Add CSV data if requested
                if filename.endswith('.html'):
                    # Create HTML report
                    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Downloads Monitor Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 8px; }}
        h1 {{ color: #007AFF; }}
    </style>
</head>
<body>
    <h1>Downloads Monitor Report</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <pre>{summary_content}</pre>
</body>
</html>"""
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    # Create text report
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Downloads Monitor Report\n")
                        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        f.write(summary_content)
                
                messagebox.showinfo("Success", "File details exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file details: {e}")
    
    def open_settings_window(self):
        """Open settings configuration window"""
        from settings_window import open_settings_window
        open_settings_window(self.root, self.settings, self.on_settings_changed)
    
    def open_custom_folder_dialog(self):
        """Open custom folder selection and management dialog"""
        if self.is_monitoring:
            messagebox.showwarning("Warning", "Please stop monitoring before managing custom folders")
            return
        
        # Create custom folder dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Custom Folders")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        
        # Make window modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        self.center_dialog(dialog)
        
        # Setup custom folder dialog content
        self.setup_custom_folder_dialog(dialog)
    
    def center_dialog(self, dialog):
        """Center dialog on parent window"""
        dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        
        # Calculate position for centering
        dialog_width = dialog.winfo_reqwidth()
        dialog_height = dialog.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        dialog.geometry(f"+{x}+{y}")
    
    def setup_custom_folder_dialog(self, dialog):
        """Setup the custom folder dialog content"""
        # Main container
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Custom Folder Monitoring", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Folder selection section
        selection_frame = ttk.LabelFrame(main_frame, text="Select Folder", padding=15)
        selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Current folder display
        current_frame = ttk.Frame(selection_frame)
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(current_frame, text="Current monitoring folder:").pack(side=tk.LEFT)
        current_folder_var = tk.StringVar(value=self.settings['downloads_path'])
        ttk.Label(current_frame, textvariable=current_folder_var, 
                 foreground=self.colors['primary']).pack(side=tk.LEFT, padx=(10, 0))
        
        # New folder selection
        select_frame = ttk.Frame(selection_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(select_frame, text="New folder:").pack(side=tk.LEFT)
        
        folder_var = tk.StringVar()
        folder_entry = ttk.Entry(select_frame, textvariable=folder_var, width=50)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        def browse_folder():
            folder_path = filedialog.askdirectory(
                title="Select folder to monitor",
                initialdir=os.path.expanduser("~")
            )
            if folder_path:
                folder_var.set(folder_path)
        
        ttk.Button(select_frame, text="Browse", command=browse_folder).pack(side=tk.RIGHT)
        
        # Features explanation
        features_frame = ttk.LabelFrame(main_frame, text="Features", padding=15)
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        features_text = """• Complete file monitoring functionality, same as default Downloads directory
• Automatically calculate file SHA1 hash values and record modification times
• Generate CSV report files saved in the selected directory
• Support file statistics analysis and change detection
• Can manage multiple different directories simultaneously"""
        
        ttk.Label(features_frame, text=features_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        def start_custom_monitoring():
            selected_folder = folder_var.get().strip()
            if not selected_folder:
                messagebox.showwarning("Warning", "Please select a folder")
                return
            
            if not os.path.exists(selected_folder):
                messagebox.showerror("Error", "Selected folder does not exist")
                return
            
            if not os.path.isdir(selected_folder):
                messagebox.showerror("Error", "Selected path is not a folder")
                return
            
            # Start monitoring the custom folder
            self.start_custom_folder_monitoring(selected_folder)
            dialog.destroy()
        
        def restore_default():
            from file_monitor import get_downloads_path
            default_path = get_downloads_path()
            self.settings['downloads_path'] = default_path
            self.refresh_system_info()
            messagebox.showinfo("Success", f"Restored default Downloads directory: {default_path}")
            dialog.destroy()
        
        # Buttons
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Restore Default", 
                  command=restore_default).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Start Monitoring", 
                  command=start_custom_monitoring).pack(side=tk.RIGHT, padx=(10, 0))
    
    def start_custom_folder_monitoring(self, folder_path):
        """Start monitoring a custom folder with the same logic as Downloads"""
        try:
            # Update settings to use the new folder
            self.settings['downloads_path'] = folder_path
            
            # Clear current file tree immediately
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Reset counters
            self.files_count_var.set("0")
            self.last_scan_var.set("Never")
            
            # Update GUI display
            self.refresh_system_info()
            
            # Update status
            self.update_status(f"Switched to custom folder: {os.path.basename(folder_path)}", "SUCCESS")
            
            # Save the new setting
            self.save_settings()
            
            # Show success message with options
            result = messagebox.askyesno(
                "Success",
                f"Switched to folder: {folder_path}\n\nWould you like to perform an initial scan now?",
                icon="question"
            )
            
            if result:
                # Clear any cached data before scanning
                self.clear_cached_data()
                # Perform initial scan
                self.scan_once()
            else:
                # If not scanning immediately, ensure display is clean
                self.clear_file_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch folder: {e}")
    
    def clear_cached_data(self):
        """Clear any cached monitoring data"""
        # Clear file tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Reset counters
        self.files_count_var.set("0")
        self.last_scan_var.set("Never")
        
        # If there's any cached data in the monitor objects, we'll let the scan create fresh ones
        
    def clear_file_display(self):
        """Clear the file display area"""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add a placeholder message
        self.file_tree.insert('', tk.END, 
                            text="No files scanned yet",
                            values=("Click 'Scan Once' to start", "", "", ""))
    
    def clear_startup_display(self):
        """Clear the startup scan display to show clean interface"""
        try:
            # Clear file tree from startup scan
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Reset counters to clean state
            self.files_count_var.set("0")
            self.last_scan_var.set("Never")
            
            # Update status to ready
            self.update_status("Ready - Click 'Scan Once' to start monitoring", "INFO")
        except Exception as e:
            print(f"Error clearing startup display: {e}")
    
    def on_settings_changed(self, new_settings):
        """Handle settings changes"""
        # Save settings immediately
        self.save_settings()
        
        # Update GUI to reflect changes
        self.refresh_system_info()
        
        # Show confirmation
        self.update_status("Settings updated successfully", "SUCCESS")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_monitoring:
            result = messagebox.askyesno("Confirm Exit", "Monitoring is active. Stop monitoring and exit?")
            if result:
                self.stop_monitoring()
                self.save_settings()
                self.root.destroy()
        else:
            self.save_settings()
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main entry point for GUI application"""
    # Set up proper encoding for console output
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # For older Python versions
        pass
    
    print("Starting Downloads Monitor GUI...")
    
    try:
        app = MonitorGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
