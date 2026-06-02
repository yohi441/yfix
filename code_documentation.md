# Yfix Code Documentation

## Architecture Overview

Yfix is a two-interface tool backed by a single shared logic layer.

```
                    ┌─────────────────────────────────────────┐
                    │              yfix.py                     │
                    │  (CLI + all diagnostic/repair logic)    │
                    │                                         │
                    │  43 functions: utilities, diagnostics,  │
                    │  repairs, system tools, menu             │
                    └──────────┬──────────────────────┬───────┘
                               │                      │
            monkey-patches     │                      │  imports & calls
            input() and        │                      │
            prompt_yesno()     │                      │
                               ▼                      ▼
                    ┌──────────────────┐   ┌─────────────────────┐
                    │   yfix_gui.py    │   │   Yfix.exe /        │
                    │  (Tkinter GUI)   │   │   Yfix-CLI.exe      │
                    │                  │   │   (PyInstaller)     │
                    │  TextRedirector  │   │                     │
                    │  threads long    │   │  runw.exe (GUI)     │
                    │  tasks           │   │  run.exe (CLI)      │
                    └──────────────────┘   └─────────────────────┘
```

### File Roles

| File | Role |
|------|------|
| `yfix.py` | All logic lives here. CLI entrypoint, 43 functions, menu loop, utility helpers. |
| `yfix_gui.py` | Tkinter wrapper. Imports `yfix`, monkey-patches `input()`/`prompt_yesno()`, redirects stdout to a `ScrolledText` widget, runs long tasks in threads. |
| `build_exe.bat` | Batch script that runs PyInstaller to produce both GUI and CLI `.exe` files. |

### How the GUI Wraps the CLI

The GUI never duplicates logic. Instead it:

1. **Imports `yfix`** — all functions are used directly.
2. **Monkey-patches `yfix.input` and `yfix.prompt_yesno`** — replaces CLI `input()` with `simpledialog.askstring()` and `y/n` prompts with `messagebox.askyesno()`.
3. **Redirects stdout** via `contextlib.redirect_stdout(TextRedirector)` — captures all `print()` calls from `yfix` functions and displays them in a `ScrolledText` widget.
4. **Threads long-running tasks** — SFC, DISM, malware scan, "Run ALL", disk optimizer, and temp cleanup run in `threading.Thread(daemon=True)` so the GUI stays responsive.
5. **Shows progress** — an indeterminate `ttk.Progressbar` appears during any task, driven by `set_busy()`/`set_idle()`.

---

## yfix.py — Function Reference

### Utility Functions

#### `is_admin()`
- **Line:** 32
- **Purpose:** Checks if the current process has Administrator privileges.
- **Mechanism:** Calls `ctypes.windll.shell32.IsUserAnAdmin()`.
- **Returns:** `True` if admin, `False` otherwise (including on non-Windows).
- **Requires admin:** No (self-check)
- **Used by:** `require_admin()`, `menu()`, `update_status()` (GUI), many feature functions that check early and return if not admin.

#### `run_cmd(cmd, capture=True)`
- **Line:** 39
- **Purpose:** Runs a shell command and returns its output or exit code.
- **Args:**
  - `cmd` (str) — command string to execute via `shell=True`.
  - `capture` (bool) — if `True`, returns stdout as string; if `False`, runs without capturing (output goes to console) and returns the return code.
- **Mechanism:** Uses `subprocess.run()` with `CREATE_NO_WINDOW` flag when not capturing (to avoid flashing a console window for background commands).
- **Returns:** `str` (stdout) if `capture=True`, `int` (return code) if `capture=False`, or `"[ERROR] ..."` string on exception.
- **Requires admin:** Depends on the command passed.

#### `require_admin()`
- **Line:** 47
- **Purpose:** Prints a notice if not running as admin. Does NOT elevate — just warns.
- **Returns:** None (prints to stdout).
- **Requires admin:** No

#### `run_as_admin()`
- **Line:** 54
- **Purpose:** Attempts to relaunch the current script/exe with admin privileges via a UAC prompt (`ShellExecuteW` with `"runas"` verb). If the user accepts the UAC prompt, the current process exits and the new elevated process runs. If the user cancels, execution continues with a warning.
- **Returns:** Never returns if UAC approved (`sys.exit(0)`).
- **Requires admin:** No (self-check)
- **Called by:** `yfix.py` entrypoint, `yfix_gui.py` `main()`.

