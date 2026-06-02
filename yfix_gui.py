#!/usr/bin/env python3
"""
yfix_gui.py - Tkinter GUI wrapper for Yfix
Run as Administrator for full functionality.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from io import StringIO
from contextlib import redirect_stdout

import yfix


# ── Redirect stdout to ScrolledText ─────────────────────────────────────


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)

    def flush(self):
        pass


# ── Override input() for GUI mode ───────────────────────────────────────


def gui_input(prompt_text=""):
    return simpledialog.askstring("Input Required", prompt_text) or ""


def gui_prompt_yesno(question):
    return messagebox.askyesno("Confirm", question)


# ── Main Application ────────────────────────────────────────────────────


class R2FixGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Yfix v{yfix.VERSION} by yohi - Windows PC Fix & Speedup Tool")
        self.root.geometry("860x680")

        # Override input functions in yfix module
        yfix.input = gui_input
        yfix.prompt_yesno = gui_prompt_yesno

        self.running = False
        self.build_ui()
        self.update_status()

    def build_ui(self):
        # ── Top frame: title + status ──
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(top, text=f"Yfix v{yfix.VERSION}", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

        self.admin_label = tk.Label(top, text="", font=("Segoe UI", 10))
        self.admin_label.pack(side=tk.RIGHT, padx=4)

        # ── Admin warning banner (packed only when not admin) ──
        self.admin_banner = tk.Label(
            self.root, text="  Run as Administrator for full functionality",
            bg="#fff3cd", fg="#856404", font=("Segoe UI", 10, "bold"),
            anchor=tk.W, padx=8, pady=4
        )
        if not yfix.is_admin():
            self.admin_banner.pack(fill=tk.X, padx=8, pady=(0, 2))

        # ── Button frame ──
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=8, pady=2)

        buttons = [
            ("Sys Info", 1), ("Why Slow", 2), ("Restore Pt", 3), ("Malware", 4),
            ("Clean Temp", 5), ("Storage Sense", 6), ("Startup", 7), ("Bkg Apps", 8),
            ("Bloatware", 9), ("Drivers", 10), ("Disk Opt", 11), ("Mem Diag", 12),
            ("Battery", 13), ("Visual FX", 14), ("Privacy", 15), ("Power Plan", 16),
            ("Network", 17), ("SFC", 18), ("DISM", 19), ("Win Update", 20),
            ("Browser", 21), ("Flush DNS", 22), ("Repair Install", 23),
            ("Run ALL", 24), ("Help", 25),
            ("Restore List", 26), ("Restore Now", 27), ("About", 28),
        ]

        self.buttons = []
        row, col = 0, 0
        max_cols = 5
        for text, opt_num in buttons:
            btn = tk.Button(
                btn_frame, text=text, width=14, height=1,
                command=lambda n=opt_num: self.run_option(n)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # ── Progress bar (hidden by default) ──
        self.progress_frame = tk.Frame(self.root)
        self.progress_label = tk.Label(self.progress_frame, text="", font=("Segoe UI", 9))
        self.progress_label.pack(side=tk.LEFT, padx=2)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=2)

        # ── Output text area ──
        self.output = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white"
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # ── Bottom frame: buttons ──
        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=8, pady=4)

        self.clear_btn = tk.Button(bottom, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        tk.Button(bottom, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=2)

        # Redirect stdout
        self.redirector = TextRedirector(self.output)

    def update_status(self):
        admin = yfix.is_admin()
        self.admin_label.config(text=f"Admin: {'YES' if admin else 'NO (limited)'}")
        if admin:
            self.admin_banner.pack_forget()
        else:
            self.admin_banner.pack(fill=tk.X, padx=8, pady=(0, 2))
        self.root.after(5000, self.update_status)

    def clear_output(self):
        self.output.delete(1.0, tk.END)

    def set_busy(self, label):
        self.running = True
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.progress_label.config(text=f"Running: {label}...")
        self.progress_bar.start(10)
        self.progress_frame.pack(fill=tk.X, padx=8, pady=(0, 2))

    def set_idle(self):
        if not self.running:
            return
        self.running = False
        for btn in self.buttons:
            btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.progress_frame.pack_forget()

    def run_option(self, option_num):
        if self.running:
            return

        items = [
            ("System Information",              yfix.show_sysinfo),
            ("Why Is My PC Slow? (Diagnostic)", yfix.why_slow),
            ("Create System Restore Point",     yfix.create_restore_point),
            ("Malware & Virus Scan",            yfix.malware_scan),
            ("Clean Temporary Files",           yfix.show_clean_temp),
            ("Storage Sense (Auto Cleanup)",    yfix.storage_sense),
            ("Startup Programs Manager",        yfix.show_startup),
            ("Background Apps Control",         yfix.background_apps_control),
            ("Unnecessary Apps & Bloatware",    yfix.show_bloatware),
            ("Driver Health Check",             yfix.driver_check),
            ("Disk Optimizer (Defrag/TRIM)",    yfix.disk_optimizer),
            ("Windows Memory Diagnostic",       yfix.memory_diag),
            ("Battery Health Report",           yfix.battery_report),
            ("Visual Effects Tuner",            yfix.visual_effects_tuner),
            ("Windows Privacy Tweaks",          yfix.privacy_tweaks),
            ("Power Plan Optimizer",            yfix.power_optimizer),
            ("Network Diagnostics",             yfix.network_diag),
            ("System File Checker (SFC)",       yfix.sfc_scan),
            ("DISM Health Restore",             yfix.dism_restore),
            ("Windows Update Status",           yfix.winupdate_status),
            ("Browser Cleanup",                 yfix.browser_cleanup),
            ("Flush DNS & Reset Network Stack", yfix.flush_dns),
            ("Repair Install (In-place Upgrade)", yfix.repair_install),
            ("Run ALL Automated Fixes",         yfix.run_all),
            ("Help & Manual",                   yfix.show_help),
            ("View Restore Points",             yfix.list_restore_points),
            ("Restore from Point",              yfix.restore_from_point),
            ("About",                           yfix.show_about),
        ]

        if option_num < 1 or option_num > len(items):
            return

        label, func = items[option_num - 1]

        # Long-running tasks that need threading
        long_tasks = {
            "System File Checker (SFC)",
            "DISM Health Restore",
            "Malware & Virus Scan",
            "Run ALL Automated Fixes",
            "Disk Optimizer (Defrag/TRIM)",
            "Clean Temporary Files",
        }

        self.set_busy(label)
        self.root.update_idletasks()

        if label in long_tasks:
            self.run_in_thread(func, label)
        else:
            self.run_sync(func, label)

    def run_sync(self, func, label):
        try:
            with redirect_stdout(self.redirector):
                func()
                print(f"\nOK: {label} finished successfully.\n")
        except Exception as e:
            with redirect_stdout(self.redirector):
                print(f"\nFAIL: {label} failed - {e}\n")
        finally:
            self.set_idle()

    def run_in_thread(self, func, label):
        def target():
            try:
                with redirect_stdout(self.redirector):
                    func()
                    print(f"\nOK: {label} finished successfully.\n")
            except Exception as e:
                with redirect_stdout(self.redirector):
                    print(f"\nFAIL: {label} failed - {e}\n")
            finally:
                self.root.after(0, self.set_idle)

        t = threading.Thread(target=target, daemon=True)
        t.start()


# ── Entrypoint ──────────────────────────────────────────────────────────


def main():
    yfix.check_deps()
    yfix.run_as_admin()
    yfix.require_admin()

    root = tk.Tk()
    app = R2FixGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
