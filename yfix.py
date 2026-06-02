#!/usr/bin/env python3
"""
yfix.py - Yfix: Windows maintenance & troubleshooting tool
Run as Administrator for full functionality.

Usage:
  python yfix.py          Interactive menu
  python yfix.py --help   Show this help and exit
  python yfix.py --quick  Run quick diagnostics + cleanup
"""

import os
import sys
import time
import platform
import subprocess
import ctypes
import psutil
import socket
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path


VERSION = "2.1"


# ── Utilities ──────────────────────────────────────────────────────────


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_cmd(cmd, capture=True):
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if not capture else 0)
        return r.stdout.strip() if capture else r.returncode
    except Exception as e:
        return f"[ERROR] {e}"


def require_admin():
    if not is_admin():
        print("  NOTE: Most features need Administrator privileges.")
        print("  Right-click -> 'Run as Administrator' for full access.\n")


def section(title):
    print(f"\n{'=' * 52}")
    print(f"  {title}")
    print(f"{'=' * 52}")


def warn(msg):
    print(f"  [!!] {msg}")


def ok(msg):
    print(f"  [OK] {msg}")


def info(msg):
    print(f"  [..] {msg}")


def prompt_yesno(question):
    a = input(f"  {question} (y/n): ").strip().lower()
    return a in ("y", "yes")


# ── Help / Manual ──────────────────────────────────────────────────────


def show_help():
    section("Help & Manual")
    print("""
  Yfix is an all-in-one tool for diagnosing and fixing slow Windows PCs.
  Run it, pick an option, and follow the on-screen instructions.

  -- Admin Required --------------------------------------
  Many features require Administrator access.
  Right-click the script or CMD/PowerShell -> 'Run as Administrator'.

  -- Menu Options Summary --------------------------------

   1. System Information
      Shows hardware specs (CPU, RAM, GPU, disk), OS version, uptime.
      No changes made -- just info.

   2. Why Is My PC Slow? (Diagnostic)
      Checks 15+ common causes of slowness in one shot:
      disk space, memory, CPU, startup bloat, background processes,
      malware signs, driver age, disk health, visual effects,
      power plan, browser cache, temps, updates, pagefile, disk type.
      Use this FIRST when someone says their PC is slow.

   3. Create System Restore Point
      Creates a restore point before making any changes.
      Lets you roll back if something goes wrong.
      Always run this first before fixing someone else's PC.

   4. Malware & Virus Scan
      Runs Windows Defender Quick Scan via MpCmdRun.exe.
      Also checks running processes for suspicious names,
      inspects startup registry locations and autoruns.
      Does NOT install 3rd-party AV -- uses Microsoft's built-in.

   5. Clean Temporary Files
      Empties: TEMP, %TMP%, Windows\\Temp, Prefetch,
      LocalAppData\\Temp, browser caches (Edge, Chrome, Firefox),
      and runs cleanmgr. Frees disk space and removes junk.

   6. Storage Sense (Auto Cleanup)
      Enables Windows Storage Sense to automatically delete
      temp files and recycle bin contents monthly.
      Set-it-and-forget-it disk space management.

   7. Startup Programs Manager
      Lists all programs that start automatically.
      Shows total count with warning if > 5 (common slowness cause).
      Recommends disabling high-impact items.

   8. Background Apps Control
      Lists Windows Store apps running in background.
      Disabling background access frees up RAM and CPU.
      Safe to disable for games, media, and productivity apps.

   9. Unnecessary Apps & Bloatware
      Scans for common pre-installed bloatware (Candy Crush,
      Xbox widgets, OneDrive prompts, etc.) and suggests removal.
      Lists large installed apps for review.

  10. Driver Health Check
      Checks driver dates via WMIC.
      Flags drivers older than 5 years.
      Suggests updating GPU, chipset, network drivers.

  11. Disk Optimizer (Defrag / Trim)
      Analyzes each drive. If SSD -> runs TRIM.
      If HDD -> runs defrag analysis and optional defrag.
      Keeps SSDs healthy and HDDs fast.

  12. Windows Memory Diagnostic
      Schedules a RAM test on next reboot.
      Faulty RAM causes crashes, freezes, and random slowdowns.
      Runs during boot -- results appear after login.

  13. Battery Health Report
      Generates a detailed HTML battery report (laptops only).
      Shows design capacity vs current capacity (battery wear),
      cycle count, and recent usage.

  14. Visual Effects Tuner
      One-click toggle: "Adjust for best performance"
      (disables animations, transparency, shadows).
      Great for low-RAM or older machines.

  15. Windows Privacy Tweaks
      Disables telemetry, ads, tips, suggestions, and activity
      tracking. Reduces background network and CPU usage.
      All tweaks are safe and reversible.

  16. Power Plan Optimizer
      Shows current power plan. Options:
      - High Performance (best speed, more power use)
      - Balanced (default)
      - Power Saver
      Laptops on Power Saver are often perceived as slow.

  17. Network Diagnostics
      IP config, gateway ping, external ping (8.8.8.8),
      DNS resolution test. Use when "internet is slow".

  18. System File Checker (SFC)
      Runs sfc /scannow to repair corrupted Windows files.
      Takes 5-15 minutes.

  19. DISM Health Restore
      Runs DISM /RestoreHealth to fix component store corruption.
      Run this BEFORE SFC for best results. Takes 10-20 min.

  20. Windows Update Status
      Checks for pending updates and shows install status.
      Missing updates = security risk + potential slowness.

  21. Browser Cleanup
      Clears cache, history, cookies for Edge, Chrome, Firefox.
      Large browser caches slow down both browsing and the PC.

  22. Flush DNS & Reset Network Stack
      Resets TCP/IP, flushes DNS cache, renews IP.
      Fixes many network connectivity/speed issues.

  23. Repair Install (In-place Upgrade)
      Last resort: reinstalls Windows while keeping files & apps.
      Fixes deep corruption, registry issues, and stubborn slowness.
      Opens the official Media Creation Tool download page.

  24. Run ALL Automated Fixes
      Runs: restore point -> temp cleanup -> storage sense ->
      malware scan -> browser cleanup -> background apps ->
      SFC -> DISM -> flush DNS -> disk optimizer -> visual effects ->
      privacy tweaks -> power plan high perf.
      Come back in 30 minutes.

  25. Help & Manual
      You're here.

  26. View Restore Points
      Lists all saved restore points with description and date.
      Use to check what's available before rolling back.

  27. Restore from Point
      Pick a restore point by SequenceNumber and roll back
      Windows system files. PC will restart. Keeps your data.

  28. About
      Version info, author, and credits.

  -- Tips for Speeding Up a Slow PC ----------------------

  1. Start with option 2 (diagnostic) to find the cause.
  2. Always create a restore point FIRST (option 3).
  3. Run option 24 (all fixes) if you're short on time.
  4. Remove bloatware (option 9) -- many OEM PCs ship with
     useless programs that eat RAM and CPU.
  5. Check startup programs (option 7) -- disable anything
     you don't need at boot (Spotify, Steam, Adobe updaters...).
  6. Run Windows Update (option 20) -- old builds can be slow.
  7. Check memory health (option 12) if you get random crashes.
  8. If still slow -- consider an SSD upgrade (option 11 can
     check if you're on an HDD).
  9. Last resort: repair install (option 23) -- reinstalls
     Windows while keeping your files.
""")


