# Downloads Folder Monitor / 下载文件夹监控器

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://microsoft.com/windows)

Windows 原生 Python 命令行工具，通过自动文件分类、SHA1 跟踪和智能规则匹配，保持下载文件夹的整洁有序。

---

## 功能特性

- 🗂️ **自动文件整理** - 按扩展名分类到 6 个文件夹
- 🧠 **智能分类规则** - 支持文件名模式匹配（如 `screenshot*` → Pictures）
- ⚡ **增量扫描** - 仅对变化的文件计算 SHA1，大幅提升性能
- 📊 **SHA1 跟踪** - 文件哈希计算，用于重复检测和完整性验证
- 📝 **CSV 导出** - 维护可搜索的文件数据库
- 🔍 **文件分析** - 内置扩展：文件类型分布、大小分析、变更检测、重复检测
- ⚙️ **JSON 配置** - 通过 config.json 灵活配置
- 🚀 **零依赖** - 仅使用 Python 标准库

## 快速开始

```bash
# 运行监控
python app.py

# 详细输出
python app.py --log-level INFO

# 预览模式（不移动文件）
python app.py --dry-run

# 显示系统信息
python app.py --info

# 显示清理建议
python app.py --cleanup
```

## 命令行选项

| 选项 | 说明 |
|------|------|
| `-c, --continuous [秒]` | 持续监控模式（默认 60 秒间隔） |
| `--dry-run` | 预览模式，不实际移动文件 |
| `--no-ext` | 禁用扩展分析 |
| `--ext-only` | 仅运行扩展分析 |
| `--cleanup` | 显示重复文件清理建议 |
| `--downloads-path` | 自定义下载文件夹路径 |
| `--csv-path` | 自定义 CSV 输出路径 |
| `--config` | 指定配置文件路径 |
| `--log-level` | 日志级别 (DEBUG/INFO/WARNING/ERROR) |
| `--log-file` | 日志输出文件 |
| `--info, -i` | 显示系统信息 |

## 配置文件

`config.json` 首次运行时自动创建：

```json
{
  "downloads_path": null,
  "csv_path": "results.csv",
  "monitoring": {
    "interval_seconds": 60,
    "enable_extensions": true,
    "calculate_sha1": true,
    "incremental_scan": true
  },
  "organization": {
    "auto_organize": true,
    "categories": {
      "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1"],
      "Documents": [".pdf", ".doc", ".docx", ".txt", "..."],
      "Pictures": [".jpg", ".jpeg", ".png", ".gif", "..."],
      "Videos": [".mp4", ".avi", ".mkv", "..."],
      "Compressed": [".zip", ".rar", ".7z", "..."],
      "Music": [".mp3", ".wav", ".flac", "..."]
    },
    "excluded_files": ["results.csv", "desktop.ini", "Thumbs.db"],
    "smart_rules": [
      {"pattern": "screenshot*", "category": "Pictures"},
      {"pattern": "*setup*", "category": "Programs"},
      {"pattern": "*installer*", "category": "Programs"}
    ]
  },
  "performance": {
    "max_file_size_for_sha1_mb": 500,
    "chunk_size_bytes": 32768
  },
  "logging": {
    "level": "WARNING",
    "file": null,
    "console": true
  }
}
```

### 智能分类规则

`smart_rules` 支持通配符模式匹配，优先级高于扩展名匹配：

```json
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
```

### 增量扫描

启用 `incremental_scan` 后，工具会比较文件时间戳，跳过未修改文件的 SHA1 计算：

```
Incremental scan enabled, 42 existing records indexed
Incremental scan: 42 unchanged files skipped SHA1 calculation
```

## 文件分类

| 分类 | 扩展名 |
|------|--------|
| Programs | .exe, .msi, .bat, .cmd, .ps1 |
| Documents | .pdf, .doc, .docx, .txt, .md, .csv, .xls, .xlsx, .ppt, .pptx, .py, .js, .html, .css, .json... |
| Pictures | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff, .ttf, .otf... |
| Videos | .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm |
| Compressed | .zip, .rar, .7z, .tar, .gz, .bz2, .xz, .iso, .torrent |
| Music | .mp3, .wav, .flac, .aac, .ogg, .m4a |

## 项目结构

```
downloads-monitor/
├── app.py              # 主程序入口
├── file_monitor.py     # 文件扫描、SHA1 计算、CSV 管理
├── file_organizer.py   # 文件整理逻辑
├── extensions.py       # 分析扩展（类型、大小、变更）
├── duplicate_detector.py # 重复文件检测
├── progress_tracker.py # 进度条显示
├── config_manager.py   # 配置管理
├── config.json         # 用户配置
├── start.bat           # 交互式启动脚本
├── start_daily.bat     # 定时任务启动脚本
└── logs/               # 日志目录
```

## 定时任务

使用 Windows 任务计划程序：

1. 打开任务计划程序：`Win + R` → `taskschd.msc`
2. 创建基本任务，设置每日触发
3. 操作：启动程序 `cmd.exe`
4. 参数：`/c "C:\path\to\start_daily.bat"`
5. 起始位置：`C:\path\to\downloads-monitor`

## 系统要求

- Windows 10/11 64-bit
- Python 3.8+
- 无外部依赖

## 更新日志

### v2.1.0 (2024-12-16)
- ✨ 新增智能分类规则（文件名模式匹配）
- ⚡ 新增增量扫描（跳过未修改文件的 SHA1 计算）
- 🗑️ 移除未使用的 file_watcher.py
- 📦 代码精简约 43%（2200+ → 1244 行）

### v2.0.3 (2024-12-10)
- 架构优化，消除重复代码
- SHA1 计算性能优化
- 完善类型提示

---

**License**: MIT
