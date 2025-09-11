# Windows 计划任务设置指南 | Daily Task Setup Guide

## 📋 文件说明 | File Description

### 🤖 `start_daily.bat` - 每日任务执行器
- **功能**: 完全后台运行下载文件夹监控
- **特点**: 无窗口显示，适合计划任务
- **日志**: 自动创建详细的执行日志
- **路径**: `logs/daily_YYYY-MM-DD_HH-MM.log`

### 📊 `view_daily_logs.bat` - 日志查看器
- **功能**: 查看和管理每日任务日志
- **选项**: 查看最新日志、浏览所有日志、清理旧日志
- **界面**: 用户友好的菜单驱动界面

## ⚙️ Windows 计划任务设置步骤 | Windows Task Scheduler Setup

### 第一步: 打开任务计划程序
1. 按 `Win + R`，输入 `taskschd.msc`，按回车
2. 或者在开始菜单搜索"任务计划程序"

### 第二步: 创建基本任务
1. 在右侧操作面板点击"创建基本任务"
2. 输入任务名称: `Downloads Monitor Daily`
3. 输入描述: `Daily monitoring of Downloads folder`

### 第三步: 设置触发器
1. 选择"每天"
2. 设置开始时间: 建议 `02:00:00` (凌晨2点)
3. 设置重复间隔: `每 1 天`

### 第四步: 设置操作
1. 选择"启动程序"
2. **程序或脚本**: `C:\Users\Zen\Codings\Monitor\start_daily.bat`
3. **起始于**: `C:\Users\Zen\Codings\Monitor`

### 第五步: 高级设置
在任务完成后，右键点击任务 → "属性"，进行以下设置:

#### "常规"选项卡:
- ✅ **无论用户是否登录都要运行**
- ✅ **使用最高权限运行**
- ✅ **配置**: Windows 10

#### "条件"选项卡:
- ❌ 取消勾选"只有在计算机空闲时才启动此任务"
- ✅ **只有在接通交流电源时才启动此任务** (笔记本电脑建议)

#### "设置"选项卡:
- ✅ **允许按需运行任务**
- ✅ **如果过了计划开始时间，立即启动任务**
- ❌ **如果任务运行时间超过以下时间，则停止任务**: 取消勾选
- ✅ **如果请求后任务还在运行，强行将其停止**

## 🔧 手动测试 | Manual Testing

### 测试步骤:
1. 右键点击创建的任务
2. 选择"运行"
3. 检查任务状态是否为"正在运行"然后变为"就绪"

### 验证结果:
1. 运行 `view_daily_logs.bat`
2. 查看最新日志确认任务执行成功
3. 检查 `logs` 文件夹中的日志文件

## 📊 日志文件格式 | Log File Format

```
========================================
Downloads Monitor Daily Task
Started: Wed 01/15/2025 02:00:15.23
========================================

Python 3.11.0
[INFO] No virtual environment found, using system Python

[TASK] Starting daily Downloads folder monitoring...
Command: python app.py --log-level INFO

Initializing Downloads folder monitor...

=== System Information ===
Platform: Windows
Machine: AMD64
Hostname: YourComputer
WSL2 detected: False
Extensions enabled: True

Monitoring path: C:\Users\Zen\Downloads

Loading existing data...
Existing records: 1250

Starting Downloads folder monitoring...

=== File Organization Phase ===
Found 15 files to organize
Moved 'document.pdf' to 'Documents/' folder
Moved 'installer.exe' to 'Programs/' folder
File organization completed. 12 files organized.

Scanning Downloads folder...
Files scanned: 1347

Updating data...
Updated records: 1347

Saving data to CSV...

Running extensions...

=== File Type Analysis ===
Total files: 1347
Unique extensions: 28

File type distribution:
  .pdf: 234 files (17.4%)
  .jpg: 189 files (14.0%)
  .mp4: 156 files (11.6%)
  .docx: 145 files (10.8%)

=== File Size Analysis ===
Total size: 15.2 GB
Total files: 1347

Size distribution:
  Small (1KB - 1MB): 892 files
  Medium (1MB - 100MB): 398 files
  Large (100MB - 1GB): 57 files

=== Change Detection ===
New files: 5
Modified files: 2
Deleted files: 0
Total changes: 7

=== Statistics ===
Downloads path: C:\Users\Zen\Downloads
Total files: 1347

By folder distribution:
  Documents: 425 files
  Programs: 234 files
  Music: 189 files
  Video: 156 files
  Compressed: 98 files
  Root Directory: 245 files

Monitoring completed!

[TASK] Monitoring completed with exit code: 0
[SUCCESS] Daily monitoring task completed successfully

========================================
Task finished: Wed 01/15/2025 02:05:42.18
========================================
```

## 🚨 故障排除 | Troubleshooting

### 问题: 任务未执行
**解决方案**:
1. 检查任务计划程序中的任务状态
2. 确保"使用最高权限运行"已勾选
3. 验证文件路径是否正确

### 问题: Python未找到
**解决方案**:
1. 确保Python已安装并添加到PATH
2. 在命令行运行 `python --version` 验证
3. 检查虚拟环境路径是否正确

### 问题: 权限不足
**解决方案**:
1. 确保任务以管理员权限运行
2. 检查文件夹访问权限
3. 尝试手动运行 `start_daily.bat` 测试

## 🔍 监控和维护 | Monitoring & Maintenance

### 定期检查:
- **每周**: 运行 `view_daily_logs.bat` 检查任务执行状态
- **每月**: 清理超过30天的旧日志文件
- **季度**: 验证任务配置是否需要更新

### 日志管理:
- 日志文件自动按日期命名
- 使用 `view_daily_logs.bat` 的选项4清理7天前的日志
- 大量日志可能占用磁盘空间，建议定期清理

## 📈 性能优化建议 | Performance Optimization

### 最佳实践:
1. **时间选择**: 选择系统负载较低的时间（如凌晨2-4点）
2. **频率设置**: 每日执行一次通常足够
3. **资源监控**: 定期检查任务执行时间，避免与其他任务冲突
4. **日志轮转**: 定期清理旧日志，保持系统性能

### 可选配置:
- 如果文件变化频繁，可考虑每12小时执行一次
- 对于大型文件夹，可能需要调整任务超时设置
- 可以创建多个任务监控不同文件夹

---

## 📞 技术支持 | Technical Support

如果遇到问题：
1. 查看最新的日志文件
2. 检查Windows事件查看器中的任务计划程序日志
3. 手动运行 `start_daily.bat` 进行调试
4. 确保所有依赖文件都在正确位置
