# Downloads Folder Monitoring Tool
# 下载文件夹监控工具

[English](#english) | [中文](#chinese)

---

## English

### Overview
A Python-based tool for monitoring the Windows Downloads folder, tracking SHA1 hashes and modification timestamps of all files and subdirectories. Supports both Windows native and WSL2 environments with an extensible architecture.

### Features
- **File Monitoring**: Tracks SHA1 hashes and modification timestamps
- **File Organization**: Automatically categorizes files into organized folders
- **Directory Structure**: Handles both root directory and subdirectory files
- **Automatic WSL2 Detection**: Seamlessly switches between Windows and WSL2 paths (improved username detection, env override via `MONITOR_WIN_USERNAME`)
- **Modular Architecture**: Easy to add new features and extensions
- **Built-in Analysis Extensions**: File type analysis, size analysis, and change detection
- **CSV Export (Enhanced)**: Now outputs `path, rel_path, folder_name, filename, sha1sum, timestamp, mtime_iso`
- **System File Exclusion**: Automatically excludes `desktop.ini` and `results.csv`
- **Smart SHA1 Deduplication**: Prevents duplicate entries when files are moved (better timestamp comparison)
- **Improved CLI & Logging**: Argparse-based flags (`--log-level`, `--log-file`, paths override) and structured logs
- **Windows Startup Script**: Enhanced `start.ps1` with venv setup and options

### Project Structure
```
.
├── app.py              # Main program entry point
├── file_monitor.py     # Core file monitoring and SHA1 calculation
├── file_organizer.py   # File organization and categorization system
├── extensions.py       # Extension system and analysis tools
├── pyproject.toml      # Project configuration (no external deps)
├── requirements.txt    # Dev dependencies (pytest, black, flake8)
├── README.md           # This file
├── MIGRATION.md        # Migration guide for new CSV/CLI/logging
├── start.ps1           # Enhanced PowerShell startup script (Windows)
├── start.bat           # Basic batch startup script (Windows)
└── .gitignore          # Git ignore rules
```

### Installation
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd apps
   ```

2. **Install dependencies using uv**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

### Usage

#### Basic Monitoring
```bash
# Execute monitoring once (with extensions)
python app.py

# Execute monitoring once (without extensions)
python app.py --no-ext

# Run only extensions (requires previous data)
python app.py --ext-only
```

#### Continuous Monitoring
```bash
# Continuous monitoring with 60s interval
python app.py -c

# Custom interval (30 seconds)
python app.py -c 30
```

#### System Information
```bash
# Show system information
python app.py --info

# Show help
python app.py --help
```

#### Advanced Options
```bash
# Override paths
python app.py --downloads-path "C:\\Users\\Me\\Downloads" --csv-path "C:\\Users\\Me\\Downloads\\results.csv"

# Logging
python app.py --log-level DEBUG --log-file monitor.log

# Run only extensions
python app.py --ext-only
```

#### PowerShell Startup (Windows)
```powershell
# Single run (default)
.\start.ps1

# Continuous monitoring with interval and logging
.\start.ps1 -Mode continuous -Interval 30 -LogLevel DEBUG

# System info mode
.\start.ps1 -Mode info
```

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

### CSV File Format
The tool generates a `results.csv` file in the Downloads folder using an enhanced, backward-compatible format:

```csv
path,rel_path,folder_name,filename,sha1sum,timestamp,mtime_iso
~\Programs\filename.exe,Programs/filename.exe,Programs,filename.exe,sha1_hash_value,25/08/27,2025-08-27T12:34:56
~\Documents\file.pdf,Documents/file.pdf,Documents,file.pdf,sha1_hash_value,25/08/27,2025-08-27T12:35:10
```

- **path**: Legacy path in `~\folder\name` format (kept for compatibility)
- **rel_path**: Path relative to the Downloads folder (POSIX style)
- **folder_name**: Category folder (or `~` for root)
- **filename**: File name only
- **sha1sum**: SHA1 hash of the file
- **timestamp**: Legacy date (YY/MM/DD) kept for compatibility
- **mtime_iso**: Precise last modification time in ISO8601 (YYYY-MM-DDTHH:MM:SS)

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

For detailed migration instructions, see [MIGRATION.md](MIGRATION.md).

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

### 概述
一个基于Python的Windows下载文件夹监控工具，跟踪所有文件和子目录的SHA1哈希值和修改时间戳。支持Windows原生和WSL2环境，具有可扩展的架构。

### 功能特性
- **文件监控**: 跟踪SHA1哈希值和修改时间戳
- **文件组织**: 自动将文件分类到有组织的文件夹中
- **目录结构**: 处理根目录和子目录文件
- **自动WSL2检测**: 在Windows和WSL2路径间无缝切换（改进用户名检测，支持 `MONITOR_WIN_USERNAME` 环境变量）
- **模块化架构**: 易于添加新功能和扩展
- **内置分析扩展**: 文件类型分析、大小分析和变更检测
- **CSV导出（增强）**: 现在输出 `path, rel_path, folder_name, filename, sha1sum, timestamp, mtime_iso`
- **系统文件排除**: 自动排除`desktop.ini`和`results.csv`
- **智能SHA1去重**: 防止文件移动时产生重复条目（改进时间戳比较）
- **改进的CLI与日志**: 基于 argparse 的参数（`--log-level`、`--log-file`、路径覆盖）与结构化日志
- **Windows 启动脚本**: 增强的 `start.ps1`，支持 venv 创建与参数选项

### 项目结构
```
.
├── app.py              # 主程序入口点
├── file_monitor.py     # 核心文件监控和SHA1计算
├── file_organizer.py   # 文件组织和分类系统
├── extensions.py       # 扩展系统和分析工具
├── pyproject.toml      # 项目配置（无外部依赖）
├── requirements.txt    # 开发依赖（pytest、black、flake8）
├── README.md           # 本文件
├── MIGRATION.md        # 迁移指南（新CSV/CLI/日志）
├── start.ps1           # 增强的 PowerShell 启动脚本（Windows）
├── start.bat           # 基础批处理启动脚本（Windows）
└── .gitignore          # Git忽略规则
```

### 安装
1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd apps
   ```

2. **使用uv安装依赖**
   ```bash
   uv sync
   ```

3. **运行应用程序**
   ```bash
   python app.py
   ```

### 使用方法

#### 基本监控
```bash
# 执行一次监控（启用扩展）
python app.py

# 执行一次监控（禁用扩展）
python app.py --no-ext

# 仅运行扩展（需要先有数据）
python app.py --ext-only
```

#### 连续监控
```bash
# 连续监控，60秒间隔
python app.py -c

# 自定义间隔（30秒）
python app.py -c 30
```

#### 系统信息
```bash
# 显示系统信息
python app.py --info

# 显示帮助
python app.py --help
```

#### 高级选项
```bash
# 覆盖路径
python app.py --downloads-path "C:\\Users\\Me\\Downloads" --csv-path "C:\\Users\\Me\\Downloads\\results.csv"

# 日志
python app.py --log-level DEBUG --log-file monitor.log

# 仅运行扩展
python app.py --ext-only
```

#### PowerShell 启动（Windows）
```powershell
# 单次运行（默认）
.\start.ps1

# 连续监控（设置间隔与日志）
.\start.ps1 -Mode continuous -Interval 30 -LogLevel DEBUG

# 系统信息模式
.\start.ps1 -Mode info
```

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

详细迁移说明请参见 [MIGRATION.md](MIGRATION.md)。

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

## License / 许可证

MIT License

Copyright (c) 2025 Downloads Folder Monitoring Tool

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
