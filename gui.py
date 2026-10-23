# gui.py
# Phase 3 GUI: Modern look, Preview, Progress, Organize, and Undo.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

from organizer import scan_folder, organize_files
from history import undo_last_operation

# --- Color Palette ---
BG_COLOR = "#F3F4F6"        # Light gray background
CARD_COLOR = "#FFFFFF"      # White panels
TEXT_COLOR = "#1F2937"      # Dark gray text
PRIMARY_COLOR = "#2563EB"   # Blue button
PRIMARY_HOVER = "#1D4ED8"

class OrganizerApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.master.title("File Organizer Pro")
        self.master.geometry("820x680")
        self.master.configure(bg=BG_COLOR)
        
        self.pack(fill="both", expand=True, padx=20, pady=20)

        # Variables
        self.source_dir = tk.StringVar()
        self.include_subfolders = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Select a folder to begin.")
        self.last_scan_result = None

        self._setup_styles()
        self._build_widgets()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_COLOR, relief="flat")
        
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Card.TLabel", background=CARD_COLOR)
        
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        
        # Custom Primary Button
        style.configure("Primary.TButton", foreground="white", background=PRIMARY_COLOR, font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", background=[("active", PRIMARY_HOVER)])
        
        # Treeview styling
        style.configure("Treeview", background=CARD_COLOR, foreground=TEXT_COLOR, rowheight=28, fieldbackground=CARD_COLOR, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E5E7EB", foreground=TEXT_COLOR, padding=4)
        style.map("Treeview", background=[("selected", PRIMARY_COLOR)], foreground=[("selected", "white")])
        
        style.configure("TProgressbar", thickness=8, background=PRIMARY_COLOR)

    def _build_widgets(self):
        # 1. Header
        header = ttk.Label(self, text="📁 File Organizer", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 15))

        # 2. Source Selection Panel
        src_frame = ttk.Frame(self, style="Card.TFrame", padding=15)
        src_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(src_frame, text="Source Folder:", style="Card.TLabel").pack(anchor="w")
        
        row1 = ttk.Frame(src_frame, style="Card.TFrame")
        row1.pack(fill="x", pady=(5, 0))
        
        self.entry_src = ttk.Entry(row1, textvariable=self.source_dir, font=("Segoe UI", 10))
        self.entry_src.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ttk.Button(row1, text="Browse", command=self.browse_folder).pack(side="left")

        # Options Row
        row2 = ttk.Frame(src_frame, style="Card.TFrame")
        row2.pack(fill="x", pady=(10, 0))
        ttk.Checkbutton(row2, text="Include Subfolders", variable=self.include_subfolders).pack(side="left")
        
        ttk.Button(row2, text="🔍 Preview Files", command=self.do_scan).pack(side="right")

        # 3. Preview Table
        table_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        columns = ("filename", "category", "destination")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("filename", text="File Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("destination", text="Proposed Destination")
        
        self.tree.column("filename", width=250, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("destination", width=300, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 4. Bottom Action Area
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x")
        
        self.progress = ttk.Progressbar(bottom_frame, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))
        
        action_row = ttk.Frame(bottom_frame)
        action_row.pack(fill="x")
        
        ttk.Label(action_row, textvariable=self.status).pack(side="left")
        
        # Organize button (starts disabled)
        self.btn_organize = ttk.Button(action_row, text="✨ Organize Files", style="Primary.TButton", command=self.do_organize, state="disabled")
        self.btn_organize.pack(side="right", padx=(10, 0))
        
        # Undo button (starts disabled)
        self.btn_undo = ttk.Button(action_row, text="↩️ Undo Last", command=self.do_undo, state="disabled")
        self.btn_undo.pack(side="right")

    # ---------- Actions ----------
    def browse_folder(self):
        chosen = filedialog.askdirectory(title="Select source folder")
        if chosen:
            self.source_dir.set(chosen)
            self.tree.delete(*self.tree.get_children())
            self.btn_organize.config(state="disabled")
            self.status.set("Folder selected. Click 'Preview Files' to scan.")

    def do_scan(self):
        folder = self.source_dir.get().strip()
        if not folder or not Path(folder).is_dir():
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        self.status.set("Scanning…")
        self.progress["value"] = 0
        self.btn_organize.config(state="disabled")
        self.update_idletasks()

        result = scan_folder(folder, include_subfolders=self.include_subfolders.get())
        self.last_scan_result = result
        
        self.tree.delete(*self.tree.get_children())
        for path, category in result.files:
            dest = str(Path(folder) / category / path.name)
            self.tree.insert("", "end", values=(path.name, category, dest))

        total = len(result.files)
        if total > 0:
            self.status.set(f"Found {total} files. Ready to organize.")
            self.btn_organize.config(state="normal")
        else:
            self.status.set("No files found to organize.")

    def do_organize(self):
        if not self.last_scan_result or not self.last_scan_result.files:
            return

        folder = self.source_dir.get().strip()
        confirm = messagebox.askyesno(
            "Confirm Move", 
            f"Are you sure you want to organize {len(self.last_scan_result.files)} files?\n\nThis will move files into folders inside {folder}."
        )
        if not confirm:
            return

        self.btn_organize.config(state="disabled")
        self.btn_undo.config(state="disabled") # Disable undo while organizing
        self.status.set("Organizing files, please wait…")
        self.progress["maximum"] = len(self.last_scan_result.files)
        
        def worker():
            summary = organize_files(
                self.last_scan_result, 
                folder, 
                progress_callback=self.update_progress
            )
            self.after(0, lambda: self.on_organize_done(summary))

        threading.Thread(target=worker, daemon=True).start()

    def update_progress(self, current, total):
        self.after(0, lambda: self.progress.configure(value=current))

    def on_organize_done(self, summary):
        self.progress["value"] = 0
        self.tree.delete(*self.tree.get_children())
        
        moved = summary["moved"]
        errors = len(summary["errors"])
        
        if errors == 0:
            self.status.set(f"Success! Organized {moved} files.")
            messagebox.showinfo("Success", f"Successfully moved {moved} files.")
        else:
            self.status.set(f"Done. Moved {moved}, Errors: {errors}.")
            messagebox.showwarning("Finished with errors", f"Moved {moved} files.\nFailed to move {errors} files.")
            
        # Enable Undo button now that we have history
        self.btn_undo.config(state="normal")

    def do_undo(self):
        confirm = messagebox.askyesno(
            "Confirm Undo", 
            "Are you sure you want to undo the last organize operation?\n\nThis will move files back to their original locations."
        )
        if not confirm:
            return
            
        self.status.set("Undoing last operation...")
        self.update_idletasks()
        
        result = undo_last_operation()
        
        if not result["success"]:
            self.status.set("Undo failed.")
            messagebox.showerror("Undo Failed", result["message"])
            return
            
        restored = result["restored"]
        errors = len(result["errors"])
        
        if errors == 0:
            self.status.set(f"Successfully restored {restored} files.")
            messagebox.showinfo("Undo Complete", f"Moved {restored} files back to their original locations.")
        else:
            self.status.set(f"Restored {restored} files, failed to restore {errors}.")
            error_msg = "\n".join([f"{path}: {msg}" for path, msg in result["errors"][:5]])
            messagebox.showwarning(
                "Undo Finished with Errors", 
                f"Restored {restored} files.\nCould not restore {errors} files:\n\n{error_msg}\n\n(Check the console for full details)"
            )
        
        self.tree.delete(*self.tree.get_children())
        self.btn_undo.config(state="disabled") # Disable undo again

def main():
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    OrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()