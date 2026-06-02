# Yfix Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [CLI Usage](#cli-usage)
4. [GUI Usage](#gui-usage)
5. [Feature Reference](#feature-reference)
6. [Admin Requirements](#admin-requirements)
7. [Building from Source](#building-from-source)
8. [Tips & Workflow](#tips--workflow)

---

## Overview

Yfix is a Windows PC diagnostic and repair tool written in Python. It provides 27 tools to diagnose slowdowns, clean junk, scan for malware, repair system files, manage restore points, and optimize performance.

Two interfaces are available:
- **CLI** (`yfix.py`) — interactive terminal menu, also supports `--quick` mode
- **GUI** (`yfix_gui.py`) — Tkinter graphical interface with buttons and progress bar

Both interfaces share the same backend logic in `yfix.py`.

---

## Installation

### Option 1: Pre-built EXE
- **GUI version**: `Yfix.exe` — double-click to launch, no console window
- **CLI version**: `Yfix-CLI.exe` — run from Command Prompt or PowerShell

Download from the [releases page](https://github.com/yohi441/yfix/releases).

### Option 2: From Source
```cmd
git clone https://github.com/yohi441/yfix.git
cd yfix
pip install psutil
```

Dependencies:
- `psutil` — system monitoring and process management
- `tkinter` — included with Python, no separate install needed

---

## CLI Usage

Run the interactive menu:
```cmd
python yfix.py
```

Quick diagnostic + cleanup (no menu):
```cmd
python yfix.py --quick
```

Show help:
```cmd
python yfix.py --help
```

### Menu Navigation
1. Select an option by number (1–28), then press Enter.
2. Enter "29", "q", "exit", or "quit" to exit.
3. Enter "help", "h", or "?" to view the help screen at any time.
4. Some options require text input (e.g., restore point descriptions).
5. Yes/No prompts accept "y" or "n".

Admin status is shown at the top of the menu. Most features require admin.

---

## GUI Usage

Launch the GUI:
```cmd
python yfix_gui.py
```

Or double-click `Yfix.exe`.

### Layout
- **Top bar**: tool name, admin status indicator (YES / NO limited), warning banner
- **Button grid**: 28 feature buttons arranged in 5 columns
- **Progress bar**: appears at the bottom while a task is running
- **Output panel**: dark-themed text area showing real-time command output
- **Bottom bar**: "Clear Output" and "Exit" buttons

### Behavior
- Click any button to run the corresponding tool.
- Buttons are disabled while a task is running.
- Long-running tasks (SFC, DISM, malware scan, Run ALL) run in a background thread with a progress bar.
- Short tasks run synchronously; results appear immediately in the output panel.
- Each task prints an `OK:` or `FAIL:` message in the output when done.

---

## Feature Reference

### 1. System Information
Displays: CPU (cores, threads), RAM (total, available, usage), GPU model(s), disk drives (model, type, size), OS version + build, uptime, running processes count, CPU temperature (if available). Read-only.

### 2. Why Is My PC Slow? (Diagnostic)
Scans 15+ factors: free disk space, memory pressure, CPU usage, startup program count, suspicious processes, old drivers, disk health, disk type (SSD vs HDD), visual effects setting, power plan, browser cache size, CPU temperature, Windows update recency, pagefile size. Assigns severity levels (CRITICAL → LOW). Best first step.

### 3. Create System Restore Point
Creates a restore point via `Checkpoint-Computer`. Prompts for a description. Run this before any fix or before servicing someone else's PC.

### 4. Malware & Virus Scan
Runs Windows Defender Quick Scan (`MpCmdRun.exe -Scan -ScanType 1`). Also checks running processes against a suspicious names list, inspects startup registry locations (`Run`, `RunOnce`, `Wow6432Node\Run`), and common autorun folders. No third-party AV required.

### 5. Clean Temporary Files
Deletes: `%TEMP%`, `%TMP%`, `C:\Windows\Temp`, `C:\Windows\Prefetch`, browser caches (Edge, Chrome, Firefox), `LocalAppData\Temp`. Runs `cleanmgr /sageset` for automated cleanup. Frees disk space and removes accumulated junk.

### 6. Storage Sense (Auto Cleanup)
Enables Windows Storage Sense via registry: auto-delete temp files and recycle bin contents monthly. Set-and-forget.

### 7. Startup Programs Manager
Lists all startup programs via `wmic startup`. Shows total count. Warnings if more than 5 startup items.

### 8. Background Apps Control
Lists Windows Store apps registered for background activity. Prompts to disable background access (frees RAM/CPU for games and demanding apps).

### 9. Unnecessary Apps & Bloatware
Scans for common pre-installed bloatware packages via `winget` and registry. Also lists large installed applications. Suggests removal candidates.

### 10. Driver Health Check
Checks driver dates via WMIC. Flags any driver older than 5 years with a note.

### 11. Disk Optimizer (Defrag / TRIM)
Analyzes each drive. SSD → runs TRIM. HDD → runs defrag analysis with optional defrag. Reports disk health status.

### 12. Windows Memory Diagnostic
Schedules `mdsched.exe` to run on next reboot. Advises the user to restart and let the test complete.

### 13. Battery Health Report
Generates an HTML battery report to `%TEMP%\battery-report.html` via `powercfg /batteryreport`. Shows design capacity, full charge capacity, wear level, cycle count. Laptops only.

### 14. Visual Effects Tuner
One-click toggle for "Adjust for best performance" (disables animations, transparency, shadows, taskbar animations). Best for low-RAM or older machines.

### 15. Windows Privacy Tweaks
Disables: telemetry, ads, suggestions, activity tracking, app diagnostics, browser data sharing, Windows tips, and inventory collector. All via registry. Safe and reversible.

### 16. Power Plan Optimizer
Shows current active power plan. Offers to switch to: High Performance, Balanced, or Power Saver. Laptops on Power Saver are often perceived as slow.

### 17. Network Diagnostics
Shows: IP configuration (IPv4, gateway, DNS), gateway ping, external ping (8.8.8.8), DNS resolution test (google.com). Quick connectivity check.

### 18. System File Checker (SFC)
Runs `sfc /scannow` to scan and repair protected system files. Takes 5–15 minutes. Run DISM first for best results.

### 19. DISM Health Restore
Runs `DISM /Online /Cleanup-Image /RestoreHealth` to repair Windows component store corruption. Takes 10–20 minutes. Should be run before SFC.

### 20. Windows Update Status
Shows last update date. Missing updates = higher security risk and potential performance degradation.

### 21. Browser Cleanup
Clears cache, history, and cookies for Microsoft Edge, Google Chrome, and Mozilla Firefox. Large browser caches slow down both browsing and the PC.

### 22. Flush DNS & Reset Network Stack
Runs: `ipconfig /flushdns`, `ipconfig /release`, `ipconfig /renew`, `netsh int ip reset`, `netsh winsock reset`. Fixes many network issues.

### 23. Repair Install (In-place Upgrade)
Opens the official Microsoft Media Creation Tool download page. This is the last resort — reinstalls Windows while keeping files and apps. Fixes deep corruption, registry issues, and stubborn slowness.

### 24. Run ALL Automated Fixes
Sequential automated run: restore point → clean temp → Storage Sense → malware scan → browser cleanup → background apps → SFC → DISM → flush DNS → disk optimizer → visual effects → privacy tweaks → power plan (high perf). Estimated time: 30 minutes.

### 25. Help & Manual
Displays the built-in help text with option summaries and tips.

### 26. View Restore Points
Lists all saved restore points via `Get-ComputerRestorePoint`. Shows description and creation date.

### 27. Restore from Point
Prompts for a SequenceNumber (from list), then runs `Restore-Computer` to roll back. The PC will restart.

### 28. About
Shows version, author, tool description, and GitHub repository URL.

---

## Admin Requirements

| Feature | Requires Admin |
|---------|:--------------:|
| System Information | No |
| Why Is My PC Slow? | No |
| Create Restore Point | Yes |
| Malware Scan | Yes |
| Clean Temp Files | Yes |
| Storage Sense | Yes |
| Startup Manager | No |
| Background Apps | Yes |
| Bloatware Remover | Yes |
| Driver Check | No |
| Disk Optimizer | Yes |
| Memory Diagnostic | Yes |
| Battery Report | No |
| Visual Effects | Yes |
| Privacy Tweaks | Yes |
| Power Plan | Yes |
| Network Diagnostics | No |
| SFC | Yes |
| DISM | Yes |
| Windows Update | No |
| Browser Cleanup | No |
| Flush DNS | Yes |
| Repair Install | No (opens link) |
| Run ALL | Yes (most steps) |
| Help | No |
| View Restore Points | Yes |
| Restore from Point | Yes |
| About | No |

---

## Building from Source

```cmd
pip install pyinstaller psutil
build_exe.bat
```

The batch file runs:
```cmd
pyinstaller --onefile --windowed --name="Yfix" --hidden-import=psutil yfix_gui.py
```

**Output:**
- `dist\Yfix.exe` — GUI version (windowed, no console)
- `dist\Yfix-CLI.exe` — CLI version (console) — built separately via:
```cmd
pyinstaller --onefile --name="Yfix-CLI" --hidden-import=psutil yfix.py
```

---

## Tips & Workflow

1. **Start with option 2** (diagnostic) to identify the root cause.
2. **Always create a restore point** (option 3) before making changes.
3. **Run option 24** (all fixes) if you're short on time — it handles the most common issues automatically.
4. **Remove bloatware** (option 9) — many OEM PCs ship with useless programs that eat RAM and CPU.
5. **Check startup programs** (option 7) — disable anything you don't need at boot (Spotify, Steam, Adobe updaters...).
6. **Run Windows Update** (option 20) — old builds can be slow.
7. **Check memory health** (option 12) if you get random crashes or blue screens.
8. **SSD upgrade check** — option 11 reports if you're on an HDD. Upgrading to an SSD is the single biggest speed improvement for most older PCs.
9. **Run DISM before SFC** — option 19 then option 18 for best system file repair results.
10. **Last resort**: repair install (option 23) reinstalls Windows while keeping your files.

---

## Repository

[https://github.com/yohi441/yfix.git](https://github.com/yohi441/yfix.git)

Built with Python, psutil, Tkinter, and PyInstaller.