#### `confirm_destructive(action_name)`
- **Line:** 63
- **Purpose:** Prints a warning that the action modifies system settings, then prompts to create a system restore point before proceeding. Called at the start of destructive functions to give the user a safety net.
- **Args:**
  - `action_name` (str) — display name of the action (e.g. "Privacy Tweaks", "Bloatware Removal").
- **Returns:** None (may call `create_restore_point()` if user agrees).
- **Requires admin:** No (but `create_restore_point()` requires admin).
- **Called by:** `privacy_tweaks()`, `visual_effects_tuner()`, `show_bloatware()`.

#### `section(title)`
- **Line:** 53
- **Purpose:** Prints a formatted section header. Used at the top of every feature function.
- **Args:**
  - `title` (str) — the section name to display.
- **Output format:**
  ```
  ====================================================
    title
  ====================================================
  ```

#### `warn(msg)`
- **Line:** 59
- **Print helper:** `"  [!!] {msg}"`

#### `ok(msg)`
- **Line:** 63
- **Print helper:** `"  [OK] {msg}"`

#### `info(msg)`
- **Line:** 67
- **Print helper:** `"  [..] {msg}"`

#### `prompt_yesno(question)`
- **Line:** 71
- **Purpose:** Asks a yes/no question and returns the answer.
- **Args:**
  - `question` (str) — the question text (appended with " (y/n): ").
- **Returns:** `True` for y/yes, `False` otherwise.
- **Note:** This function is monkey-patched by the GUI with `messagebox.askyesno()`.

---

### Help & Manual

#### `show_help()`
- **Line:** 79
- **Purpose:** Prints a comprehensive help text covering all 28 menu options, admin requirements, and tips for speeding up a slow PC.
- **Requires admin:** No
- **Called by:** Menu option 25, `--help` flag.

---

### System Information

#### `get_disk_type(path="C:")`
- **Line:** 246
- **Purpose:** Determines whether a drive is SSD or HDD.
- **Args:**
  - `path` (str) — drive letter with colon, e.g. `"C:"`.
- **Mechanism:** Checks via: (1) `wmic diskdrive` MediaType, (2) PowerShell `Get-PhysicalDisk`, (3) `wmic diskdrive` Model name for NVMe/SSD keywords.
- **Returns:** `"SSD"`, `"HDD"`, or `"HDD (or unknown)"`.
- **Requires admin:** No
- **Used by:** `show_sysinfo()`, `why_slow()`, `disk_optimizer()`.

#### `show_sysinfo()`
- **Line:** 266
- **Purpose:** Displays comprehensive system information: hostname, OS version, CPU (physical/logical cores), RAM (total/available), GPU, disk type, boot time, uptime, CPU temperature.
- **Requires admin:** No (temperature reading may be limited without admin).
- **Called by:** Menu option 1.

---

### Restore Points

#### `create_restore_point()`
- **Line:** 307
- **Purpose:** Creates a System Restore Point via PowerShell `Checkpoint-Computer`.
- **Flow:** Prompts for description → runs PowerShell command → reports success/failure → offers to open System Protection settings if it failed.
- **Requires admin:** Yes
- **Called by:** Menu option 3, `run_all()`.

#### `list_restore_points()`
- **Line:** 327
- **Purpose:** Lists all saved system restore points showing SequenceNumber, Description, CreationTime, and EventType.
- **Mechanism:** Runs `Get-ComputerRestorePoint` PowerShell command.
- **Requires admin:** Yes
- **Called by:** Menu option 26.

#### `restore_from_point()`
- **Line:** 349
- **Purpose:** Restores the system to a specified restore point.
- **Flow:** Fetches restore points → prompts for SequenceNumber → warns about reboot → calls `Restore-Computer` PowerShell command → initiates system restart.
- **Requires admin:** Yes
- **Called by:** Menu option 27.

---

### Storage & Cleanup

#### `storage_sense()`
- **Line:** 389
- **Purpose:** Enables Windows Storage Sense to auto-delete temp files and recycle bin monthly.
- **Mechanism:** Reads current registry value, sets `01` key to enable if not already enabled.
- **Requires admin:** Yes
- **Called by:** Menu option 6, `run_all()`.