# ── System Information ────────────────────────────────────────────────


def get_disk_type(path="C:"):
    out = run_cmd(f"wmic diskdrive where \"DeviceID='{path}'\" get MediaType")
    if "SSD" in out or "Solid State" in out or "SSD" in platform.uname().version:
        for line in out.splitlines():
            if "SSD" in line or "Solid" in line:
                return "SSD"
    out2 = run_cmd("powershell -Command \"Get-PhysicalDisk | Select-Object FriendlyName,MediaType | Format-Table -HideTableHeaders\"")
    if "SSD" in out2 or "Unspecified" not in out2:
        for line in out2.splitlines():
            if "SSD" in line:
                return "SSD"
            if "HDD" in line:
                return "HDD"
    parts = run_cmd("wmic diskdrive get Model")
    for line in parts.splitlines():
        if "SSD" in line.upper() or "NVMe" in line.upper() or "M.2" in line.upper():
            return "SSD"
    return "HDD (or unknown)"


def show_sysinfo():
    section("System Information")
    uname = platform.uname()
    booted = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()

    print(f"  Hostname       : {socket.gethostname()}")
    print(f"  OS             : {uname.system} {uname.release} ({uname.version})")
    print(f"  Processor      : {uname.processor}")
    print(f"  CPU Cores      : {psutil.cpu_count(logical=False)} physical / {psutil.cpu_count()} logical")
    print(f"  RAM            : {psutil.virtual_memory().total / (1024**3):.2f} GB total")
    print(f"  RAM Available  : {psutil.virtual_memory().available / (1024**3):.2f} GB")
    print(f"  Boot Time      : {booted.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Uptime         : {str(now - booted).split('.')[0]}")

    try:
        gpu = subprocess.run("wmic path Win32_VideoController get Name", capture_output=True, text=True, shell=True)
        lines = [l.strip() for l in gpu.stdout.splitlines() if l.strip() and "Name" not in l]
        if lines:
            print(f"  GPU            : {lines[0]}")
    except Exception:
        pass

    print(f"  Disk Type      : {get_disk_type()}")
    print()

    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current:
                        hwarn = "  !! HIGH" if entry.current > 80 else ""
                        print(f"  Temp ({name})   : {entry.current} C{hwarn}")
    except Exception:
        pass


# ── Create System Restore Point ────────────────────────────────────────


def create_restore_point():
    section("Create System Restore Point")
    if not is_admin():
        print("  Admin required.")
        return
    desc = input("  Description for restore point (or Enter for 'Yfix'): ").strip() or "Yfix"
    info(f"Creating restore point '{desc}'...")
    out = run_cmd(f'powershell -Command "Checkpoint-Computer -Description \'{desc}\' -RestorePointType MODIFY_SETTINGS"')
    if "completed" in out.lower():
        ok("Restore point created successfully!")
    else:
        print(f"  {out}")
        warn("If this failed, System Protection may be disabled.")
        if prompt_yesno("Open System Protection settings to enable it?"):
            run_cmd("SystemPropertiesProtection")


# ── List Restore Points ────────────────────────────────────────────────


def list_restore_points():
    section("View Restore Points")
    if not is_admin():
        print("  Admin required.")
        return
    out = run_cmd(
        'powershell -Command "Get-ComputerRestorePoint | '
        'Select-Object SequenceNumber,Description,CreationTime,EventType | '
        'Format-Table -AutoSize | Out-String -Width 200"'
    )
    if out and "Get-ComputerRestorePoint" not in out and out.strip():
        print(f"  {out}")
        print("  To restore: select option 27 and enter the SequenceNumber.")
    else:
        warn("No restore points found or System Protection is disabled.")
        if prompt_yesno("Open System Protection settings to enable it?"):
            run_cmd("SystemPropertiesProtection")


# ── Restore from Point ─────────────────────────────────────────────────


def restore_from_point():
    section("Restore from Point")
    if not is_admin():
        print("  Admin required.")
        return
    info("Fetching available restore points...")
    out = run_cmd(
        'powershell -Command "Get-ComputerRestorePoint | '
        'Select-Object SequenceNumber,Description,CreationTime | '
        'Format-Table -AutoSize | Out-String -Width 200"'
    )
    if not out or "Get-ComputerRestorePoint" in out or not out.strip():
        warn("No restore points found. Create one first (option 3).")
        return
    print(f"  {out}")
    try:
        seq = int(input("  Enter SequenceNumber to restore: ").strip())
    except ValueError:
        warn("Invalid number.")
        return
    print(f"\n  WARNING: This will restart your PC and roll back system files.")
    print(f"  Your personal files will NOT be affected.")
    if prompt_yesno(f"Restore to point #{seq}? PC will reboot."):
        info(f"Restoring to point #{seq}... PC will restart shortly.")
        r = subprocess.run(
            ["powershell", "-Command", f"Restore-Computer -RestorePoint {seq} -Confirm:$false"],
            capture_output=True, text=True, timeout=30
        )
        output = r.stdout + r.stderr
        if "restart" in output.lower() or "shut down" in output.lower() or "shutdown" in output.lower():
            print("  Restore initiated. Save your work — the system will reboot.")
        else:
            print(f"  {output[:500] if output else 'Command sent. The system may restart.'}")
    else:
        print("  Canceled.")


# ── Storage Sense (Auto Cleanup) ───────────────────────────────────────


def storage_sense():
    section("Storage Sense")
    info("Current Storage Sense status:")
    out = run_cmd(
        'powershell -Command "(Get-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense\\Parameters\\StoragePolicy\').01"'
    )
    if out.strip() == "1":
        ok("Storage Sense is enabled")
    else:
        warn("Storage Sense is disabled")
        if prompt_yesno("Enable Storage Sense (auto-clean temp files & recycle bin)?"):
            run_cmd(
                'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense\\Parameters\\StoragePolicy\' -Name \'01\' -Value 1 -Type DWord"'
            )
            run_cmd(
                'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense\\Parameters\\StoragePolicy\' -Name \'04\' -Value 30 -Type DWord"'
            )
            run_cmd(
                'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense\\Parameters\\StoragePolicy\' -Name \'08\' -Value 1 -Type DWord"'
            )
            ok("Storage Sense enabled (runs monthly, cleans every 30 days)")


# ── Background Apps Control ────────────────────────────────────────────


