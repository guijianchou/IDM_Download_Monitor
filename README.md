# Downloads Folder Monitor / 下载文件夹监控器

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**EN** A Windows-native Python CLI tool that keeps your Downloads folder clean, organized, and indexed with automatic file categorization and SHA1 tracking.

**中文** Windows 原生 Python 命令行工具，通过自动文件分类和 SHA1 跟踪，保持下载文件夹的整洁、有序和索引。

---

## Overview / 概览

**Downloads Monitor** is a lightweight, zero-dependency Python tool for Windows that automatically organizes and tracks files in your Downloads folder.

**下载监控器** 是一个轻量级、零依赖的 Windows Python 工具，可自动整理和跟踪下载文件夹中的文件。

### Key Features / 核心功能

- ✨ **Automatic file organization** - Categorizes files by type (Programs, Documents, Pictures, Music, Video, Compressed)
- 📊 **SHA1 tracking** - Calculates and tracks file hashes for duplicate detection
- 📝 **CSV export** - Maintains a searchable database of all files
- 🔍 **File analysis** - Provides insights on file types, sizes, and changes
- ⚙️ **Highly configurable** - JSON-based configuration for all settings
- 🚀 **Zero dependencies** - Uses only Python standard library
- 🔒 **Safe operation** - Dry-run mode for previewing changes

### Platform Requirements / 平台要求

- **OS**: Windows 10/11 64-bit
- **Python**: 3.8+
- **Dependencies**: None (standard library only)
- **Disk Space**: ~10 MB
- **RAM**: ~50-100 MB

---

## Quick Start / 快速开始

### Installation / 安装

