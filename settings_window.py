#!/usr/bin/env python3
"""
Settings window for Downloads Monitor GUI
Allows users to configure application settings
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


class SettingsWindow:
    """Settings configuration window"""
    
    def __init__(self, parent, settings, callback=None):
        self.parent = parent
        self.settings = settings.copy()  # Work with a copy
        self.original_settings = settings
        self.callback = callback
        
        # Create settings window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings - Downloads Monitor")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.center_window()
        
        # Setup GUI
        self.setup_gui()
        
        # Load current settings
        self.load_current_settings()
        
    def center_window(self):
        """Center the settings window on the parent"""
        self.window.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate position for centering
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def setup_gui(self):
        """Setup the settings window GUI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for different setting categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create setting tabs
        self.create_general_tab()
        self.create_monitoring_tab()
        self.create_advanced_tab()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Buttons
        ttk.Button(button_frame, text="Restore Defaults", 
                  command=self.restore_defaults).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Apply", 
                  command=self.apply_settings).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="OK", 
                  command=self.ok).pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_general_tab(self):
        """Create general settings tab"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Downloads path setting
        path_frame = ttk.LabelFrame(general_frame, text="Paths", padding=15)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(path_frame, text="Downloads Folder:").pack(anchor=tk.W)
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.downloads_path_var = tk.StringVar()
        self.downloads_path_entry = ttk.Entry(path_entry_frame, textvariable=self.downloads_path_var)
        self.downloads_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(path_entry_frame, text="Browse", 
                  command=self.browse_downloads_path).pack(side=tk.RIGHT)
        
        # File organization settings
        org_frame = ttk.LabelFrame(general_frame, text="File Organization", padding=15)
        org_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_organize_var = tk.BooleanVar()
        ttk.Checkbutton(org_frame, text="Automatically organize files into folders", 
                       variable=self.auto_organize_var).pack(anchor=tk.W)
        
        ttk.Label(org_frame, text="Files will be automatically moved to categorized folders\n"
                                 "(Programs, Documents, Music, Video, Compressed)").pack(anchor=tk.W, pady=(5, 0))
        
        # Extensions settings
        ext_frame = ttk.LabelFrame(general_frame, text="Extensions", padding=15)
        ext_frame.pack(fill=tk.X)
        
        self.enable_extensions_var = tk.BooleanVar()
        ttk.Checkbutton(ext_frame, text="Enable analysis extensions", 
                       variable=self.enable_extensions_var).pack(anchor=tk.W)
        
        ttk.Label(ext_frame, text="Extensions provide additional analysis features\n"
                                 "(File type analysis, size analysis, change detection)").pack(anchor=tk.W, pady=(5, 0))
    
    def create_monitoring_tab(self):
        """Create monitoring settings tab"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="Monitoring")
        
        # Continuous monitoring settings
        cont_frame = ttk.LabelFrame(monitoring_frame, text="Continuous Monitoring", padding=15)
        cont_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.continuous_monitoring_var = tk.BooleanVar()
        ttk.Checkbutton(cont_frame, text="Enable continuous monitoring by default", 
                       variable=self.continuous_monitoring_var).pack(anchor=tk.W)
        
        # Monitoring interval
        interval_frame = ttk.Frame(cont_frame)
        interval_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(interval_frame, text="Monitoring Interval (seconds):").pack(side=tk.LEFT)
        
        self.monitoring_interval_var = tk.StringVar()
        interval_spinbox = ttk.Spinbox(interval_frame, from_=10, to=3600, width=10,
                                      textvariable=self.monitoring_interval_var)
        interval_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(interval_frame, text="(10-3600 seconds)").pack(side=tk.LEFT, padx=(10, 0))
        
        # Scan options
        scan_frame = ttk.LabelFrame(monitoring_frame, text="Scan Options", padding=15)
        scan_frame.pack(fill=tk.X)
        
        ttk.Label(scan_frame, text="Performance Settings:").pack(anchor=tk.W)
        
        perf_frame = ttk.Frame(scan_frame)
        perf_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(perf_frame, text="• Large files are processed in chunks").pack(anchor=tk.W)
        ttk.Label(perf_frame, text="• System files are automatically excluded").pack(anchor=tk.W)
        ttk.Label(perf_frame, text="• SHA1 deduplication prevents duplicate entries").pack(anchor=tk.W)
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Logging settings
        log_frame = ttk.LabelFrame(advanced_frame, text="Logging", padding=15)
        log_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(log_frame, text="Log Level:").pack(anchor=tk.W)
        
        self.log_level_var = tk.StringVar()
        log_combo = ttk.Combobox(log_frame, textvariable=self.log_level_var,
                                values=["DEBUG", "INFO", "WARNING", "ERROR"],
                                state="readonly", width=20)
        log_combo.pack(anchor=tk.W, pady=(5, 10))
        
        # CSV settings
        csv_frame = ttk.LabelFrame(advanced_frame, text="Data Export", padding=15)
        csv_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(csv_frame, text="CSV Export Format:").pack(anchor=tk.W)
        ttk.Label(csv_frame, text="• Enhanced format with 7 columns").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(csv_frame, text="• Backward compatible with v0.1.x").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(csv_frame, text="• ISO8601 timestamps for precision").pack(anchor=tk.W, padx=(20, 0))
        
        # System info
        sys_frame = ttk.LabelFrame(advanced_frame, text="System Information", padding=15)
        sys_frame.pack(fill=tk.X)
        
        # System info display
        self.sys_info_text = tk.Text(sys_frame, height=6, wrap=tk.WORD)
        self.sys_info_text.pack(fill=tk.X)
        
        ttk.Button(sys_frame, text="Refresh System Info", 
                  command=self.refresh_system_info).pack(pady=(10, 0))
    
    def browse_downloads_path(self):
        """Browse for downloads folder"""
        current_path = self.downloads_path_var.get()
        initial_dir = current_path if os.path.exists(current_path) else os.path.expanduser("~")
        
        folder_path = filedialog.askdirectory(
            title="Select Downloads Folder",
            initialdir=initial_dir
        )
        
        if folder_path:
            self.downloads_path_var.set(folder_path)
    
    def load_current_settings(self):
        """Load current settings into the form"""
        self.downloads_path_var.set(self.settings.get('downloads_path', ''))
        self.auto_organize_var.set(self.settings.get('auto_organize', True))
        self.enable_extensions_var.set(self.settings.get('enable_extensions', True))
        self.continuous_monitoring_var.set(self.settings.get('continuous_monitoring', False))
        self.monitoring_interval_var.set(str(self.settings.get('monitoring_interval', 60)))
        self.log_level_var.set(self.settings.get('log_level', 'INFO'))
        
        # Load system info
        self.refresh_system_info()
    
    def refresh_system_info(self):
        """Refresh system information display"""
        try:
            from file_monitor import get_system_info
            
            sys_info = get_system_info()
            
            info_text = f"Platform: {sys_info.get('platform', 'Unknown')}\n"
            info_text += f"Machine: {sys_info.get('machine', 'Unknown')}\n"
            info_text += f"Node: {sys_info.get('node', 'Unknown')}\n"
            info_text += f"Downloads Path: {sys_info.get('downloads_path', 'Unknown')}\n"
            info_text += f"GUI Version: Windows-native (WSL2 support removed)\n"
            
            self.sys_info_text.delete(1.0, tk.END)
            self.sys_info_text.insert(1.0, info_text)
            self.sys_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.sys_info_text.delete(1.0, tk.END)
            self.sys_info_text.insert(1.0, f"Error getting system info: {e}")
    
    def validate_settings(self):
        """Validate current settings"""
        errors = []
        
        # Validate downloads path
        downloads_path = self.downloads_path_var.get().strip()
        if not downloads_path:
            errors.append("Downloads path cannot be empty")
        elif not os.path.exists(downloads_path):
            errors.append("Downloads path does not exist")
        elif not os.path.isdir(downloads_path):
            errors.append("Downloads path is not a directory")
        
        # Validate monitoring interval
        try:
            interval = int(self.monitoring_interval_var.get())
            if interval < 10 or interval > 3600:
                errors.append("Monitoring interval must be between 10 and 3600 seconds")
        except ValueError:
            errors.append("Monitoring interval must be a valid number")
        
        return errors
    
    def apply_settings(self):
        """Apply current settings"""
        errors = self.validate_settings()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        
        # Update settings dictionary
        self.settings['downloads_path'] = self.downloads_path_var.get().strip()
        self.settings['auto_organize'] = self.auto_organize_var.get()
        self.settings['enable_extensions'] = self.enable_extensions_var.get()
        self.settings['continuous_monitoring'] = self.continuous_monitoring_var.get()
        self.settings['monitoring_interval'] = int(self.monitoring_interval_var.get())
        self.settings['log_level'] = self.log_level_var.get()
        
        # Update original settings
        self.original_settings.clear()
        self.original_settings.update(self.settings)
        
        # Call callback if provided
        if self.callback:
            self.callback(self.settings)
        
        return True
    
    def ok(self):
        """OK button handler"""
        if self.apply_settings():
            self.window.destroy()
    
    def cancel(self):
        """Cancel button handler"""
        self.window.destroy()
    
    def restore_defaults(self):
        """Restore default settings"""
        result = messagebox.askyesno("Restore Defaults", 
                                   "Are you sure you want to restore default settings?")
        if result:
            # Default settings
            from file_monitor import get_downloads_path
            
            self.downloads_path_var.set(get_downloads_path())
            self.auto_organize_var.set(True)
            self.enable_extensions_var.set(True)
            self.continuous_monitoring_var.set(False)
            self.monitoring_interval_var.set("60")
            self.log_level_var.set("INFO")


def open_settings_window(parent, settings, callback=None):
    """Convenience function to open settings window"""
    return SettingsWindow(parent, settings, callback)
