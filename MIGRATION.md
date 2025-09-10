# Migration Guide - Downloads Monitor v0.2.0

This document outlines the improvements made to the Downloads Monitor and how to migrate from previous versions.

## What's New in v0.2.0

### 🔧 Fixed Issues
- **FileSizeAnalyzer Label**: Fixed typo in size category "Small (1MB - 1MB)" → "Small (1KB - 1MB)"
- **Timestamp Precision**: Improved from YY/MM/DD to ISO8601 format (YYYY-MM-DDTHH:MM:SS)
- **CSV Full Path**: Enhanced CSV format to include relative paths and restore full_path for extensions
- **Dependencies**: Cleaned up pyproject.toml by removing standard library "dependencies"

### ✨ New Features
- **Enhanced Command Line**: Added argparse-based CLI with better help and validation
- **Logging Support**: Configurable logging levels and file output
- **Improved WSL2 Detection**: Better username detection with environment variable override
- **Enhanced Startup Script**: Improved PowerShell script with error handling and dependency management

### 📊 Enhanced CSV Format
The CSV format now includes additional columns for better data management:
- `path` - Legacy path format (~\folder\name) for backward compatibility
- `rel_path` - Relative path from Downloads folder
- `folder_name` - Folder category name
- `filename` - File name
- `sha1sum` - SHA1 hash
- `timestamp` - Legacy timestamp (YY/MM/DD) for compatibility
- `mtime_iso` - New precise timestamp (ISO8601 format)

## Migration Steps

### 1. Backup Existing Data
```bash
# Backup your current results.csv file
copy "%USERPROFILE%\Downloads\results.csv" "%USERPROFILE%\Downloads\results_backup.csv"
```

### 2. Update Dependencies (if using uv)
The project no longer lists standard library modules as dependencies. If you encounter issues:
```bash
# If using uv
uv sync

# If using pip
pip install -r requirements.txt  # (only dev dependencies)
```

### 3. Environment Variable (WSL2 Users)
For WSL2 users with non-standard usernames, set the environment variable:
```bash
# In WSL2 ~/.bashrc or ~/.profile
export MONITOR_WIN_USERNAME=YourWindowsUsername
```

### 4. Test Migration
Run the monitor once to test the new format:
```bash
# Windows
python app.py --log-level DEBUG

# Or use the enhanced PowerShell script
.\start.ps1 -LogLevel DEBUG
```

## New Command Line Usage

### Basic Usage
```bash
# Single monitoring cycle
python app.py

# Continuous monitoring (60s intervals)
python app.py -c

# Continuous with custom interval
python app.py -c 30

# Show system information
python app.py --info

# Run only extensions
python app.py --ext-only

# Disable extensions
python app.py --no-ext
```

### Advanced Options
```bash
# Custom paths
python app.py --downloads-path "C:\Custom\Path" --csv-path "output.csv"

# Logging
python app.py --log-level DEBUG --log-file monitor.log

# Help
python app.py --help
```

### PowerShell Script Usage
```powershell
# Basic usage
.\start.ps1

# Continuous monitoring
.\start.ps1 -Mode continuous -Interval 30

# With options
.\start.ps1 -NoExt -LogLevel DEBUG

# System information
.\start.ps1 -Mode info
```

## Backward Compatibility

### CSV Data
- Existing CSV files will be read correctly
- New format adds columns without breaking existing data
- Legacy timestamp format is maintained for compatibility
- Full paths are reconstructed automatically

### Command Line
- Old command line arguments still work:
  ```bash
  python app.py -c 60      # Still works
  python app.py --no-ext   # Still works
  python app.py --info     # Still works
  ```

### Extensions
- All existing extensions continue to work
- FileSizeAnalyzer now receives proper full_path data
- Timestamp comparisons are more accurate

## Troubleshooting

### WSL2 Path Detection
If WSL2 path detection fails:
1. Set environment variable: `export MONITOR_WIN_USERNAME=YourUsername`
2. Use override: `python app.py --downloads-path "/mnt/c/Users/YourUser/Downloads"`
3. Check permissions: `ls -la /mnt/c/Users/`

### CSV Format Issues
If you encounter CSV issues:
1. Backup current CSV: `cp results.csv results_backup.csv`
2. Let the program recreate it: `rm results.csv && python app.py`
3. Compare with backup to ensure data integrity

### PowerShell Script
If PowerShell script fails:
1. Check execution policy: `Get-ExecutionPolicy`
2. Allow script execution: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Install Python if not found in PATH

## Performance Improvements

### Timestamp Comparison
- More accurate file modification detection
- Better deduplication based on precise timestamps
- Handles same-day file changes correctly

### Path Handling
- Reduced path resolution overhead
- Better caching of Downloads folder location
- More robust cross-platform path handling

### Error Handling
- Graceful degradation for permission issues
- Better error messages with context
- Timeout protection for subprocess calls

## Future Compatibility

The enhanced CSV format and command line interface are designed to be forward-compatible:
- Additional columns can be added without breaking existing tools
- Command line arguments follow standard conventions
- Logging format is structured for potential log analysis tools

For questions or issues with migration, please check the main README.md or create an issue.