#### `clean_temp()`
- **Line:** 883
- **Purpose:** Deletes temporary files from TEMP, TMP, Windows\Temp, Prefetch, LocalAppData\Temp, and Windows\Recent. Also runs `cleanmgr /sagerun:1`.
- **Requires admin:** Yes (for some system temp directories).
- **Called by:** `show_clean_temp()`, `run_all()`.

#### `show_clean_temp()`
- **Line:** 923
- **Purpose:** Wrapper that calls `clean_temp()` then also clears browser caches.
- **Requires admin:** Partial
- **Called by:** Menu option 5.

---

### Startup & Background Apps

#### `show_startup()`
- **Line:** 932
- **Purpose:** Lists all startup programs via `wmic startup`. Shows total count with a warning if more than 5 items (a common cause of slow boot).
- **Requires admin:** No
- **Called by:** Menu option 7.

#### `background_apps_control()`
- **Line:** 415
- **Purpose:** Lists Windows Store apps registered for background activity via PowerShell. Offers to disable background access for all of them, freeing RAM and CPU.
- **Requires admin:** Yes
- **Called by:** Menu option 8, `run_all()`.

---

### Bloatware

#### `show_bloatware()`
- **Line:** 970
- **Purpose:** Scans for pre-installed bloatware by matching against `BLOATWARE_KEYWORDS` list (Candy Crush, Xbox, Skype, OneDrive, and many more). Lists large installed programs (>500MB). Offers to remove detected bloatware.
- **Requires admin:** Yes
- **Called by:** Menu option 9.

**`BLOATWARE_KEYWORDS`** (line 957): A list of 30+ keyword strings used to match against installed AppxPackage names.

---

### Malware & Virus Scan

**`SUSPICIOUS_NAMES`** (line 760): A list of process names and substrings associated with cryptominers, trojans, and malware masquerading as system processes.

**`SUSPICIOUS_LOCATIONS`** (line 768): Two Path objects pointing to common startup folders used for malware persistence.

#### `check_suspicious_processes()`
- **Line:** 774
- **Purpose:** Iterates all running processes and checks their name and command line against `SUSPICIOUS_NAMES`.
- **Returns:** `list[str]` — names of suspicious processes found, or empty list.
- **Requires admin:** No (some process access may be denied without admin).

#### `malware_scan()`
- **Line:** 788
- **Purpose:** Five-stage malware scan:
  1. **Process scan** — calls `check_suspicious_processes()`.
  2. **Startup locations** — checks common autorun folders for files.
  3. **Registry autoruns** — queries Run/RunOnce keys in HKLM and HKCU.
  4. **Windows Defender Quick Scan** — runs MpCmdRun.exe with `-ScanType 1` (Quick Scan), timeout 15 minutes.
  5. **Network connections** — lists external established connections (non-private IPs).
- **Requires admin:** Yes (for Defender scan and some process checks).
- **Called by:** Menu option 4, `run_all()`.

---

### Drivers

#### `check_old_drivers()`
- **Line:** 1017
- **Purpose:** Gets a list of running system drivers via `wmic sysdriver`.
- **Returns:** `list[str]` — up to 10 driver lines that are currently "Running".
- **Requires admin:** No
- **Used by:** `why_slow()`.

#### `driver_check()`
- **Line:** 1026
- **Purpose:** Shows all PnP signed drivers with their dates, versions, and signing status. Also shows the 5 oldest drivers. Provides links to GPU/chipset driver update pages.
- **Requires admin:** No
- **Called by:** Menu option 10.

---

### Disk

#### `disk_optimizer()`
- **Line:** 1060
- **Purpose:** Analyzes each mounted drive. SSD → runs TRIM (`defrag /L`). HDD → runs defrag analysis and offers to defrag.
- **Requires admin:** Yes
- **Called by:** Menu option 11, `run_all()`.

#### `disk_health()`
- **Line:** 1382
- **Purpose:** Shows disk usage for all partitions (total/used/free/percent) and SMART status via WMIC.
- **Requires admin:** No (SMART may require admin for some drives).
- **Called by:** Not directly in menu (legacy function).

---

### Memory

