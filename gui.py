import tkinter as tk
from tkinter import filedialog, ttk
import threading
import os
from PIL import Image, ImageTk
from multiprocessing import Process, Queue

# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────
NUM_PROCESSES = 8
BG        = "#0d0f14"
PANEL     = "#14171f"
CARD      = "#1a1e28"
ACCENT    = "#4f8aff"
ACCENT2   = "#a259ff"
TEXT      = "#e8eaf0"
SUBTEXT   = "#6b7280"
SUCCESS   = "#22d3a5"
ERROR     = "#ff5f6d"
BORDER    = "#262b38"
FONT_MONO = ("Courier New", 9)
FONT_UI   = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI Semibold", 11)

# ─────────────────────────────────────────────
#  Worker
# ─────────────────────────────────────────────
def process_to_gray(files, process_num, output_folder, queue):
    for file in files:
        try:
            img = Image.open(file).convert("L")
            out = os.path.join(output_folder, "gray_" + os.path.basename(file))
            img.save(out)
            queue.put(("done", process_num, file, out))
        except Exception as e:
            queue.put(("error", process_num, file, str(e)))

# ─────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────
class ImageProcessorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grayscale Processor")
        self.configure(bg=BG)
        self.geometry("960x680")
        self.minsize(820, 560)
        self.resizable(True, True)

        self.input_folder  = tk.StringVar(value="")
        self.output_folder = tk.StringVar(value="")
        self.status_var    = tk.StringVar(value="Ready")
        self.total         = 0
        self.done_count    = 0
        self._queue        = Queue()
        self._sample_paths = []       # output paths for preview strip
        self._preview_imgs = []       # keep refs to avoid GC
        self._running      = False

        self._build_ui()

    # ── UI ────────────────────────────────────
    def _build_ui(self):
        # ── Sidebar
        sidebar = tk.Frame(self, bg=PANEL, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="⬡ GRAYSHIFT", bg=PANEL, fg=ACCENT,
                 font=("Courier New", 13, "bold")).pack(pady=(28, 4), padx=20, anchor="w")
        tk.Label(sidebar, text="Batch Image Processor", bg=PANEL, fg=SUBTEXT,
                 font=FONT_UI).pack(padx=20, anchor="w")

        self._sep(sidebar)

        # Input folder
        tk.Label(sidebar, text="INPUT FOLDER", bg=PANEL, fg=SUBTEXT,
                 font=("Courier New", 8)).pack(padx=20, anchor="w", pady=(12, 3))

        row = tk.Frame(sidebar, bg=PANEL)
        row.pack(fill="x", padx=20, pady=(0, 4))
        self._entry_in = tk.Entry(row, textvariable=self.input_folder,
                                  bg=CARD, fg=TEXT, insertbackground=TEXT,
                                  relief="flat", bd=0, font=FONT_MONO)
        self._entry_in.pack(side="left", fill="x", expand=True,
                            ipady=7, ipadx=6)
        tk.Button(row, text="…", command=self._browse_input,
                  bg=ACCENT, fg="white", relief="flat", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  activebackground=ACCENT2, activeforeground="white",
                  cursor="hand2", padx=8).pack(side="left", ipady=4)

        # Output folder
        tk.Label(sidebar, text="OUTPUT FOLDER", bg=PANEL, fg=SUBTEXT,
                 font=("Courier New", 8)).pack(padx=20, anchor="w", pady=(10, 3))

        row2 = tk.Frame(sidebar, bg=PANEL)
        row2.pack(fill="x", padx=20, pady=(0, 4))
        self._entry_out = tk.Entry(row2, textvariable=self.output_folder,
                                   bg=CARD, fg=TEXT, insertbackground=TEXT,
                                   relief="flat", bd=0, font=FONT_MONO)
        self._entry_out.pack(side="left", fill="x", expand=True,
                             ipady=7, ipadx=6)
        tk.Button(row2, text="…", command=self._browse_output,
                  bg=BORDER, fg=TEXT, relief="flat", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  activebackground=ACCENT, activeforeground="white",
                  cursor="hand2", padx=8).pack(side="left", ipady=4)

        self._sep(sidebar)

        # Process count
        tk.Label(sidebar, text="PROCESSES", bg=PANEL, fg=SUBTEXT,
                 font=("Courier New", 8)).pack(padx=20, anchor="w", pady=(10, 3))
        self._proc_var = tk.IntVar(value=NUM_PROCESSES)
        proc_frame = tk.Frame(sidebar, bg=PANEL)
        proc_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Scale(proc_frame, from_=1, to=32, orient="horizontal",
                 variable=self._proc_var, bg=PANEL, fg=TEXT,
                 troughcolor=CARD, highlightthickness=0,
                 activebackground=ACCENT, sliderrelief="flat").pack(fill="x")
        tk.Label(proc_frame, textvariable=self._proc_var, bg=PANEL,
                 fg=ACCENT, font=("Courier New", 11, "bold")).pack(anchor="e")

        self._sep(sidebar)

        # Run button
        self._run_btn = tk.Button(sidebar, text="▶  PROCESS IMAGES",
                                  command=self._start_processing,
                                  bg=ACCENT, fg="white", relief="flat", bd=0,
                                  font=("Segoe UI Semibold", 11),
                                  activebackground=ACCENT2,
                                  activeforeground="white",
                                  cursor="hand2", pady=12)
        self._run_btn.pack(fill="x", padx=20, pady=8)

        # Stats
        self._stats_lbl = tk.Label(sidebar, text="", bg=PANEL, fg=SUBTEXT,
                                   font=FONT_MONO, justify="left")
        self._stats_lbl.pack(padx=20, anchor="w")

        # Status bottom
        tk.Label(sidebar, textvariable=self.status_var, bg=PANEL, fg=SUCCESS,
                 font=("Courier New", 9), wraplength=220,
                 justify="left").pack(side="bottom", padx=20, pady=16, anchor="w")

        # ── Main area
        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        # Progress bar area
        top_bar = tk.Frame(main, bg=CARD, height=60)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        tk.Label(top_bar, text="Progress", bg=CARD, fg=SUBTEXT,
                 font=FONT_UI).pack(side="left", padx=16, pady=18)
        self._pct_lbl = tk.Label(top_bar, text="0%", bg=CARD, fg=ACCENT,
                                  font=("Courier New", 12, "bold"))
        self._pct_lbl.pack(side="right", padx=16)

        prog_wrap = tk.Frame(main, bg=BG, height=6)
        prog_wrap.pack(fill="x")
        self._prog = ttk.Progressbar(prog_wrap, orient="horizontal",
                                     mode="determinate", maximum=100)
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TProgressbar", troughcolor=CARD, background=ACCENT,
                     bordercolor=BG, lightcolor=ACCENT, darkcolor=ACCENT,
                     thickness=6)
        self._prog.pack(fill="x")

        # Preview strip label
        tk.Label(main, text="OUTPUT PREVIEW", bg=BG, fg=SUBTEXT,
                 font=("Courier New", 8)).pack(anchor="w", padx=18, pady=(18, 6))

        # Preview strip
        strip_outer = tk.Frame(main, bg=CARD, bd=0,
                                highlightbackground=BORDER,
                                highlightthickness=1)
        strip_outer.pack(fill="x", padx=18)
        self._strip = tk.Frame(strip_outer, bg=CARD)
        self._strip.pack(fill="x", pady=10, padx=10)

        tk.Label(self._strip, text="Processed images will appear here…",
                 bg=CARD, fg=SUBTEXT, font=FONT_UI).pack(pady=30)

        # Log
        tk.Label(main, text="LOG", bg=BG, fg=SUBTEXT,
                 font=("Courier New", 8)).pack(anchor="w", padx=18, pady=(16, 4))

        log_frame = tk.Frame(main, bg=CARD, highlightbackground=BORDER,
                             highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self._log = tk.Text(log_frame, bg=CARD, fg=TEXT,
                            font=FONT_MONO, relief="flat", bd=0,
                            state="disabled", wrap="none",
                            insertbackground=TEXT)
        scroll = tk.Scrollbar(log_frame, command=self._log.yview,
                              bg=CARD, troughcolor=CARD, relief="flat")
        self._log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._log.pack(fill="both", expand=True, padx=8, pady=8)

        # colour tags
        self._log.tag_config("ok",    foreground=SUCCESS)
        self._log.tag_config("err",   foreground=ERROR)
        self._log.tag_config("info",  foreground=ACCENT)
        self._log.tag_config("proc",  foreground=SUBTEXT)

    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

    # ── Folder browsers ───────────────────────
    def _browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
            # Auto-set output next to input
            if not self.output_folder.get():
                self.output_folder.set(os.path.join(folder, "output_gray"))
            self._scan_folder(folder)

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    def _scan_folder(self, folder):
        files = [f for f in os.listdir(folder)
                 if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        count = len(files)
        self._log_write(f"📂  Folder: {folder}\n", "info")
        self._log_write(f"    Found {count} image(s)\n", "proc")
        self._stats_lbl.config(text=f"{count} images found")
        self.status_var.set(f"{count} images ready")

    # ── Processing ────────────────────────────
    def _start_processing(self):
        if self._running:
            return
        inp  = self.input_folder.get().strip()
        outp = self.output_folder.get().strip()
        if not inp or not os.path.isdir(inp):
            self.status_var.set("⚠ Choose a valid input folder first.")
            return
        if not outp:
            self.status_var.set("⚠ Choose an output folder first.")
            return

        os.makedirs(outp, exist_ok=True)
        files = [os.path.join(inp, f) for f in os.listdir(inp)
                 if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not files:
            self.status_var.set("No images found in folder.")
            return

        self.total      = len(files)
        self.done_count = 0
        self._sample_paths.clear()
        self._running   = True
        self._run_btn.config(state="disabled", text="⏳  Processing…")
        self._prog["value"] = 0
        self._pct_lbl.config(text="0%")
        self._clear_strip()
        self._log_write(f"\n▶  Starting {self.total} images across "
                        f"{self._proc_var.get()} processes…\n", "info")

        threading.Thread(target=self._run_workers,
                         args=(files, outp), daemon=True).start()
        self._poll_queue()

    def _run_workers(self, files, outp):
        n     = self._proc_var.get()
        chunk = len(files) // n + 1
        procs = []
        for i in range(n):
            chunk_files = files[i*chunk:(i+1)*chunk]
            if not chunk_files:
                continue
            p = Process(target=process_to_gray,
                        args=(chunk_files, i, outp, self._queue))
            procs.append(p)
            p.start()
        for p in procs:
            p.join()
        self._queue.put(("finished", None, None, None))

    def _poll_queue(self):
        try:
            while True:
                msg = self._queue.get_nowait()
                kind, proc_num, file, extra = msg
                if kind == "done":
                    self.done_count += 1
                    pct = int(self.done_count / self.total * 100)
                    self._prog["value"] = pct
                    self._pct_lbl.config(text=f"{pct}%")
                    self._stats_lbl.config(
                        text=f"{self.done_count}/{self.total} done")
                    self._log_write(
                        f"[P{proc_num:02d}] ✓ {os.path.basename(file)}\n",
                        "ok")
                    # collect first 6 for preview
                    if len(self._sample_paths) < 6:
                        self._sample_paths.append(extra)
                        self._refresh_strip()
                elif kind == "error":
                    self._log_write(
                        f"[P{proc_num:02d}] ✗ {os.path.basename(file)}"
                        f" — {extra}\n", "err")
                elif kind == "finished":
                    self._on_finished()
                    return
        except Exception:
            pass
        self.after(80, self._poll_queue)

    def _on_finished(self):
        self._running = False
        self._run_btn.config(state="normal", text="▶  PROCESS IMAGES")
        self._prog["value"] = 100
        self._pct_lbl.config(text="100%")
        self.status_var.set(
            f"✓ Done — {self.done_count}/{self.total} processed")
        self._log_write(
            f"\n✅  All done! {self.done_count} images saved to:\n"
            f"    {self.output_folder.get()}\n", "info")

    # ── Preview strip ─────────────────────────
    def _clear_strip(self):
        for w in self._strip.winfo_children():
            w.destroy()
        self._preview_imgs.clear()

    def _refresh_strip(self):
        self._clear_strip()
        for path in self._sample_paths:
            try:
                img = Image.open(path).convert("L")
                img.thumbnail((120, 90))
                photo = ImageTk.PhotoImage(img)
                self._preview_imgs.append(photo)

                cell = tk.Frame(self._strip, bg=CARD)
                cell.pack(side="left", padx=6, pady=4)

                tk.Label(cell, image=photo, bg=CARD,
                         highlightbackground=ACCENT,
                         highlightthickness=1).pack()
                tk.Label(cell, text=os.path.basename(path)[:16],
                         bg=CARD, fg=SUBTEXT,
                         font=("Courier New", 7)).pack(pady=(3, 0))
            except Exception:
                pass

    # ── Log helper ────────────────────────────
    def _log_write(self, text, tag="proc"):
        self._log.config(state="normal")
        self._log.insert("end", text, tag)
        self._log.see("end")
        self._log.config(state="disabled")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = ImageProcessorApp()
    app.mainloop()