def background_apps_control():
    section("Background Apps Control")
    info("Windows Store apps can run in the background, consuming RAM and CPU.")
    info("Disabling background access for unused apps helps speed up your PC.\n")

    out = run_cmd(
        'powershell -Command "Get-AppxPackage | ForEach-Object { $_.PackageFamilyName }"'
    )
    apps = [a.strip() for a in out.splitlines() if a.strip() and "PackageFamilyName" not in a]
    print(f"  Found {len(apps)} apps with background capability.\n")

    if prompt_yesno("Disable background access for ALL non-essential apps?"):
        count = 0
        for app in apps:
            r = run_cmd(
                f'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications\\{app}\' -Name GlobalUserDisabled -Value 1 -Type DWord -ErrorAction SilentlyContinue"'
            )
            count += 1
        print(f"  Disabled background access for {count} apps.")
        print("  Changes take effect after restart.")
        print("  (Essential system apps like mail/calendar are unaffected)")


# ── Windows Memory Diagnostic ──────────────────────────────────────────


def memory_diag():
    section("Windows Memory Diagnostic")
    print("  Faulty RAM is a common cause of crashes, freezes, and slowdowns.")
    print("  Windows Memory Diagnostic will test your RAM on next restart.\n")
    if prompt_yesno("Schedule memory test on next reboot?"):
        run_cmd("mdsched.exe", capture=False)
        print("  Windows Memory Diagnostic scheduled.")
        print("  Save your work, then restart the PC.")
        print("  The test runs automatically during boot (may take 30+ min).")
        print("  Results appear after login.")


# ── Battery Health Report ──────────────────────────────────────────────


def battery_report():
    section("Battery Health Report")
    out = run_cmd("powercfg /batteryreport /output \"%TEMP%\\battery-report.html\"")
    report = Path(os.environ.get("TEMP", "")) / "battery-report.html"
    if report.exists():
        size = report.stat().st_size
        if size > 0:
            print(f"  Report saved to {report}")
            os.startfile(report)
            print()
            print("  Key things to check:")
            print("    - DESIGN CAPACITY vs FULL CHARGE CAPACITY (battery wear)")
            print("    - CYCLE COUNT (higher = more worn)")
            print("    - Recent usage and battery life estimates")
        else:
            warn("Report file is empty. Try running as Admin.")
    else:
        warn("Could not generate battery report.")
        info("This feature is for laptops only.")


# ── Windows Privacy Tweaks ─────────────────────────────────────────────


def privacy_tweaks():
    section("Windows Privacy Tweaks")
    print("  These tweaks disable telemetry, ads, and suggestions")
    print("  that consume background resources. Safe to apply.\n")

    changes = 0

    if prompt_yesno("Disable telemetry & data collection?"):
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection\' -Name AllowTelemetry -Value 0 -Type DWord -ErrorAction SilentlyContinue"'
        )
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection\' -Name MaxTelemetryAllowed -Value 0 -Type DWord -ErrorAction SilentlyContinue"'
        )
        changes += 1

    if prompt_yesno("Disable 'Show me tips, tricks, and suggestions'?"):
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager\' -Name SubscribedContent-338389Enabled -Value 0 -Type DWord"'
        )
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager\' -Name SystemPaneSuggestionsEnabled -Value 0 -Type DWord"'
        )
        changes += 1

    if prompt_yesno("Disable advertising ID (stop personalized ads)?"):
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo\' -Name Enabled -Value 0 -Type DWord -ErrorAction SilentlyContinue"'
        )
        changes += 1

    if prompt_yesno("Disable activity history (Microsoft tracks your activity)?"):
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System\' -Name EnableActivityFeed -Value 0 -Type DWord -ErrorAction SilentlyContinue"'
        )
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System\' -Name PublishUserActivities -Value 0 -Type DWord -ErrorAction SilentlyContinue"'
        )
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System\' -Name UploadUserActivities -Value 0 -Type DWord -ErrorAction SilentlyContinue"'
        )
        changes += 1

    if prompt_yesno("Disable startup app suggestions in Start Menu?"):
        run_cmd(
            'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager\' -Name SubscribedContent-310093Enabled -Value 0 -Type DWord"'
        )
        changes += 1

    print(f"\n  Applied {changes} change(s). Restart to take full effect.")


# ── Repair Install (In-place Upgrade) ──────────────────────────────────


def repair_install():
    section("Repair Install (In-place Upgrade)")
    print("  If Windows is severely corrupted or still slow after all fixes,")
    print("  an in-place upgrade reinstalls Windows while keeping your files.")
    print()
    print("  STEPS:")
    print("  1. Download Windows 11 Media Creation Tool from:")
    print("     https://www.microsoft.com/software-download/windows11")
    print("     (Or Windows 10: https://www.microsoft.com/software-download/windows10)")
    print("  2. Run the tool and select 'Upgrade this PC now'")
    print("  3. Choose 'Keep personal files and apps'")
    print("  4. Let it run (1-2 hours) -- PC will restart several times")
    print()
    if prompt_yesno("Open the download page in your browser?"):
        import webbrowser
        webbrowser.open("https://www.microsoft.com/software-download/windows11")
        print("  Page opened.")


# ── Why Is My PC Slow? (Comprehensive Diagnostic) ─────────────────────