#### `memory_diag()`
- **Line:** 441
- **Purpose:** Schedules Windows Memory Diagnostic (`mdsched.exe`) to run on next reboot. Advises the user to save work and restart.
- **Requires admin:** Yes
- **Called by:** Menu option 12.

---

### Battery

#### `battery_report()`
- **Line:** 456
- **Purpose:** Generates an HTML battery health report via `powercfg /batteryreport`. Output saved to `%TEMP%\battery-report.html`. Displays key metrics: design capacity vs full charge capacity (wear level), cycle count.
- **Requires admin:** No
- **Called by:** Menu option 13.

---

### Visual Effects

#### `visual_effects_tuner()`
- **Line:** 1094
- **Purpose:** Reads current visual effects setting. Offers to disable all animations, transparency, and shadows for best performance. Writes to registry: `VisualFXSetting = 3` and `UserPreferencesMask`.
- **Requires admin:** Yes
- **Called by:** Menu option 14, `run_all()`.

---

### Privacy

#### `privacy_tweaks()`
- **Line:** 480
- **Purpose:** Disables telemetry, advertising ID, Windows tips, suggested content, activity history, app diagnostics, browser data sharing, and inventory collector via registry settings. Each is individually checked and disabled if needed. Keeps a count of changes made.
- **Requires admin:** Yes
- **Called by:** Menu option 15, `run_all()`.

---

### Power

#### `power_optimizer()`
- **Line:** 1120
- **Purpose:** Shows current active power plan. Offers to switch to High Performance, Balanced, or Power Saver using `powercfg /setactive` with the corresponding GUID.
- **Requires admin:** Yes
- **Called by:** Menu option 16, `run_all()`.

#### `power_report()`
- **Line:** 1367
- **Purpose:** Generates a power efficiency report via `powercfg /energy` (10 second test). Opens the resulting HTML report.
- **Requires admin:** Yes
- **Called by:** Not directly in menu (legacy function).

---

### Network

#### `network_diag()`
- **Line:** 1149
- **Purpose:** Runs a multi-step network diagnostic:
  1. Shows IP configuration (IPv4, subnet, gateway, DNS).
  2. Pings the default gateway.
  3. Pings 8.8.8.8 (Internet connectivity).
  4. Resolves google.com (DNS test).
  5. Quick web connectivity check via PowerShell.
- **Requires admin:** No
- **Called by:** Menu option 17.

#### `flush_dns()`
- **Line:** 1349
- **Purpose:** Resets the full network stack: flushes DNS, releases/renews IP, resets Winsock and TCP/IP stack.
- **Requires admin:** Yes
- **Called by:** Menu option 22, `run_all()`.

---

### System File Repair

#### `sfc_scan()`
- **Line:** 1195
- **Purpose:** Runs `sfc /scannow` (System File Checker) to repair corrupted Windows system files. Takes 5–15 minutes.
- **Requires admin:** Yes
- **Called by:** Menu option 18, `run_all()`.

#### `dism_restore()`
- **Line:** 1209
- **Purpose:** Runs `DISM /Online /Cleanup-Image /RestoreHealth` to repair Windows component store corruption. Takes 10–20 minutes. Should be run before SFC for best results.
- **Requires admin:** Yes
- **Called by:** Menu option 19, `run_all()`.

---

### Windows Update

#### `winupdate_status()`
- **Line:** 1223
- **Purpose:** Triggers update detection via COM object `Microsoft.Update.AutoUpdate`. Attempts to list pending updates via the `PSWindowsUpdate` PowerShell module (if installed). Falls back to displaying the last 5 installed hotfixes.
- **Requires admin:** No
- **Called by:** Menu option 20.

---

### Browser Cleanup

**`BROWSER_CACHE_PATHS`** (line 1248): Dictionary mapping browser names to lists of cache directory `Path` objects for Edge, Chrome, and Firefox.

#### `get_browser_cache_size()`
- **Line:** 1263
- **Purpose:** Walks all browser cache directories and sums file sizes.
- **Returns:** `float` — total cache size in GB.
- **Requires admin:** No
- **Used by:** `why_slow()`.

#### `clean_browser_cache(which="all")`
- **Line:** 1277
- **Purpose:** Deletes browser cache files for specified browser(s).
- **Args:**
  - `which` (str) — `"all"`, `"Chrome"`, `"Edge"`, or `"Firefox"`.
