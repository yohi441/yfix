# Yfix — Windows PC Fix & Speedup Tool

An all-in-one diagnostic and repair tool for Windows PCs. 27 tools covering system info, malware scan, disk cleanup, driver checks, network diagnostics, SFC/DISM, restore points, privacy tweaks, and more.

## Features

| #   | Tool                      | What it does                                           |
| --- | ------------------------- | ------------------------------------------------------ |
| 1   | System Information        | Hardware specs, OS version, uptime                     |
| 2   | Why Is My PC Slow?        | 15+ cause diagnostic in one shot                       |
| 3   | Create Restore Point      | Backup before making changes                           |
| 4   | Malware & Virus Scan      | Windows Defender Quick Scan + process check            |
| 5   | Clean Temporary Files     | Empties TEMP, Prefetch, browser caches, runs cleanmgr  |
| 6   | Storage Sense             | Enables auto-cleanup of temp files                     |
| 7   | Startup Programs Manager  | Lists & warns about startup bloat                      |
| 8   | Background Apps Control   | Manage Windows Store background apps                   |
| 9   | Bloatware Remover         | Finds & suggests removal of pre-installed junk         |
| 10  | Driver Health Check       | Flags drivers older than 5 years                       |
| 11  | Disk Optimizer            | TRIM for SSDs, defrag for HDDs                         |
| 12  | Memory Diagnostic         | Schedules RAM test on next reboot                      |
| 13  | Battery Report            | HTML battery health report (laptops)                   |
| 14  | Visual Effects Tuner      | One-click performance mode                             |
| 15  | Privacy Tweaks            | Disables telemetry, ads, tracking                      |
| 16  | Power Plan Optimizer      | Switch between High Perf / Balanced / Saver            |
| 17  | Network Diagnostics       | Ping, DNS, IP config tests                             |
| 18  | System File Checker       | `sfc /scannow` to repair system files                  |
| 19  | DISM Health Restore       | Fixes component store corruption                       |
| 20  | Windows Update Status     | Check pending updates                                  |
| 21  | Browser Cleanup           | Clear cache/history for Edge, Chrome, Firefox          |
| 22  | Flush DNS & Reset Network | Reset TCP/IP, DNS cache, renew IP                      |
| 23  | Repair Install            | Opens Media Creation Tool for in-place upgrade         |
| 24  | Run ALL Fixes             | Automated: restore point → cleanup → SFC → DISM → more |
| 25  | Help & Manual             | Full documentation                                     |
| 26  | View Restore Points       | List all saved restore points                          |
| 27  | Restore from Point        | Roll back to a selected restore point                  |
| 28  | About                     | Version info & credits                                 |

## Quick Start

### Pre-built EXE (no Python needed)

Download `Yfix.exe` (GUI) or `Yfix-CLI.exe` (terminal) from the [releases](https://github.com/yohi441/yfix/releases) tab, then run it.

### From Source

```cmd
git clone https://github.com/yohi441/yfix.git
cd yfix
pip install psutil
python yfix.py              # CLI interactive menu
python yfix.py --quick      # Quick diagnostic + cleanup
python yfix_gui.py           # GUI version
```

### Build EXE

```cmd
build_exe.bat
```

Requires Python and PyInstaller:

```cmd
pip install pyinstaller
```

## Requirements

- Windows 10/11
- Python 3.8+ (if running from source)
- Administrator privileges for most features

## License

MIT