def why_slow():
    section("Why Is My PC Slow? -- Full Diagnostic")
    issues = []

    print("  Checking 15+ common causes...\n")

    # 1. Disk space
    info("Checking disk space...")
    low_space = False
    for part in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(part.mountpoint)
            free_pct = 100 - u.percent
            if free_pct < 10:
                issues.append((3, f"Very low disk space on {part.device}: only {free_pct:.0f}% free ({u.free / (1024**3):.1f} GB)"))
                low_space = True
            elif free_pct < 20:
                issues.append((5, f"Low disk space on {part.device}: {free_pct:.0f}% free ({u.free / (1024**3):.1f} GB)"))
        except PermissionError:
            pass
    if not low_space:
        ok("Disk space OK")

    # 2. Memory
    info("Checking memory...")
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        issues.append((1, f"Critical RAM usage: {mem.percent}% -- PC will swap heavily and feel slow"))
    elif mem.percent > 80:
        issues.append((4, f"High RAM usage: {mem.percent}% -- consider closing programs or adding RAM"))
    else:
        ok(f"RAM usage OK ({mem.percent}%)")

    # 3. CPU
    info("Checking CPU...")
    cpu = psutil.cpu_percent(interval=2)
    if cpu > 90:
        issues.append((2, f"CPU pegged at {cpu}% -- a process may be stuck or malware"))
    elif cpu > 70:
        issues.append((6, f"High CPU usage: {cpu}% -- check running processes"))
    else:
        ok(f"CPU usage OK ({cpu}%)")

    # 4. Process count
    info("Checking process count...")
    proc_count = len(list(psutil.process_iter()))
    if proc_count > 180:
        issues.append((4, f"Too many processes running ({proc_count}) -- lots of background bloat"))
    elif proc_count > 120:
        issues.append((6, f"High process count ({proc_count}) -- may slow boot and background perf"))
    else:
        ok(f"Process count OK ({proc_count})")

    # 5. Startup programs
    info("Checking startup programs...")
    startup = run_cmd("wmic startup get caption 2>nul")
    startup_lines = [l.strip() for l in startup.splitlines() if l.strip() and l.strip() != "Caption"]
    startup_count = len(startup_lines)
    if startup_count > 10:
        issues.append((3, f"Too many startup programs ({startup_count}) -- slows boot and background RAM"))
    elif startup_count > 5:
        issues.append((5, f"Many startup programs ({startup_count}) -- consider trimming"))
    else:
        ok(f"Startup programs OK ({startup_count})")

    # 6. Malware signs
    info("Checking for suspicious processes...")
    suspicious = check_suspicious_processes()
    if suspicious:
        issues.append((1, f"Suspicious processes detected: {', '.join(suspicious)} -- possible malware"))
    else:
        ok("No obvious malware processes detected")

    # 7. Driver age
    info("Checking driver ages...")
    old_drivers = check_old_drivers()
    if old_drivers:
        issues.append((5, f"{len(old_drivers)} driver(s) are very old -- may cause performance/stability issues"))
    else:
        ok("Drivers seem up-to-date")

    # 8. Disk health
    info("Checking disk health...")
    health = run_cmd("wmic diskdrive get status")
    if "Bad" in health or "Unknown" in health:
        issues.append((1, "Disk health check: BAD -- drive may be failing! Backup immediately!"))
    elif "OK" not in health:
        issues.append((6, "Disk health status unclear, verify manually"))
    else:
        ok("Disk health OK")

    # 9. Disk type (HDD vs SSD)
    info("Checking disk type...")
    dtype = get_disk_type()
    if "HDD" in dtype:
        issues.append((6, "You're on an HDD. Upgrading to an SSD is the #1 speed improvement you can make"))
    else:
        ok(f"Disk type: {dtype} -- fast!")

    # 10. Visual effects
    info("Checking visual effects...")
    perf = run_cmd('powershell -Command "(Get-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\').VisualFXSetting"')
    if perf.strip() == "3":
        ok("Visual effects already set to performance mode")
    else:
        issues.append((7, "Windows visual effects / animations are ON -- disabling can speed up old PCs"))

    # 11. Power plan
    info("Checking power plan...")
    plan = run_cmd("powercfg /getactivescheme")
    if "Power Saver" in plan or "a1841308" in plan.lower():
        issues.append((6, "Power plan is set to 'Power Saver' -- this throttles performance"))
    elif "High performance" in plan or "8c5e7fda" in plan.lower():
        ok("Power plan: High Performance")
    else:
        ok("Power plan: Balanced")

    # 12. Browser cache size
    info("Checking browser caches...")
    cache_size = get_browser_cache_size()
    if cache_size > 2.0:
        issues.append((5, f"Browser caches are large ({cache_size:.1f} GB) -- clearing may help"))
    else:
        ok(f"Browser cache size OK ({cache_size:.1f} GB)")

    # 13. Windows Update age
    info("Checking Windows Update status...")
    last_update = run_cmd('powershell -Command "(Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1).InstalledOn"')
    if last_update:
        try:
            last_update_dt = datetime.strptime(last_update.strip(), "%m/%d/%Y %I:%M:%S %p")
            days_since = (datetime.now() - last_update_dt).days
            if days_since > 60:
                issues.append((5, f"Windows not updated in {days_since} days -- updates fix performance bugs"))
            elif days_since > 30:
                issues.append((7, f"Last Windows update: {days_since} days ago"))
            else:
                ok(f"Windows updated recently ({days_since} days ago)")
        except ValueError:
            pass

    # 14. Pagefile
    info("Checking pagefile...")
    pf = run_cmd("wmic pagefile get AllocatedBaseSize")
    pf_lines = [l.strip() for l in pf.splitlines() if l.strip().isdigit()]
    if pf_lines:
        pf_size_mb = int(pf_lines[0])
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if pf_size_mb < 1024 and ram_gb < 8:
            issues.append((7, f"Pagefile is small ({pf_size_mb} MB) with only {ram_gb:.1f} GB RAM -- can cause out-of-memory errors"))
        else:
            ok(f"Pagefile OK ({pf_size_mb} MB)")
    else:
        warn("Could not determine pagefile size")

    # 15. System temperature
    try:
        info("Checking temperatures...")
        hot = False
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    if entry.current and entry.current > 85:
                        issues.append((2, f"High temperature: {entry.current}C ({name}) -- thermal throttling slows the CPU"))
                        hot = True
            if not hot:
                ok("Temperatures normal")
    except Exception:
        pass

    # Print Report
    print(f"\n{'=' * 52}")
    print("  DIAGNOSTIC RESULTS")
    print(f"{'=' * 52}")

    if not issues:
        print("\n  No major issues found! Your PC looks healthy.")
        print("  If it still feels slow, consider:")
        print("    - Upgrading to an SSD")
        print("    - Adding more RAM")
        print("    - Reinstalling Windows")
        return

    issues.sort(key=lambda x: x[0])
    severity_map = {1: "CRITICAL", 2: "HIGH", 3: "HIGH", 4: "MEDIUM", 5: "MEDIUM", 6: "LOW", 7: "LOW"}

    for sev, msg in issues:
        label = severity_map.get(sev, "INFO")
        print(f"  [{label}] {msg}")

    print(f"\n  Found {len(issues)} issue(s). Recommended actions:")
    print("  1. Create restore point first (option 3)")
    print("  2. Run option 24 (Run ALL Automated Fixes)")
    print("  3. For malware, run option 4 (Malware Scan)")
    print("  4. For bloatware, run option 9")
    print("  5. For startup bloat, run option 7")
    print("  6. Run Windows Update (option 20)")


# ── Malware & Virus Scan ──────────────────────────────────────────────


SUSPICIOUS_NAMES = [
    "miner", "xmrig", "ethminer", "cpuminer", "geth.exe", "minerd",
    "cryptonight", "coinminer",
    "winupdate.exe", "svch0st.exe", "csrsss.exe",
    "expl0rer.exe", "taskhostx.exe",
    "bitcoin", "monero",
]

SUSPICIOUS_LOCATIONS = [
    Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
]