- **Requires admin:** No
- **Called by:** `browser_cleanup()`, `show_clean_temp()`.

#### `browser_cleanup()`
- **Line:** 1298
- **Purpose:** Interactive menu for selecting which browser(s) to clean. Calls `clean_browser_cache()` with the user's choice.
- **Requires admin:** No
- **Called by:** Menu option 21.

---

### Diagnostics & Reports

#### `why_slow()`
- **Line:** 557
- **Purpose:** Full PC slowness diagnostic checking 15+ factors:
  1. Disk space (<10% or <20% free)
  2. Memory usage (>90% or >80%)
  3. CPU usage (>90% or >70%)
  4. Process count (>180 or >120)
  5. Startup program count (>10 or >5)
  6. Suspicious/malware processes
  7. Driver age (old drivers)
  8. Disk health (SMART status)
  9. Disk type (HDD vs SSD)
  10. Visual effects setting
  11. Power plan (Power Saver detected)
  12. Browser cache size (>2 GB)
  13. Windows Update recency (>60 or >30 days)
  14. Pagefile size (small pagefile + low RAM)
  15. CPU temperature (>85°C = thermal throttling)
- Each check is assigned a severity level (1=CRITICAL through 7=LOW). Issues are sorted and displayed in a report with recommended actions.
- **Requires admin:** No
- **Called by:** Menu option 2, `--quick` mode, `run_all()`.

#### `common_checks()`
- **Line:** 1404
- **Purpose:** Quick health check covering disk space, memory, disk health SMART status, and battery health. Simpler than `why_slow()`.

#### `perf_monitor()`
- **Line:** 1330
- **Purpose:** Takes a 5-second performance snapshot showing CPU%, RAM%, swap%, network I/O, and top 5 processes by CPU usage.
- **Requires admin:** No

#### `chkdsk()`
- **Line:** 1319
- **Purpose:** Runs read-only `chkdsk C:` to check for file system errors without repairing.
- **Requires admin:** Yes

---

### Repair Install

#### `repair_install()`
- **Line:** 535
- **Purpose:** Opens the official Microsoft Media Creation Tool download page in the default browser. This is an in-place upgrade guide — reinstalls Windows while keeping files and apps.
- **Requires admin:** No
- **Called by:** Menu option 23.

---

### Run All

#### `run_all()`
- **Line:** 1455
- **Purpose:** Runs all automated fixes sequentially:
  1. Create restore point (`create_restore_point`)
  2. Clean temp files (`show_clean_temp`)
  3. Enable Storage Sense (`storage_sense`)
  4. Malware scan (`malware_scan`)
  5. Browser cleanup (`browser_cleanup`)
  6. Disable background apps (`background_apps_control`)
  7. SFC scan (`sfc_scan`)
  8. DISM restore (`dism_restore`)
  9. Flush DNS (`flush_dns`)
  10. Disk optimizer (`disk_optimizer`)
  11. Visual effects performance mode (`visual_effects_tuner`)
  12. Privacy tweaks (`privacy_tweaks`)
  13. High performance power plan (`power_optimizer`)
- Estimated time: 30 minutes.
- **Requires admin:** Yes (most steps require it).
- **Called by:** Menu option 24.

---

### About

#### `show_about()`
- **Line:** 1496
- **Purpose:** Displays version info, author credit (yohi), tool description, feature count, tech stack, and GitHub repository URL.
- **Requires admin:** No
- **Called by:** Menu option 28.

---

### CLI Entrypoint

#### `menu()`
- **Line:** 1517
- **Purpose:** Main interactive menu loop. Displays 29 options (1–28 features + Exit on 29). Accepts input by number, also accepts "q"/"quit"/"exit" and "help"/"h"/"?".
- **Flow:** Prints header with version, admin status, and timestamp → loops asking for choice → calls selected function → waits for Enter before re-displaying menu.
- **Requires admin:** No

#### `check_deps()`
- **Line:** 1586
- **Purpose:** Verifies that `psutil` is importable. Exits with an install instruction if missing.

#### `main` (script entrypoint)
- **Line:** 1595
- **Purpose:** Sets console title, checks deps, warns about admin, parses CLI args:
  - `--help` / `-h` / `/?` → shows help and exits.
  - `--quick` / `-q` / `/quick` → runs `why_slow()` + `clean_temp()` + `clean_browser_cache("all")`, then exits.
  - No args → runs `menu()`.