1. **Install Python 3.8+** from [python.org](https://python.org)
   - ✅ Check "Add Python to PATH" during installation

2. **Download or clone this project**
   ```bash
   git clone https://github.com/yourusername/downloads-monitor.git
   cd downloads-monitor
   ```

3. **Run the tool**
   ```bash
   python app.py
   ```

### First Run / 首次运行

On first run, the tool will:
1. Create `config.json` with default settings
2. Scan your Downloads folder
3. Organize files into category folders
4. Generate `results.csv` with file information

首次运行时，工具会：
1. 创建默认配置文件 `config.json`
2. 扫描下载文件夹
3. 将文件整理到分类文件夹
4. 生成包含文件信息的 `results.csv`

---

## Usage / 使用

### Basic Commands / 基本命令

```bash
# Single scan (quiet mode)
python app.py

# Single scan (show details)
python app.py --log-level INFO

# Continuous monitoring (60s interval)
python app.py --continuous

# Continuous monitoring (custom interval)
python app.py --continuous 30

# Preview mode (no file moves)
python app.py --dry-run

# Show system information
python app.py --info

# Show help
python app.py --help
```

### Quick Launch / 快速启动

**Windows:**
- Double-click `start.bat` to run a scan / 双击 `start.bat` 运行扫描

### Advanced Options / 高级选项

```bash
# Custom configuration file
python app.py --config my_config.json

# Override Downloads path
python app.py --downloads-path "D:\MyDownloads"

# Set log level
python app.py --log-level DEBUG

# Log to file
python app.py --log-file monitor.log

# Run extensions only
python app.py --ext-only

# Disable extensions
python app.py --no-ext
```

---

## Configuration / 配置

The `config.json` file is automatically created on first run. Customize it to fit your needs.

`config.json` 文件在首次运行时自动创建，可根据需要自定义。

### Default Configuration / 默认配置

```json
{
  "downloads_path": null,
  "csv_path": "results.csv",
  "monitoring": {
    "interval_seconds": 60,
    "enable_extensions": true,
    "calculate_sha1": true
  },
  "organization": {
    "auto_organize": true,
    "categories": {
      "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
      "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
      "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".csv", ".xls", ".xlsx", ".ppt", ".pptx"],
      "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif"],
      "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
      "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]
    },
    "excluded_files": ["results.csv", "desktop.ini", "Thumbs.db", ".DS_Store"]
  },
  "performance": {
    "max_file_size_for_sha1_mb": 500,
    "chunk_size_bytes": 8192
  },
  "logging": {
    "level": "INFO",
    "file": null,
    "console": true
  }
}
```

### Configuration Examples / 配置示例

**Add custom categories / 添加自定义分类:**
```json
"categories": {
  "Images": [".jpg", ".png", ".gif", ".bmp"],
  "Code": [".py", ".js", ".java", ".cpp"]
}
```

**Performance tuning / 性能调优:**
```json
"performance": {
  "max_file_size_for_sha1_mb": 100,
  "chunk_size_bytes": 16384
}
```

**Logging levels / 日志级别:**
```json
"logging": {
  "level": "WARNING",  // ERROR, WARNING, INFO, DEBUG
  "file": null,        // or "monitor.log" to save to file
  "console": true
}
```

- `ERROR` - Only errors / 仅错误
- `WARNING` - Warnings and errors (default) / 警告和错误（默认）
- `INFO` - Detailed information / 详细信息
- `DEBUG` - All debug information / 所有调试信息

---

## Features / 功能详解

### File Organization / 文件整理

Automatically categorizes files into folders:
- **Programs**: .exe, .msi, .bat, .cmd, .ps1
- **Compressed**: .zip, .rar, .7z, .tar, .gz, .iso
- **Documents**: .pdf, .doc, .docx, .txt, .xls, .ppt
- **Pictures**: .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff
- **Music**: .mp3, .wav, .flac, .aac, .ogg, .m4a
- **Video**: .mp4, .avi, .mkv, .mov, .wmv, .webm

### File Analysis / 文件分析

Built-in extensions provide:
- **File type distribution** - Shows breakdown by extension
- **File size analysis** - Categorizes by size (Tiny, Small, Medium, Large, Huge)
- **Change detection** - Tracks new, modified, and deleted files

### CSV Export / CSV 导出

Generates `results.csv` with columns:
- `path` - File path relative to Downloads
- `rel_path` - Relative path
- `folder_name` - Category folder
- `filename` - File name
- `sha1sum` - SHA1 hash
- `timestamp` - Legacy timestamp (YY/MM/DD)
- `mtime_iso` - ISO8601 timestamp

---

## Project Structure / 项目结构

```
downloads-monitor/
├── app.py                  # Main entry point
├── file_monitor.py         # File scanning & CSV management
├── file_organizer.py       # File organization logic
├── extensions.py           # Analysis extensions
├── config_manager.py       # Configuration management
├── config.json             # User configuration
├── start.bat               # Windows launcher
├── pyproject.toml          # Project metadata
├── requirements.txt        # Dependencies (none)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## Changelog / 更新日志

### v2.0.0 (2024-11-14) - Major Update

**Added / 新增:**
- ✨ JSON-based configuration system
- ✨ Comprehensive logging with configurable levels (DEBUG, INFO, WARNING, ERROR)
- ✨ Full type hints throughout codebase
- ✨ Dry-run mode for previewing changes (`--dry-run`)
- ✨ Configurable SHA1 calculation with file size limits
- ✨ Enhanced error handling with permission checks
- ✨ Configuration manager module

**Changed / 更改:**
- 🔧 Refactored all modules with type hints and logging
- 🔧 Improved CSV deduplication logic
- 🔧 Enhanced file scanning with configurable exclusions
- 🔧 Better timestamp handling (ISO8601 format)
- 📝 Comprehensive documentation

**Removed / 移除:**
- ❌ WSL2 support (Windows-only now)
- ❌ Print statements (replaced with logging)
- ❌ Legacy code and unused functions

**Performance / 性能:**
- ⚡ Configurable SHA1 chunk sizes
- ⚡ Skip SHA1 for large files
- ⚡ Improved scanning efficiency
- ⚡ Better memory usage

### v1.0.0 (2024-11-01) - Initial Release

- Initial release with basic monitoring
- SHA1 calculation and CSV output
- File organization by category
- Extension system for analysis

---

## Troubleshooting / 故障排除

### Common Issues / 常见问题

**Q: Garbled output / 输出乱码**
```bash
# Set console encoding to UTF-8
chcp 65001
python app.py
```

**Q: Permission errors / 权限错误**
- Run as Administrator
- Check folder permissions
- Close programs using the files

**Q: Files not organized / 文件未整理**
- Check `config.json` - ensure `auto_organize` is `true`
- Verify file extensions are in categories
- Run `python app.py --dry-run` to preview

**Q: SHA1 is slow / SHA1 计算慢**
- Reduce `max_file_size_for_sha1_mb` in config
- Increase `chunk_size_bytes`
- Disable SHA1: `"calculate_sha1": false`

### Debug Mode / 调试模式

```bash
# Enable debug logging
python app.py --log-level DEBUG --log-file debug.log

# Preview without moving files
python app.py --dry-run

# Check system info
python app.py --info
```

---

## Performance / 性能

### Benchmarks / 基准测试

- **Small files (< 1MB)**: ~100 files/second
- **Medium files (1-100MB)**: ~10 files/second
- **Large files (> 100MB)**: Configurable (can skip SHA1)
- **Memory usage**: ~50-100 MB

### Tuning Tips / 调优建议

**For many small files / 大量小文件:**
```json
{
  "performance": {
    "chunk_size_bytes": 16384,
    "max_file_size_for_sha1_mb": 50
  }
}
```

**For speed / 追求速度:**
```json
{
  "monitoring": {
    "calculate_sha1": false
  }
}
```

---

## Advanced Usage / 高级使用

### Scheduled Tasks / 计划任务

**Windows Task Scheduler:**
1. Open Task Scheduler (`Win + R` → `taskschd.msc`)
2. Create Basic Task
3. Set trigger (e.g., daily at 9 AM)
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `"C:\path\to\app.py"`
   - Start in: `C:\path\to\downloads-monitor`

### Batch Scripts / 批处理脚本

**quick_scan.bat:**
```batch
@echo off
cd /d "%~dp0"
python app.py --no-ext
pause
```

**continuous_monitor.bat:**
```batch
@echo off
cd /d "%~dp0"
python app.py --continuous 300
```

---

## Contributing / 贡献

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

欢迎贡献！

---

## License / 许可证

MIT License - Free to use, modify, and distribute.

MIT 许可证 - 可自由使用、修改和分发。

---

## Support / 支持

- 📖 Documentation: This README
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Version**: 2.0.0  
**Last Updated**: 2024-11-14  
**Status**: Production Ready ✅  
**Platform**: Windows 10/11 64-bit  
**Python**: 3.8+  
**Dependencies**: None (standard library only)