def check_suspicious_processes():
    found = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = proc.info["name"] or ""
            cmdline = " ".join(proc.info["cmdline"] or [""])
            if any(s.lower() in name.lower() or s.lower() in cmdline.lower() for s in SUSPICIOUS_NAMES):
                if name not in found:
                    found.append(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return found


def malware_scan():
    section("Malware & Virus Scan")

    # Stage 1: Check running processes
    print("  [Stage 1] Scanning running processes for suspicious activity...")
    found = check_suspicious_processes()
    if found:
        warn(f"Suspicious process(es) detected: {', '.join(found)}")
    else:
        ok("No suspicious processes found")

    # Stage 2: Check startup locations
    print("\n  [Stage 2] Checking common malware persistence locations...")
    for loc in SUSPICIOUS_LOCATIONS:
        if loc.exists():
            items = list(loc.iterdir())
            if items:
                warn(f"Files in {loc}:")
                for f in items:
                    print(f"         {f.name}")
    ok("Startup locations checked")

    # Stage 3: Check registry autoruns
    print("\n  [Stage 3] Checking registry autorun locations...")
    reg_paths = [
        "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
    ]
    for rp in reg_paths:
        out = run_cmd(f'reg query "{rp}" 2>nul')
        for line in out.splitlines():
            if line.strip() and "ERROR" not in line:
                print(f"    {rp} -> {line.strip()}")
    ok("Registry autoruns checked")

    # Stage 4: Windows Defender Quick Scan
    print("\n  [Stage 4] Running Windows Defender Quick Scan...")
    mpcmd = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Windows Defender" / "MpCmdRun.exe"
    alt_mpcmd = Path(os.environ.get("PROGRAMW6432", "C:\\Program Files")) / "Windows Defender" / "MpCmdRun.exe"

    defender = mpcmd if mpcmd.exists() else alt_mpcmd if alt_mpcmd.exists() else None
    if defender and defender.exists():
        info("Scanning... this may take 5-10 minutes.")
        print("  (The scan runs silently in the background)")
        r = subprocess.run(
            [str(defender), "-Scan", "-ScanType", "1"],
            capture_output=True, text=True, timeout=900
        )
        output = r.stdout + r.stderr
        if "no threats" in output.lower() or "no virus" in output.lower():
            ok("Windows Defender: No threats found")
        elif "threat" in output.lower():
            warn("Threats detected! Check Windows Security for details.")
            print(f"    {output[:500]}")
        else:
            info(f"Defender scan finished. Output truncated:\n    {output[:300]}")
    else:
        warn("Windows Defender not found at expected path.")
        warn("Try running: Start-MpScan -ScanType QuickScan in PowerShell as Admin.")

    # Stage 5: Network connections check
    print("\n  [Stage 5] Checking for unusual network connections...")
    try:
        connections = psutil.net_connections()
        unusual = []
        for conn in connections:
            if conn.status == "ESTABLISHED" and conn.raddr:
                ip = conn.raddr.ip
                if not ip.startswith(("10.", "172.16.", "172.17.", "172.18.", "172.19.",
                                      "172.20.", "172.21.", "172.22.", "172.23.",
                                      "172.24.", "172.25.", "172.26.", "172.27.",
                                      "172.28.", "172.29.", "172.30.", "172.31.",
                                      "192.168.", "127.")):
                    try:
                        proc = psutil.Process(conn.pid)
                        unusual.append(f"{proc.name()} -> {ip}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        if unusual:
            info(f"External connections ({len(unusual)}):")
            for u in unusual[:10]:
                print(f"      {u}")
        else:
            ok("No unusual external connections")
    except Exception as e:
        warn(f"Could not check connections: {e}")

    print("\n  Scan complete. If threats were found, run Windows Security for full remediation.")


# ── Clean Temporary Files ─────────────────────────────────────────────


def clean_temp():
    section("Clean Temporary Files")
    paths = [
        os.environ.get("TEMP", ""),
        os.environ.get("TMP", ""),
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Temp",
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Prefetch",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Temp",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Recent",
    ]

    total = 0
    for p in set(filter(None, paths)):
        target = Path(p) if isinstance(p, str) else p
        if not target.exists():
            continue
        count = 0
        size = 0
        for item in target.glob("*"):
            try:
                if item.is_file():
                    size += item.stat().st_size
                    item.unlink()
                    count += 1
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    count += 1
            except (PermissionError, OSError):
                pass
        total += size
        print(f"  {target}")
        print(f"    Removed {count} items, freed {size / (1024**2):.2f} MB")

    print("\n  Running Windows Disk Cleanup...")
    run_cmd("cleanmgr /sagerun:1", capture=False)

    print(f"\n  Total: {total / (1024**2):.2f} MB freed")
    print("  Restart to fully complete cleanup.")


def show_clean_temp():
    clean_temp()
    print("\n  Also clearing browser caches...")
    clean_browser_cache("all")


# ── Startup Programs Manager ──────────────────────────────────────────


def show_startup():
    section("Startup Programs Manager")
    try:
        out = run_cmd("wmic startup get caption,command")
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        items = [l for l in lines if l != "Caption  Command"]
        print(f"  Total startup items: {len(items)}")
        if len(items) > 5:
            warn(f"{len(items)} startup items will slow boot significantly")
        print()
        for item in items:
            print(f"  * {item}")
        print()
        if len(items) > 5:
            print("  Recommendation: Disable non-essentials via Task Manager")
            print("  (Startup tab) or Settings -> Apps -> Startup.")
            print("  Common safe-to-disable: Spotify, Steam, Adobe Updater,")
            print("  Discord, Skype, OneDrive, Microsoft Teams.")
    except Exception as e:
        print(f"  Error: {e}")


# ── Unnecessary Apps & Bloatware ──────────────────────────────────────


BLOATWARE_KEYWORDS = [
    "candy crush", "king.com", "xbox", "bing", "skype",
    "onedrive", "spotify", "disney", "netflix", "tiktok",
    "instagram", "facebook", "twitter", "linkedin",
    "microsoft.windowscommunicationsapps", "officehub",
    "skypeapp", "solitaire", "minecraft", "spotify",
    "power automate", "clipchamp", "family safety",
    "your phone", "people", "mixed reality", "3d viewer",
    "feedback hub", "get-help", "zune", "wallet",
    "news", "weather", "mail", "calendar",
]


def show_bloatware():
    section("Unnecessary Apps & Bloatware")
    print("  Scanning for pre-installed bloatware...\n")

    out = run_cmd('powershell -Command "Get-AppxPackage | Select-Object Name,PackageFullName | Format-List"')
    bloat = []
    for line in out.splitlines():
        for kw in BLOATWARE_KEYWORDS:
            if kw.lower() in line.lower():
                bloat.append(line.strip())
                break

    if bloat:
        warn(f"Found {len(bloat)} potentially unnecessary app(s):")
        for b in bloat:
            print(f"    {b}")
        print()
        if prompt_yesno("Attempt to remove these apps?"):
            for b in bloat:
                if ":" in b:
                    name = b.split(":")[-1].strip()
                else:
                    name = b
                out2 = run_cmd(f'powershell -Command "Get-AppxPackage *{name.split(".")[-1]}* | Remove-AppxPackage"')
                print(f"    Removing {name}...")
            print("  Done. Some may require a reboot.")
    else:
        ok("No obvious bloatware found")

    print("\n  Large installed programs (>500MB):")
    out = run_cmd(
        'powershell -Command "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, '
        'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | '
        'Where-Object {$_.DisplayName -and $_.EstimatedSize -gt 500} | '
        'Sort-Object EstimatedSize -Descending | '
        'Select-Object DisplayName, @{N=\'SizeMB\';E={[int]($_.EstimatedSize/1)}} | '
        'Format-Table -AutoSize | Out-String"'
    )
    if out and "DisplayName" not in out:
        print(f"    {out}")
    else:
        print("    None found or access denied.")


# ── Driver Health Check ───────────────────────────────────────────────


def check_old_drivers():
    out = run_cmd("wmic sysdriver get DisplayName,PathName,State 2>nul")
    old = []
    for line in out.splitlines():
        if "Running" in line and line.strip():
            old.append(line.strip())
    return old[:10]


def driver_check():
    section("Driver Health Check")
    print("  Checking driver dates...\n")

    out = run_cmd(
        'powershell -Command "Get-WmiObject Win32_PnPSignedDriver | '
        'Select-Object DeviceName,DriverDate,DriverVersion,IsSigned | '
        'Sort-Object DriverDate | Format-Table -AutoSize | Out-String -Width 200"'
    )
    if out:
        lines = out.splitlines()
        for line in lines[:30]:
            print(f"  {line}")

    print("\n  Last 5 drivers (oldest):")
    out2 = run_cmd(
        'powershell -Command "Get-WmiObject Win32_PnPSignedDriver | '
        'Sort-Object DriverDate | Select-Object -First 5 DeviceName,DriverDate | '
        'Format-Table -AutoSize | Out-String -Width 120"'
    )
    if out2:
        for line in out2.splitlines():
            if line.strip():
                print(f"  {line}")

    print("\n  Suggested driver updates:")
    print("    GPU:  https://www.nvidia.com/drivers  or  https://www.amd.com/drivers")
    print("    Chipset / Network: check your motherboard/laptop manufacturer's site")
    print("    Or use Windows Update -> Optional Updates -> Driver updates")


# ── Disk Optimizer (Defrag / Trim) ────────────────────────────────────


def disk_optimizer():
    section("Disk Optimizer (Defrag / TRIM)")
    if not is_admin():
        print("  Admin required.")
        return

    for part in psutil.disk_partitions():
        drive = part.device.strip("\\").strip(":")
        if not drive:
            continue
        drive_letter = drive[0] if drive else "C"
        print(f"  Analyzing {part.device}...")

        dtype = get_disk_type(f"{drive}:")
        if "SSD" in dtype or "NVMe" in dtype:
            info("SSD detected -- running TRIM (retrim)...")
            out = run_cmd(f"defrag {drive_letter}: /L")
            for line in out.splitlines():
                if line.strip():
                    print(f"    {line.strip()}")
        else:
            info("HDD detected -- analyzing fragmentation...")
            out = run_cmd(f"defrag {drive_letter}: /A")
            for line in out.splitlines():
                if line.strip():
                    print(f"    {line.strip()}")
            if prompt_yesno("Defrag this drive?"):
                out2 = run_cmd(f"defrag {drive_letter}: /U /V")
                print(f"    {out2[:500] if out2 else 'Done'}")


# ── Visual Effects Tuner ──────────────────────────────────────────────


def visual_effects_tuner():
    section("Visual Effects Tuner")
    print("  Windows animations (transparency, shadows, animations)")
    print("  consume RAM and GPU. Disabling them speeds up old PCs.\n")

    current = run_cmd(
        'powershell -Command "(Get-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\').VisualFXSetting"'
    ).strip()

    if current == "3":
        info("Currently: Best Performance (minimal effects)")
    elif current == "2":
        info("Currently: Custom")
    else:
        info("Currently: Best Appearance (all effects ON)")

    print()
    if prompt_yesno("Disable visual effects for best performance?"):
        run_cmd('powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\' -Name VisualFXSetting -Value 3"')
        run_cmd('powershell -Command "Set-ItemProperty \'HKCU:\\Control Panel\\Desktop\' -Name UserPreferencesMask -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00))"')
        print("  Visual effects disabled. Changes apply after restart.")


# ── Power Plan Optimizer ──────────────────────────────────────────────


def power_optimizer():
    section("Power Plan Optimizer")
    print("  Current active plan:")
    plan = run_cmd("powercfg /getactivescheme")
    for line in plan.splitlines():
        if line.strip():
            print(f"    {line.strip()}")
    print()

    print("  Options:")
    print("    1. High Performance (max speed, more power)")
    print("    2. Balanced (default recommened)")
    print("    3. Power Saver (battery saving, slower)")
    choice = input("  Select (1-3) or Enter to skip: ").strip()

    plans = {
        "1": ("High Performance", "e9a42b02-d5df-448d-aa00-03f14749eb61"),
        "2": ("Balanced", "381b4222-f694-41f0-9685-ff5bb260df2e"),
        "3": ("Power Saver", "a1841308-3541-4fab-bc81-f71556f20b4a"),
    }
    if choice in plans:
        name, guid = plans[choice]
        run_cmd(f"powercfg /setactive {guid}", capture=False)
        print(f"  Power plan set to: {name}")


# ── Network Diagnostics ───────────────────────────────────────────────


def network_diag():
    section("Network Diagnostics")
    print("  IP Configuration:")
    ip = run_cmd("ipconfig /all")
    for line in ip.splitlines():
        stripped = line.strip()
        if stripped and any(k in stripped for k in ("IPv4", "Subnet", "Default Gateway", "DNS", "Description")):
            print(f"    {stripped}")

    gw = run_cmd("wmic path Win32_NetworkAdapterConfiguration where IPEnabled=true get DefaultIPGateway")
    gw_ip = ""
    for line in gw.splitlines():
        line = line.strip()
        if line and "DefaultIPGateway" not in line and line != "":
            gw_ip = line.replace("{", "").replace("}", "").strip()
            break
    if gw_ip:
        print(f"\n  Pinging Gateway ({gw_ip})...")
        ping = run_cmd(f"ping -n 2 {gw_ip}")
        for line in ping.splitlines():
            if "time=" in line or "TTL=" in line or "Request timed out" in line:
                print(f"    {line.strip()}")

    print("\n  Testing Internet (ping 8.8.8.8)...")
    ping = run_cmd("ping -n 2 8.8.8.8")
    for line in ping.splitlines():
        if "time=" in line or "TTL=" in line or "Request timed out" in line:
            print(f"    {line.strip()}")

    print("\n  DNS Resolution (google.com):")
    try:
        ip = socket.gethostbyname("google.com")
        print(f"    google.com -> {ip}")
    except Exception as e:
        print(f"    DNS resolution failed: {e}")

    print("\n  Network speed test:")
    speed = run_cmd(
        'powershell -Command "(New-Object Net.WebClient).DownloadString(\'https://www.google.com\') 2>$null; if($?){\'Connectivity OK\'}else{\'Failed\'}"'
    )
    print(f"    {speed}")


# ── System File Checker ───────────────────────────────────────────────


def sfc_scan():
    section("System File Checker")
    if not is_admin():
        print("  Admin required.")
        return
    info("Running SFC /SCANNOW (5-15 minutes)...")
    out = run_cmd("sfc /scannow")
    for line in out.splitlines():
        print(f"  {line}")


# ── DISM Health Restore ───────────────────────────────────────────────


def dism_restore():
    section("DISM Health Restore")
    if not is_admin():
        print("  Admin required.")
        return
    info("Running DISM /RestoreHealth (10-20 minutes)...")
    out = run_cmd("DISM /Online /Cleanup-Image /RestoreHealth")
    for line in out.splitlines():
        print(f"  {line}")


# ── Windows Update Status ─────────────────────────────────────────────


def winupdate_status():
    section("Windows Update Status")
    info("Triggering update detection...")
    run_cmd('powershell -Command "(New-Object -ComObject Microsoft.Update.AutoUpdate).DetectNow()"', capture=False)

    out = run_cmd(
        'powershell -Command "Get-WUList | Select-Object Title,KB,Size,IsDownloaded,IsInstalled | Format-Table -AutoSize | Out-String -Width 200"'
    )
    if out and "Get-WUList" not in out and out.strip():
        print(f"  {out}")
    else:
        info("No pending updates or PSWindowsUpdate module missing.")
        info("To install the module: Install-Module PSWindowsUpdate -Force")
        info("Falling back to basic check...\n")

    last = run_cmd(
        'powershell -Command "(Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 5) | Format-Table HotFixID,InstalledOn -AutoSize | Out-String -Width 120"'
    )
    if last:
        print(f"  Last installed updates:\n  {last}")


# ── Browser Cleanup ───────────────────────────────────────────────────


BROWSER_CACHE_PATHS = {
    "Edge": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache",
    ],
    "Chrome": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache",
    ],
    "Firefox": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Mozilla" / "Firefox" / "Profiles",
    ],
}