---

## yfix_gui.py — Class & Method Reference

### `TextRedirector`
- **Line:** 21
- **Purpose:** A file-like object that redirects `print()` output to a Tkinter `ScrolledText` widget.
- **Methods:**
  - `write(text)` — inserts text at the end of the widget and auto-scrolls.
  - `flush()` — no-op (required for file-like interface).

### `gui_input(prompt_text="")`
- **Line:** 36
- **Purpose:** GUI replacement for built-in `input()`. Shows a `simpledialog.askstring()` dialog.
- **Returns:** `str` — user input, or empty string if cancelled.

### `gui_prompt_yesno(question)`
- **Line:** 40
- **Purpose:** GUI replacement for `prompt_yesno()`. Shows a `messagebox.askyesno()` dialog.
- **Returns:** `bool`

### `R2FixGUI` class

#### `__init__(self, root)`
- **Line:** 48
- **Purpose:** Initializes the GUI window, monkey-patches `yfix.input` and `yfix.prompt_yesno`, builds the UI, and starts the admin status poll loop.
- **Args:**
  - `root` (tk.Tk) — the main Tkinter window.

#### `build_ui(self)`
- **Line:** 61
- **Purpose:** Creates all UI widgets:
  - **Top frame:** title label + admin status badge.
  - **Admin banner:** yellow warning label (shown only when not admin).
  - **Button grid:** 28 buttons in 5 columns, each bound to `run_option(n)`.
  - **Progress frame:** hidden by default, shows label + indeterminate progress bar.
  - **Output area:** dark-themed `ScrolledText` widget (Consolas 9pt, bg #1e1e1e).
  - **Bottom frame:** "Clear Output" and "Exit" buttons.
  - **Redirector:** creates `TextRedirector` attached to the output widget.

#### `update_status(self)`
- **Line:** 135
- **Purpose:** Polls admin status every 5 seconds. Updates the admin label text and toggles the admin banner visibility.
- **Mechanism:** Calls `self.root.after(5000, self.update_status)` for recurring timer.

#### `clear_output(self)`
- **Line:** 144
- **Purpose:** Deletes all text from the output widget.

#### `set_busy(self, label)`
- **Line:** 147
- **Purpose:** Disables all buttons and the clear button, shows the progress bar with the task label, starts the indeterminate animation at 10ms intervals.
- **Args:**
  - `label` (str) — the name of the running task.

#### `set_idle(self)`
- **Line:** 156
- **Purpose:** Re-enables all buttons, stops and hides the progress bar. Guards against double-call with `self.running` flag.

#### `run_option(self, option_num)`
- **Line:** 166
- **Purpose:** Main dispatch method. Maps option number (1–28) to a `(label, function)` pair. Calls `set_busy()`, forces a UI update via `update_idletasks()`, then dispatches to either `run_sync()` or `run_in_thread()` based on whether the task is in the `long_tasks` set.
- **Args:**
  - `option_num` (int) — 1–28.
- **Long tasks** (run in thread): SFC, DISM, malware scan, Run ALL, disk optimizer, clean temp.

#### `run_sync(self, func, label)`
- **Line:** 224
- **Purpose:** Runs a short task synchronously on the main thread within a `redirect_stdout` context. Prints OK/FAIL to the output widget when done.
- **Args:**
  - `func` (callable) — the yfix function to run.
  - `label` (str) — display name.

#### `run_in_thread(self, func, label)`
- **Line:** 235
- **Purpose:** Runs a long task in a `threading.Thread`. Uses `self.root.after(0, self.set_idle)` to return to idle state on the main thread when done.
- **Args:**
  - `func` (callable) — the yfix function to run.
  - `label` (str) — display name.

---

## Build System

### `build_exe.bat`

Produces two standalone executables:

1. **`dist\Yfix.exe`** (GUI, ~10.7 MB)
   ```
   pyinstaller --onefile --windowed --name="Yfix" --hidden-import=psutil yfix_gui.py
   ```
   - `--windowed` → no console window (runs as a GUI app).
   - Entrypoint: `yfix_gui.py` → imports and wraps `yfix`.

2. **`dist\Yfix-CLI.exe`** (Console, ~7.7 MB)
   ```
   pyinstaller --onefile --name="Yfix-CLI" --hidden-import=psutil yfix.py
   ```
   - No `--windowed` → keeps the console window for interactive I/O.
   - Entrypoint: `yfix.py` → runs the CLI menu directly.

Both use `--hidden-import=psutil` because PyInstaller's static analysis may miss the runtime import.

---

## Data Flow Diagrams

### CLI Mode
```
User input → menu() → feature function → print() → console output
                                │
                        ┌───────┴───────┐
                        ▼               ▼
                  run_cmd()        psutil API
                        │               │
                        ▼               ▼
                  subprocess.run()  system calls
```

### GUI Mode
```
Button click → run_option(n) → set_busy() + update_idletasks()
                     │
            ┌────────┴────────┐
            ▼                 ▼
       short task          long task
       run_sync()          run_in_thread()
            │                 │
            ▼                 ▼
      redirect_stdout()   threading.Thread()
            │                 │
            ▼                 ▼
       TextRedirector     redirect_stdout()
            │                 │
            ▼                 ▼
     ScrolledText.insert()  root.after(0, set_idle)
```

### Monkey-Patching Flow
```
yfix.py:             input()          prompt_yesno()
                       ▲                  ▲
                       │  monkey-patch   │
yfix_gui.py:     gui_input() ───── gui_prompt_yesno()
                   │                      │
                   ▼                      ▼
           simpledialog.askstring   messagebox.askyesno
```

---

## Dependency Graph

```
yfix.py ──── psutil ──── psutil.sensors_temperatures()
                      ├── psutil.cpu_count()
                      ├── psutil.cpu_percent()
                      ├── psutil.virtual_memory()
                      ├── psutil.swap_memory()
                      ├── psutil.disk_usage()
                      ├── psutil.disk_partitions()
                      ├── psutil.net_connections()
                      ├── psutil.net_io_counters()
                      ├── psutil.process_iter()
                      ├── psutil.boot_time()
                      └── psutil.Process()
         │
         ├── subprocess ──── run_cmd() [all WMIC, PowerShell, system commands]
         ├── ctypes ──── is_admin()
         ├── socket ──── network_diag()
         ├── platform ──── show_sysinfo()
         └── datetime / pathlib / os / shutil / json / time

yfix_gui.py ──── tkinter ──── ttk, scrolledtext, messagebox, simpledialog
              ├── threading
              ├── io.StringIO
              └── contextlib.redirect_stdout
```

---

## Admin Requirements by Function

| Function | Admin Required |
|----------|:--------------:|
| `is_admin()` | No |
| `run_cmd()` | Depends on command |
| `require_admin()` | No |
| Utilities (section/warn/ok/info) | No |
| `show_help()` | No |
| `show_sysinfo()` | No |
| `get_disk_type()` | No |
| `create_restore_point()` | Yes |
| `list_restore_points()` | Yes |
| `restore_from_point()` | Yes |
| `storage_sense()` | Yes |
| `clean_temp()` | Yes |
| `show_startup()` | No |
| `background_apps_control()` | Yes |
| `show_bloatware()` | Yes |
| `check_suspicious_processes()` | No |
| `malware_scan()` | Yes |
| `check_old_drivers()` | No |
| `driver_check()` | No |
| `disk_optimizer()` | Yes |
| `disk_health()` | No |
| `memory_diag()` | Yes |
| `battery_report()` | No |
| `visual_effects_tuner()` | Yes |
| `privacy_tweaks()` | Yes |
| `power_optimizer()` | Yes |
| `power_report()` | Yes |
| `network_diag()` | No |
| `flush_dns()` | Yes |
| `sfc_scan()` | Yes |
| `dism_restore()` | Yes |
| `winupdate_status()` | No |
| `get_browser_cache_size()` | No |
| `clean_browser_cache()` | No |
| `browser_cleanup()` | No |
| `chkdsk()` | Yes |
| `perf_monitor()` | No |
| `common_checks()` | No |
| `repair_install()` | No |
| `why_slow()` | No |
| `run_all()` | Yes (most steps) |
| `show_about()` | No |
| `menu()` | No |
| `check_deps()` | No |
