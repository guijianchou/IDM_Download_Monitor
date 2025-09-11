# Downloads Folder Monitor | 下载文件夹监控工具

> **🚀 Complete monitoring solution for Windows Downloads folder with GUI and CLI interfaces**  
> **🚀 Windows 下载文件夹的完整监控解决方案，支持图形界面和命令行**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-green)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**✨ Choose Your Interface | 选择您的界面:**
- **🖥️ GUI**: `start_gui.bat` - Quick GUI launcher | 快速 GUI 启动器
- **⚡ CLI**: `python app.py` - Command-line interface | 命令行界面  
- **🚀 Menu**: `start.bat` - Full menu launcher | 全功能菜单启动器

[English](#english) | [中文](#chinese)

---

## English

### 🎯 Overview
A comprehensive Python-based monitoring solution for Windows Downloads folder with both **modern GUI** and **powerful CLI** interfaces. Tracks SHA1 hashes, modification timestamps, and provides intelligent file organization with extensible analysis capabilities.

### ✨ Key Features

#### 🖥️ **Dual Interface Support**
- **Modern GUI Application**: Tkinter-based Windows-native interface with real-time monitoring
- **Powerful CLI Tool**: Full-featured command-line interface with advanced options
- **Unified Launcher**: Menu-driven batch script for easy access to all features

#### 📁 **File Management**
- **Real-time Monitoring**: Track file changes with SHA1 hashes and timestamps
- **Smart Organization**: Automatically categorize files (Programs, Documents, Music, Video, Compressed)
- **Custom Folder Support**: Monitor any folder, not just Downloads
- **Duplicate Prevention**: SHA1-based deduplication when files are moved

#### 🔧 **Advanced Features**
- **Extension System**: Built-in file analysis (type, size, change detection)
- **Enhanced CSV Export**: 7-column format with full compatibility
- **System Integration**: Windows-native with WSL2 support
- **Encoding Safety**: Full UTF-8 support with proper error handling
- **Cache Management**: Built-in cleanup utilities

#### 🛡️ **Reliability**
- **No External Dependencies**: Uses only Python standard library
- **Error Resilience**: Graceful handling of locked files and permissions
- **Data Integrity**: Incremental updates preserve existing records
- **Cross-Environment**: Works on Windows 10/11 and WSL2

### 📁 Project Structure
```
Monitor/
├── gui_app.py          # 🖥️ Modern GUI application (Tkinter-based)
├── settings_window.py  # ⚙️ GUI settings and configuration dialog
├── app.py              # ⚡ CLI application with advanced features
├── file_monitor.py     # 🔍 Core file monitoring and SHA1 calculation
├── file_organizer.py   # 📁 Automatic file categorization system
├── extensions.py       # 🔌 Extension system and analysis tools
├── start.bat           # 🚀 Windows batch launcher (menu-driven)
├── start_gui.bat       # 🖥️ Quick GUI launcher (direct access)
├── cleanup_cache.py   # 🧹 Cache cleanup utility
├── check_encoding.py  # ✅ Encoding verification tool
├── pyproject.toml      # 📄 Project configuration
├── requirements.txt    # 📎 Dependencies specification
├── README.md           # 📚 This documentation file
├── .gitignore          # 🚫 Git ignore rules
└── .venv/              # 📦 Virtual environment (auto-created)
```

### 🚀 Quick Start

#### Option 1: Quick GUI Launcher (Recommended)
```cmd
# Windows Command Prompt or PowerShell
start_gui.bat
```
Direct access to GUI with feature overview and launch confirmation.

#### Option 2: Full Menu Launcher
```cmd
# Windows Command Prompt or PowerShell
start.bat
```
Choose from 9 menu options including GUI, CLI, debug mode, and maintenance tools.

#### Option 3: Direct Launch
```bash
# Modern GUI Application (Recommended for most users)
python gui_app.py

# Command-Line Interface (For automation and advanced users)
python app.py

# System information
python app.py --info
```

### 📺 Installation

#### Prerequisites
- **Python 3.8+** (Windows 10/11 compatible)
- **No external dependencies** (uses standard library only)

#### Setup Steps
1. **Download/Clone** the project to your desired location
2. **Open terminal** in project directory
3. **Run launcher** or use Python directly:
   ```cmd
   start.bat              # Menu-driven launcher
   python gui_app.py      # Direct GUI launch
   python app.py --help   # CLI help
   ```

#### Optional: Virtual Environment
```bash
# Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate    # Windows

# Install dev dependencies (optional)
pip install -r requirements.txt
```

### 📚 Usage Guide

#### 🖥️ GUI Application (Recommended)
The GUI provides an intuitive interface for all monitoring features:

```bash
python gui_app.py
```

**GUI Features:**
- 📈 **Real-time Dashboard**: File counts, last scan time, monitoring status
- 📁 **File Browser**: View recent files with details (path, size, modification time)
- 📊 **Statistics Tab**: File type analysis, folder distribution, insights
- 📝 **Logs Tab**: Real-time application logs with export functionality
- ⚙️ **Settings**: Configurable monitoring options and paths
- 📂 **Custom Folders**: Monitor any directory beyond Downloads
- ▶️ **Control Panel**: Start/stop monitoring, single scan, file organization

#### ⚡ CLI Application (Advanced)
Full-featured command-line interface for automation and scripting:

##### Basic Operations
```bash
# Single scan with file organization and analysis
python app.py

# Monitor without extensions
python app.py --no-ext

# Run analysis on existing data
python app.py --ext-only

# System information
python app.py --info
```

##### Continuous Monitoring
```bash
# Monitor with 60-second intervals (default)
python app.py --continuous

# Custom interval (30 seconds)
python app.py --continuous 30
```

##### Advanced Configuration
```bash
# Custom paths
python app.py --downloads-path "C:\Path\To\Folder" --csv-path "C:\Path\output.csv"

# Debug logging to file
python app.py --log-level DEBUG --log-file monitor.log

# Combine multiple options
python app.py --continuous 45 --log-level INFO --no-ext
```

#### 🚀 Batch Launcher (Easy Access)
Menu-driven launcher with 9 options:

```cmd
start.bat
```

**Launcher Menu:**
1. 🖥️ **GUI Application** - Start modern interface
2. ⚡ **CLI Application** - Command-line single scan
3. 🔍 **GUI Debug** - GUI with detailed console output
4. 🔄 **Continuous CLI** - CLI with custom interval monitoring
5. 🔌 **Extensions Only** - Run analysis on existing data
6. ℹ️ **System Info** - Display system information
7. 📦 **Dependencies** - Install/update packages
8. 🧹 **Clean Cache** - Remove Python cache files
9. 🚪 **Exit** - Close launcher

### File Organization System

The tool automatically organizes files into categorized folders based on their file extensions:

#### Supported Categories
- **Programs**: `.exe`, `.msi`, `.bat`, `.cmd`, `.com`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Music**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`
- **Video**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`
- **Compressed**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`

#### Organization Process
1. **Scan**: Identifies files in the Downloads root directory
2. **Categorize**: Determines appropriate category based on file extension
3. **Create Folders**: Automatically creates category folders if they don't exist
4. **Move Files**: Moves files to their respective category folders
5. **Update Records**: Updates CSV records with new file locations
6. **Deduplication**: Prevents duplicate SHA1 entries when files are moved

### 📝 CSV Data Format
The tool generates a comprehensive `results.csv` file with enhanced format:

```csv
path,rel_path,folder_name,filename,sha1sum,timestamp,mtime_iso
~\Programs\installer.exe,Programs/installer.exe,Programs,installer.exe,a1b2c3d4e5f6...,25/01/15,2025-01-15T14:30:25
~\Documents\report.pdf,Documents/report.pdf,Documents,report.pdf,f6e5d4c3b2a1...,25/01/15,2025-01-15T09:15:42
~\archive.zip,archive.zip,~,archive.zip,9f8e7d6c5b4a...,25/01/15,2025-01-15T16:45:10
```

**Column Details:**
| Column | Description | Example |
|--------|-------------|----------|
| `path` | Legacy Windows path format | `~\Documents\file.pdf` |
| `rel_path` | POSIX relative path | `Documents/file.pdf` |
| `folder_name` | Category folder (or `~` for root) | `Documents` |
| `filename` | File name only | `file.pdf` |
| `sha1sum` | SHA1 hash for integrity | `a1b2c3d4e5f6...` |
| `timestamp` | Legacy date format (YY/MM/DD) | `25/01/15` |
| `mtime_iso` | ISO8601 modification time | `2025-01-15T14:30:25` |

**Benefits:**
- 🔄 **Backward Compatible**: Works with existing CSV processors
- 🔍 **Detailed Tracking**: Multiple path formats for flexibility
- ⏱️ **Precise Timestamps**: Second-level accuracy for change detection
- 🔒 **Data Integrity**: SHA1 hashes prevent duplicate entries

### How It Works
1. **Path Detection**: Automatically detects Downloads folder path
2. **File Organization**: Categorizes files into organized folders (Programs, Documents, Music, Video, Compressed)
3. **File Scanning**: Recursively scans all files and subdirectories
4. **Hash Calculation**: Computes SHA1 hash for each file
5. **Timestamp Extraction**: Gets last modification time
6. **Data Update**: Compares with existing data, updates changes with SHA1 deduplication
7. **CSV Export**: Saves results to Downloads folder
8. **Extension Analysis**: Runs additional analysis if enabled

### Modular Architecture

#### Core Classes
- **`DownloadsMonitor`**: Main monitoring class
- **`ContinuousMonitor`**: Handles continuous monitoring
- **`ExtensionManager`**: Manages analysis extensions
- **`FileOrganizer`**: Handles file categorization and organization

#### Extension System
- **`FileTypeAnalyzer`**: Analyzes file extensions and distribution
- **`FileSizeAnalyzer`**: Categorizes files by size
- **`ChangeDetector`**: Identifies new, modified, and deleted files

#### Adding Custom Extensions
```python
class CustomAnalyzer:
    def analyze(self, data, previous_data=None):
        # Your analysis logic here
        pass
    
    def get_results(self):
        return {"custom_metric": "value"}

# Register in ExtensionManager
extension_manager.register_extension(CustomAnalyzer())
```

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Windows 10/11 or WSL2
- **Dependencies**: Uses only Python standard library (no external dependencies)

### What's New in v0.2.0

#### 🔧 Critical Fixes
- **FileSizeAnalyzer**: Fixed incorrect label "Small (1MB - 1MB)" → "Small (1KB - 1MB)"
- **Timestamp Precision**: Upgraded from YY/MM/DD to ISO8601 (YYYY-MM-DDTHH:MM:SS) for better accuracy
- **Extension Data**: Fixed full_path reconstruction for FileSizeAnalyzer and other extensions
- **Dependencies**: Removed incorrect standard library entries from pyproject.toml

#### ✨ New Features
- **Enhanced CLI**: Modern argparse-based interface with `--log-level`, `--log-file`, path overrides
- **Structured Logging**: Configurable log levels with optional file output
- **Better WSL2 Support**: Auto-detection with `MONITOR_WIN_USERNAME` environment variable override
- **Enhanced CSV**: Additional columns (rel_path, folder_name, filename, mtime_iso) while maintaining compatibility
- **Improved Scripts**: Enhanced PowerShell startup script with dependency management

#### 🚀 Performance Improvements
- **Precise Timestamps**: Better file change detection with second-level accuracy
- **Robust Path Detection**: More reliable WSL2 path resolution with fallbacks
- **Better Error Handling**: Timeout protection and graceful degradation

### WSL2 Configuration

For WSL2 users with non-default Windows usernames:

```bash
# Set in WSL2 ~/.bashrc or ~/.profile
export MONITOR_WIN_USERNAME=YourWindowsUsername

# Then run monitoring
python app.py
```

Or use command-line override:
```bash
python app.py --downloads-path "/mnt/c/Users/YourUser/Downloads"
```

### Migration from v0.1.x

Existing CSV files are automatically compatible. To take advantage of new features:

1. **Backup existing data**: `copy results.csv results_backup.csv`
2. **Run once with logging**: `python app.py --log-level DEBUG`
3. **Verify new format**: Check that `results.csv` now has 7 columns instead of 3
4. **Set WSL2 username** (if needed): `export MONITOR_WIN_USERNAME=YourUser`

The application now includes comprehensive built-in help and documentation.

### Notes
- CSV file is automatically saved to Downloads folder
- System files (`desktop.ini`) are automatically excluded
- Supports both Windows native and WSL2 environments
- Extensions provide additional analysis capabilities
- Data is updated incrementally, preserving existing records
- File organization runs automatically during monitoring cycles
- SHA1 deduplication prevents duplicate entries when files are moved
- Category folders are created automatically as needed
- Backward compatible with v0.1.x CSV format

---

## 中文

### 🎯 概述
针对Windows下载文件夹的全面Python监控解决方案，同时支持**现代化GUI**和**强大CLI**界面。跟踪SHA1哈希值、修改时间戳，并提供智能文件组织和可扩展分析功能。

### ✨ 主要特性

#### 🖥️ **双界面支持**
- **现代化GUI应用**: 基于Tkinter的Windows原生GUI，支持实时监控
- **强大CLI工具**: 功能齐全的命令行界面，支持高级选项
- **统一启动器**: 菜单式批处理脚本，轻松访问所有功能

#### 📁 **文件管理**
- **实时监控**: 通过SHA1哈希和时间戳跟踪文件变化
- **智能组织**: 自动分类文件（程序、文档、音乐、视频、压缩文件）
- **自定义文件夹**: 支持监控任意目录，不仅限于下载文件夹
- **重复防止**: 基于SHA1的去重，防止文件移动时产生重复

#### 🔧 **高级功能**
- **扩展系统**: 内置文件分析（类型、大小、变更检测）
- **增强型CSV导出**: 7列格式，完全兼容
- **系统集成**: Windows原生支持，兼容WSL2
- **编码安全**: 完整UTF-8支持，正确的错误处理
- **缓存管理**: 内置清理工具

#### 🛡️ **可靠性**
- **无外部依赖**: 仅使用Python标准库
- **错误弹性**: 优雅处理文件锁定和权限问题
- **数据完整性**: 增量更新，保留现有记录
- **跨环境**: 支持Windows 10/11和WSL2

### 📁 项目结构
```
Monitor/
├── gui_app.py          # 🖥️ 现代化GUI应用（基于Tkinter）
├── settings_window.py  # ⚙️ GUI设置和配置对话框
├── app.py              # ⚡ 高级功能CLI应用
├── file_monitor.py     # 🔍 核心文件监控和SHA1计算
├── file_organizer.py   # 📁 自动文件分类系统
├── extensions.py       # 🔌 扩展系统和分析工具
├── start.bat           # 🚀 Windows批处理启动器（菜单式）
├── start_gui.bat       # 🖥️ 快速GUI启动器（直接访问）
├── cleanup_cache.py   # 🧹 缓存清理工具
├── check_encoding.py  # ✅ 编码验证工具
├── pyproject.toml      # 📄 项目配置
├── requirements.txt    # 📎 依赖规范
├── README.md           # 📚 本文档文件
├── .gitignore          # 🚫 Git忽略规则
└── .venv/              # 📦 虚拟环境（自动创建）
```

### 🚀 快速开始

#### 方式一：快速GUI启动器（推荐）
```cmd
# Windows 命令提示符或 PowerShell
start_gui.bat
```
直接启动GUI，包含功能介绍和启动确认。

#### 方式二：全功能菜单启动器
```cmd
# Windows 命令提示符或 PowerShell
start.bat
```
从9个菜单选项中选择，包括GUI、CLI、调试模式和维护工具。

#### 方式三：直接启动
```bash
# 现代化GUI应用（大多数用户推荐）
python gui_app.py

# 命令行界面（适用于自动化和高级用户）
python app.py

# 系统信息
python app.py --info
```

### 📺 安装方法

#### 系统要求
- **Python 3.8+**（兼容Windows 10/11）
- **无外部依赖**（仅使用标准库）

#### 安装步骤
1. **下载/克隆**项目到您的目标位置
2. **打开终端**在项目目录中
3. **运行启动器**或直接使用Python：
   ```cmd
   start.bat              # 菜单式启动器
   python gui_app.py      # 直接启动GUI
   python app.py --help   # CLI帮助
   ```

#### 可选：虚拟环境
```bash
# 创建虚拟环境（可选）
python -m venv .venv
.venv\Scripts\activate    # Windows

# 安装开发依赖（可选）
pip install -r requirements.txt
```

### 📚 使用指南

#### 🖥️ GUI应用（推荐）
GUI为所有监控功能提供直观的界面：

```bash
python gui_app.py
```

**GUI功能：**
- 📈 **实时仪表板**：文件计数、上次扫描时间、监控状态
- 📁 **文件浏览器**：查看最近文件和详细信息（路径、大小、修改时间）
- 📊 **统计选项卡**：文件类型分析、文件夹分布、洞察
- 📝 **日志选项卡**：实时应用程序日志和导出功能
- ⚙️ **设置**：可配置的监控选项和路径
- 📂 **自定义文件夹**：监控下载文件夹以外的任意目录
- ▶️ **控制面板**：启动/停止监控、单次扫描、文件组织

#### ⚡ CLI应用（高级）
用于自动化和脚本的功能齐全命令行界面：

##### 基本操作
```bash
# 单次扫描并进行文件组织和分析
python app.py

# 不使用扩展的监控
python app.py --no-ext

# 对现有数据运行分析
python app.py --ext-only

# 系统信息
python app.py --info
```

##### 连续监控
```bash
# 以60秒间隔监控（默认）
python app.py --continuous

# 自定义间隔（30秒）
python app.py --continuous 30
```

##### 高级配置
```bash
# 自定义路径
python app.py --downloads-path "C:\Path\To\Folder" --csv-path "C:\Path\output.csv"

# 调试日志到文件
python app.py --log-level DEBUG --log-file monitor.log

# 组合多个选项
python app.py --continuous 45 --log-level INFO --no-ext
```

#### 🚀 批处理启动器（简单访问）
拥月9个选项的菜单式启动器：

```cmd
start.bat
```

**启动器菜单：**
1. 🖥️ **GUI应用** - 启动现代界面
2. ⚡ **CLI应用** - 命令行单次扫描
3. 🔍 **GUI调试** - 带详细控制台输出的GUI
4. 🔄 **连续 CLI** - 带自定义间隔监控的CLI
5. 🔌 **仅扩展** - 对现有数据运行分析
6. ℹ️ **系统信息** - 显示系统信息
7. 📦 **依赖管理** - 安装/更新包
8. 🧹 **缓存清理** - 移除Python缓存文件
9. 🚪 **退出** - 关闭启动器

### 文件组织系统

工具根据文件扩展名自动将文件组织到分类文件夹中：

#### 支持的分类
- **程序**: `.exe`, `.msi`, `.bat`, `.cmd`, `.com`
- **文档**: `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **音乐**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`
- **视频**: `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`
- **压缩文件**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`

#### 组织过程
1. **扫描**: 识别Downloads根目录中的文件
2. **分类**: 根据文件扩展名确定适当的类别
3. **创建文件夹**: 如果不存在，自动创建分类文件夹
4. **移动文件**: 将文件移动到相应的分类文件夹
5. **更新记录**: 使用新文件位置更新CSV记录
6. **去重**: 防止文件移动时产生重复的SHA1条目

### CSV文件格式
工具在Downloads文件夹中生成增强且向后兼容的 `results.csv` 文件：

```csv
path,rel_path,folder_name,filename,sha1sum,timestamp,mtime_iso
~\\Programs\\filename.exe,Programs/filename.exe,Programs,filename.exe,sha1_hash_value,25/08/27,2025-08-27T12:34:56
~\\Documents\\file.pdf,Documents/file.pdf,Documents,file.pdf,sha1_hash_value,25/08/27,2025-08-27T12:35:10
```

- **path**: 旧版路径 `~\\folder\\name`（保留兼容）
- **rel_path**: 相对 Downloads 的路径（POSIX 风格）
- **folder_name**: 分类文件夹（根目录为 `~`）
- **filename**: 仅文件名
- **sha1sum**: 文件的SHA1哈希值
- **timestamp**: 兼容用的旧日期（YY/MM/DD）
- **mtime_iso**: 精确的ISO8601时间（YYYY-MM-DDTHH:MM:SS）

### 工作原理
1. **路径检测**: 自动检测Downloads文件夹路径
2. **文件组织**: 将文件分类到有组织的文件夹中（程序、文档、音乐、视频、压缩文件）
3. **文件扫描**: 递归扫描所有文件和子目录
4. **哈希计算**: 计算每个文件的SHA1哈希值
5. **时间戳提取**: 获取最后修改时间
6. **数据更新**: 与现有数据比较，使用SHA1去重更新变更
7. **CSV导出**: 将结果保存到Downloads文件夹
8. **扩展分析**: 如果启用，运行额外分析

### 模块化架构

#### 核心类
- **`DownloadsMonitor`**: 主监控类
- **`ContinuousMonitor`**: 处理连续监控
- **`ExtensionManager`**: 管理分析扩展
- **`FileOrganizer`**: 处理文件分类和组织

#### 扩展系统
- **`FileTypeAnalyzer`**: 分析文件扩展名和分布
- **`FileSizeAnalyzer`**: 按大小分类文件
- **`ChangeDetector`**: 识别新增、修改和删除的文件

#### 添加自定义扩展
```python
class CustomAnalyzer:
    def analyze(self, data, previous_data=None):
        # 您的分析逻辑
        pass
    
    def get_results(self):
        return {"custom_metric": "value"}

# 在ExtensionManager中注册
extension_manager.register_extension(CustomAnalyzer())
```

### 系统要求
- **Python**: 3.8或更高版本
- **操作系统**: Windows 10/11或WSL2
- **依赖**: 仅使用Python标准库（无外部依赖）

### v0.2.0 新特性

#### 🔧 关键修复
- **FileSizeAnalyzer**: 修正错误标签 "Small (1MB - 1MB)" → "Small (1KB - 1MB)"
- **时间戳精度**: 从 YY/MM/DD 升级到 ISO8601 (YYYY-MM-DDTHH:MM:SS)，提高准确性
- **扩展数据**: 修复 full_path 重构，供 FileSizeAnalyzer 等扩展使用
- **依赖管理**: 从 pyproject.toml 中移除错误的标准库条目

#### ✨ 新功能
- **增强CLI**: 现代化 argparse 接口，支持 `--log-level`、`--log-file`、路径覆盖
- **结构化日志**: 可配置日志级别与可选文件输出
- **更好的WSL2支持**: 自动检测，支持 `MONITOR_WIN_USERNAME` 环境变量覆盖
- **增强CSV**: 新增列（rel_path, folder_name, filename, mtime_iso）同时保持兼容性
- **改进脚本**: 增强的 PowerShell 启动脚本，支持依赖管理

#### 🚀 性能改进
- **精确时间戳**: 基于秒级精度的更佳文件变更检测
- **健壮路径检测**: 更可靠的 WSL2 路径解析与回退机制
- **更好的错误处理**: 超时保护与优雅降级

### WSL2 配置

对于使用非默认 Windows 用户名的 WSL2 用户：

```bash
# 在 WSL2 ~/.bashrc 或 ~/.profile 中设置
export MONITOR_WIN_USERNAME=你的Windows用户名

# 然后运行监控
python app.py
```

或使用命令行覆盖：
```bash
python app.py --downloads-path "/mnt/c/Users/你的用户名/Downloads"
```

### 从 v0.1.x 迁移

现有 CSV 文件自动兼容。要使用新功能：

1. **备份现有数据**: `copy results.csv results_backup.csv`
2. **带日志运行一次**: `python app.py --log-level DEBUG`
3. **验证新格式**: 检查 `results.csv` 现在有7列而不是3列
4. **设置WSL2用户名**（如需要）: `export MONITOR_WIN_USERNAME=你的用户名`

应用程序现在包含全面的内置帮助和文档。

### 注意事项
- CSV文件自动保存到Downloads文件夹
- 系统文件（`desktop.ini`）自动排除
- 支持Windows原生和WSL2环境
- 扩展提供额外的分析功能
- 数据增量更新，保留现有记录
- 文件组织在监控周期中自动运行
- SHA1去重防止文件移动时产生重复条目
- 分类文件夹根据需要自动创建
- 向后兼容 v0.1.x CSV 格式

---

## 🚀 Getting Started | 快速开始

**English**: Ready to monitor your Downloads folder? Just run `start.bat` and choose option 1 for the GUI!  
**中文**: 准备好监控您的下载文件夹了吗？运行`start.bat`并选择选项1启动GUI！

## 🤝 Contributing | 贡献

**English**: Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.  
**中文**: 欢迎贡献！请随时提交问题、功能请求或拉取请求。

## 📞 Support | 支持

**English**: If you encounter any issues or have questions, please check the documentation or create an issue on GitHub.  
**中文**: 如果您遇到任何问题或有疑问，请查阅文档或在GitHub上创建问题。

---

## 📜 License | 许可证

**MIT License** - Free for personal and commercial use

Copyright (c) 2025 Downloads Folder Monitor

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