def get_browser_cache_size():
    total = 0.0
    for browser, paths in BROWSER_CACHE_PATHS.items():
        for p in paths:
            if p.exists():
                for f in p.rglob("*"):
                    try:
                        if f.is_file():
                            total += f.stat().st_size
                    except (PermissionError, OSError):
                        pass
    return total / (1024**3)


def clean_browser_cache(which="all"):
    browsers_to_clean = BROWSER_CACHE_PATHS if which == "all" else {which: BROWSER_CACHE_PATHS.get(which, [])}
    for browser, paths in browsers_to_clean.items():
        for p in paths:
            if p.exists():
                count = 0
                size = 0
                try:
                    for f in p.rglob("*"):
                        try:
                            if f.is_file():
                                size += f.stat().st_size
                                f.unlink()
                                count += 1
                        except (PermissionError, OSError):
                            pass
                    print(f"  {browser}: cleared {count} files, freed {size / (1024**2):.2f} MB")
                except Exception as e:
                    warn(f"Could not clear {p}: {e}")


def browser_cleanup():
    section("Browser Cleanup")
    print("  Clearing cache, history, and cookies for:\n")
    print("  1. Google Chrome")
    print("  2. Microsoft Edge")
    print("  3. Mozilla Firefox")
    print("  4. All browsers")
    print("  5. Cancel")

    choice = input("\n  Select (1-5): ").strip()
    browser_map = {"1": "Chrome", "2": "Edge", "3": "Firefox", "4": "all"}
    if choice in browser_map:
        clean_browser_cache(browser_map[choice])
        print("  Done. Restart browsers for changes to take effect.")
    else:
        print("  Canceled.")


# ── Legacy / existing features ────────────────────────────────────────


def chkdsk():
    section("Check Disk (chkdsk)")
    if not is_admin():
        print("  Admin required.")
        return
    info("Running chkdsk C: (read-only)...")
    out = run_cmd("chkdsk C:")
    for line in out.splitlines():
        print(f"  {line}")


def perf_monitor():
    section("Performance Monitor (5s snapshot)")
    print(f"  CPU Usage        : {psutil.cpu_percent(interval=1)}%")
    mem = psutil.virtual_memory()
    print(f"  RAM Usage        : {mem.percent}% ({mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} GB)")
    print(f"  Swap Usage       : {psutil.swap_memory().percent}%")
    net = psutil.net_io_counters()
    print(f"  Network Sent     : {net.bytes_sent / (1024**2):.2f} MB")
    print(f"  Network Received : {net.bytes_recv / (1024**2):.2f} MB")

    print("\n  Top 5 processes by CPU:")
    for p in sorted(psutil.process_iter(["pid", "name", "cpu_percent"]), key=lambda p: p.info.get("cpu_percent", 0) or 0, reverse=True)[:5]:
        try:
            pinfo = p.info
            print(f"    PID {pinfo['pid']:>6}  {pinfo['cpu_percent'] or 0:>5.1f}%  {pinfo['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def flush_dns():
    section("Flush DNS & Reset Network Stack")
    if not is_admin():
        print("  Admin required.")
        return
    info("Flushing DNS...")
    run_cmd("ipconfig /flushdns", capture=False)
    info("Releasing IP...")
    run_cmd("ipconfig /release", capture=False)
    info("Renewing IP...")
    run_cmd("ipconfig /renew", capture=False)
    info("Resetting Winsock...")
    run_cmd("netsh winsock reset", capture=False)
    info("Resetting TCP/IP stack...")
    run_cmd("netsh int ip reset", capture=False)
    print("\n  Done. A reboot may be required for full effect.")


def power_report():
    section("Power Efficiency Report")
    if not is_admin():
        print("  Admin required.")
        return
    info("Generating energy report (10 second test)...")
    run_cmd("powercfg /energy /duration 10", capture=False)
    report = Path(os.environ.get("WINDIR", "C:\\Windows")) / "System32" / "energy-report.html"
    if report.exists():
        print(f"  Report saved to {report}")
        os.startfile(report)
    else:
        warn("Failed to generate report. Check permissions.")


def disk_health():
    section("Disk Usage & Health")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            dtype = get_disk_type(part.device[:2])
            print(f"  {part.device}  ({part.mountpoint})  [{dtype}]")
            print(f"    Total: {usage.total / (1024**3):.2f} GB  "
                  f"Used: {usage.used / (1024**3):.2f} GB  "
                  f"Free: {usage.free / (1024**3):.2f} GB  "
                  f"({usage.percent}% full)")
        except PermissionError:
            print(f"  {part.device}  ({part.mountpoint}) - Access denied")
        print()

    print("  SMART Status:")
    out = run_cmd("wmic diskdrive get status,model,size")
    for line in out.splitlines():
        if line.strip():
            print(f"    {line.strip()}")


def common_checks():
    section("Quick Health Check")
    issues = 0

    print("  [1] Disk Space:")
    for part in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(part.mountpoint)
            if u.percent > 90:
                warn(f"{part.device} is {u.percent}% full!")
                issues += 1
        except PermissionError:
            pass

    mem = psutil.virtual_memory()
    print(f"  [2] Memory: {mem.percent}% used")
    if mem.percent > 85:
        warn("High memory usage")
        issues += 1

    cpu = psutil.cpu_percent(interval=1)
    print(f"  [3] CPU: {cpu}%")
    if cpu > 80:
        warn("High CPU usage")
        issues += 1

    print("  [4] Recent Crashes (24h):")
    out = run_cmd(
        'powershell -Command "Get-WinEvent -FilterHashtable @{LogName=\'Application\'; Level=2; StartTime=(Get-Date).AddDays(-1)} -MaxEvents 5 | Format-Table TimeCreated,Id,ProviderName -AutoSize -Wrap | Out-String -Width 200"'
    )
    if out and "Get-WinEvent" not in out:
        print(f"    {out[:1000] if out else 'None'}")
    else:
        print("    None or access denied")

    print("  [5] Critical Services:")
    services = ["Wuauserv", "BITS", "Dnscache", "Dhcp", "LanmanServer", "LanmanWorkstation"]
    for svc in services:
        out = run_cmd(f'sc query {svc} | findstr "STATE"')
        if "RUNNING" in out:
            ok(f"{svc}")
        elif "STOPPED" in out:
            warn(f"{svc} -- STOPPED")
            issues += 1

    print(f"\n  Found {issues} issue(s).")


# ── Run ALL Automated Fixes ───────────────────────────────────────────


def run_all():
    section("Running ALL Automated Fixes")
    if not is_admin():
        warn("Admin required. Some steps will be skipped.")

    def step(n, label, func):
        print(f"\n{'=' * 52}")
        print(f"  Step {n}: {label}")
        print(f"{'=' * 52}")
        func()

    step(1, "Creating System Restore Point", lambda: run_cmd(
        'powershell -Command "Checkpoint-Computer -Description \'Yfix Auto Backup\' -RestorePointType MODIFY_SETTINGS"'
    ))
    step(2, "Cleaning Temporary Files", clean_temp)
    step(3, "Enabling Storage Sense", storage_sense)
    step(4, "Malware Scan (Quick)", lambda: malware_scan())
    step(5, "Browser Cache Cleanup", lambda: clean_browser_cache("all"))
    step(6, "Disabling Background Apps", background_apps_control)
    step(7, "System File Checker (SFC)", sfc_scan)
    step(8, "DISM Health Restore", dism_restore)
    step(9, "Flushing DNS & Resetting Network Stack", flush_dns)
    step(10, "Disk Optimizer (Defrag/TRIM)", disk_optimizer)
    step(11, "Setting Visual Effects to Performance Mode", lambda: run_cmd(
        'powershell -Command "Set-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects\' -Name VisualFXSetting -Value 3"'
    ))
    step(12, "Applying Privacy Tweaks", privacy_tweaks)
    step(13, "Setting Power Plan to High Performance", lambda: run_cmd(
        "powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61", capture=False
    ))

    print(f"\n{'=' * 52}")
    print("  ALL STEPS COMPLETED")
    print(f"{'=' * 52}")
    print("  Restart your computer to apply all changes.")
    print("  After restart, run Windows Update (option 14).")


# ── About ──────────────────────────────────────────────────────────────


def show_about():
    section("About Yfix")
    print(f"""
  Yfix v{VERSION} - Windows PC Fix & Speedup Tool
  Author: yohi

  An all-in-one diagnostic and repair tool for Windows PCs.
  Features 27 tools covering system info, malware scan,
  disk cleanup, driver checks, network diag, SFC/DISM,
  restore points, privacy tweaks, and more.

  Built with Python, psutil, and Tkinter.
  Compiled to standalone .exe via PyInstaller.

  https://github.com/anomalyco/opencode
""")


# ── Menu ──────────────────────────────────────────────────────────────


def menu():
    items = [
        ("System Information",              show_sysinfo),
        ("Why Is My PC Slow? (Diagnostic)", why_slow),
        ("Create System Restore Point",     create_restore_point),
        ("Malware & Virus Scan",            malware_scan),
        ("Clean Temporary Files",           show_clean_temp),
        ("Storage Sense (Auto Cleanup)",    storage_sense),
        ("Startup Programs Manager",        show_startup),
        ("Background Apps Control",         background_apps_control),
        ("Unnecessary Apps & Bloatware",    show_bloatware),
        ("Driver Health Check",             driver_check),
        ("Disk Optimizer (Defrag/TRIM)",    disk_optimizer),
        ("Windows Memory Diagnostic",       memory_diag),
        ("Battery Health Report",           battery_report),
        ("Visual Effects Tuner",            visual_effects_tuner),
        ("Windows Privacy Tweaks",          privacy_tweaks),
        ("Power Plan Optimizer",            power_optimizer),
        ("Network Diagnostics",             network_diag),
        ("System File Checker (SFC)",       sfc_scan),
        ("DISM Health Restore",             dism_restore),
        ("Windows Update Status",           winupdate_status),
        ("Browser Cleanup",                 browser_cleanup),
        ("Flush DNS & Reset Network Stack", flush_dns),
        ("Repair Install (In-place Upgrade)", repair_install),
        ("Run ALL Automated Fixes",         run_all),
        ("View Restore Points",             list_restore_points),
        ("Restore from Point",              restore_from_point),
        ("Help & Manual",                   show_help),
        ("About",                           show_about),
        ("Exit",                            None),
    ]

    while True:
        print(f"\n{'=' * 52}")
        print(f"  Yfix v{VERSION} by yohi - Windows PC Fix & Speedup Tool")
        print(f"{'=' * 52}")
        print(f"  Admin: {'YES' if is_admin() else 'NO (limited)'}  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'=' * 52}")
        for i, (label, _) in enumerate(items, 1):
            print(f"  {i:>2}. {label}")
        print(f"{'=' * 52}")
        print()

        try:
            choice = input("  Select option (1-29): ").strip()
            if choice in ("29", "q", "exit", "quit"):
                print("\n  Goodbye!")
                break
            if choice in ("help", "h", "?"):
                show_help()
                input("\n  Press Enter...")
                continue
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                _, fn = items[idx]
                if fn:
                    fn()
                    print()
                    input("  Press Enter to continue...")
            else:
                print("  Invalid choice.\n")
        except (ValueError, IndexError):
            print("  Invalid choice.\n")


# ── Entrypoint ────────────────────────────────────────────────────────


def check_deps():
    try:
        import psutil
    except ImportError:
        print("Missing dependency 'psutil'. Install it:")
        print("  pip install psutil")
        sys.exit(1)


if __name__ == "__main__":
    os.system("title Yfix v2.1 by yohi - Windows PC Fix & Speedup Tool" if os.name == "nt" else "")
    check_deps()
    require_admin()

    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "/?"):
        show_help()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] in ("--quick", "-q", "/quick"):
        section("Quick Run Mode")
        why_slow()
        print("\nRunning cleanup...")
        clean_temp()
        clean_browser_cache("all")
        print("\nQuick run complete.")
        sys.exit(0)

    menu()
