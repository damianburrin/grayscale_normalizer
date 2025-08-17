import math
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Optional

try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit("Pillow is required. Install it with: pip install pillow")


# ------------------------------
# Utility functions
# ------------------------------

def to_grayscale(img: Image.Image) -> Image.Image:
    """Ensure an image is 8-bit grayscale (mode 'L')."""
    if img.mode != "L":
        return img.convert("L")
    return img


def compute_histogram(img: Image.Image) -> List[int]:
    """Return a 256-bin histogram for an 8-bit grayscale image."""
    if img.mode != "L":
        img = to_grayscale(img)
    hist = img.histogram(mask=None)  # length 256 list
    return hist[:256]


def compute_stats(img: Image.Image, filename: Optional[str] = None) -> dict:
    """Compute brightness distribution statistics for an 8-bit grayscale image."""
    img = to_grayscale(img)
    width, height = img.size
    n = width * height

    min_val, max_val = img.getextrema()  # tuple
    hist = compute_histogram(img)

    # Mean and std from histogram
    total = sum(i * c for i, c in enumerate(hist))
    mean = total / n if n else 0.0

    total_sq = sum((i * i) * c for i, c in enumerate(hist))
    variance = (total_sq / n) - (mean * mean) if n else 0.0
    stddev = math.sqrt(max(0.0, variance))

    # Entropy (Shannon, bits/pixel)
    entropy = 0.0
    for c in hist:
        if c > 0:
            p = c / n
            entropy -= p * math.log2(p)

    # Dynamic range and utilized spread
    used_bins = [i for i, c in enumerate(hist) if c > 0]
    if used_bins:
        utilized_range = (used_bins[-1] - used_bins[0])
        bins_used_pct = (len(used_bins) / 256.0) * 100.0
    else:
        utilized_range = 0
        bins_used_pct = 0.0

    return {
        "filename": filename or "(unsaved image)",
        "width": width,
        "height": height,
        "pixels": n,
        "min": int(min_val),
        "max": int(max_val),
        "mean": mean,
        "stddev": stddev,
        "dynamic_range": int(max_val - min_val),
        "utilized_range": int(utilized_range),
        "bins_used_pct": bins_used_pct,
        "entropy": entropy,
        "hist": hist,
    }


def normalize_with_levels(img: Image.Image, black: int, white: int, gamma: float) -> Image.Image:
    """Levels + gamma: map [black, white] -> [0, 255], then apply gamma (out = x**(1/gamma))."""
    img = to_grayscale(img)
    black = max(0, min(255, int(black)))
    white = max(0, min(255, int(white)))
    if white <= black:
        white = min(255, black + 1)

    rng = white - black
    inv_gamma = 1.0 / max(1e-6, float(gamma))

    lut = []
    for i in range(256):
        if i <= black:
            lut.append(0)
        elif i >= white:
            lut.append(255)
        else:
            x = (i - black) / rng  # 0..1
            x = x ** inv_gamma if gamma != 1.0 else x
            v = int(round(x * 255.0))
            lut.append(0 if v < 0 else (255 if v > 255 else v))
    return img.point(lut, mode="L")


def pil_to_tk(img: Image.Image, max_dim: int = 480) -> ImageTk.PhotoImage:
    """Convert a PIL image to a Tk PhotoImage, resizing to fit (preserve aspect)."""
    img = to_grayscale(img)
    w, h = img.size
    scale = min(max_dim / max(w, h), 1.0)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# ------------------------------
# UI Components
# ------------------------------

class HistogramView(tk.Canvas):
    def __init__(self, master, width=256, height=120, **kwargs):
        super().__init__(master, width=width, height=height, bg="#ffffff", highlightthickness=1, highlightbackground="#dddddd", **kwargs)
        self.width = width
        self.height = height

    def draw(self, hist: Optional[List[int]]):
        self.delete("all")
        if not hist:
            self.create_rectangle(0, 0, self.width-1, self.height-1, outline="#dddddd")
            return
        max_count = max(hist) if hist else 1
        if max_count == 0:
            max_count = 1
        w = self.width
        h = self.height
        self.create_rectangle(0, 0, w-1, h-1, outline="#dddddd")
        for x in range(256):
            v = hist[x]
            bar_h = int((v / max_count) * (h - 2))
            self.create_line(x, h-1, x, h-1 - bar_h, fill="#333333")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grayscale Normalizer")
        self.geometry("1180x760")
        self.minsize(980, 680)

        # State
        self.input_img: Optional[Image.Image] = None
        self.output_img: Optional[Image.Image] = None
        self.input_stats: Optional[dict] = None
        self.output_stats: Optional[dict] = None
        self.input_path: Optional[str] = None

        # Layout
        self._build_menu()
        self._build_toolbar()
        self._build_controls()
        self._build_body()

    # ---- UI builders ----
    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Image…", command=self.on_open)
        file_menu.add_command(label="Save Output As…", command=self.on_save_as, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        action_menu = tk.Menu(menubar, tearoff=0)
        # Analyze removed; now automatic on open
        action_menu.add_command(label="Normalize", command=self.on_normalize, state=tk.DISABLED)
        menubar.add_cascade(label="Actions", menu=action_menu)

        self.config(menu=menubar)
        self._file_menu = file_menu
        self._action_menu = action_menu

    def _build_toolbar(self):
        bar = tk.Frame(self, bd=0, relief=tk.FLAT)
        bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)
        tk.Button(bar, text="Open Image…", command=self.on_open).pack(side=tk.LEFT)
        self.btn_normalize = tk.Button(bar, text="Normalize", command=self.on_normalize, state=tk.DISABLED)
        self.btn_normalize.pack(side=tk.LEFT, padx=(8,0))
        self.btn_save = tk.Button(bar, text="Save Output As…", command=self.on_save_as, state=tk.DISABLED)
        self.btn_save.pack(side=tk.LEFT, padx=(8,0))

    def _build_controls(self):
        controls = tk.LabelFrame(self, text="Levels & Gamma")
        controls.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0,8))

        row = tk.Frame(controls)
        row.pack(fill=tk.X, padx=8, pady=6)

        # Black level
        tk.Label(row, text="Black:").pack(side=tk.LEFT)
        self.var_black = tk.IntVar(value=0)
        self.slider_black = tk.Scale(row, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.var_black, command=self._on_slider_change)
        self.slider_black.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,14))

        # White level
        tk.Label(row, text="White:").pack(side=tk.LEFT)
        self.var_white = tk.IntVar(value=255)
        self.slider_white = tk.Scale(row, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.var_white, command=self._on_slider_change)
        self.slider_white.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,14))

        # Gamma
        tk.Label(row, text="Gamma:").pack(side=tk.LEFT)
        self.var_gamma = tk.DoubleVar(value=1.0)
        self.slider_gamma = tk.Scale(row, from_=0.10, to=4.00, resolution=0.01, orient=tk.HORIZONTAL, variable=self.var_gamma, command=self._on_slider_change)
        self.slider_gamma.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6,0))

    def _build_body(self):
        body = tk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Left: Input
        left = tk.LabelFrame(body, text="Input Image")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        self.input_preview = tk.Label(left, bg="#f8f8f8", relief=tk.SOLID, bd=1)
        self.input_preview.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.input_hist = HistogramView(left)
        self.input_hist.pack(fill=tk.X, padx=8, pady=(0,8))

        self.input_stats_text = tk.Text(left, height=8, wrap=tk.WORD)
        self.input_stats_text.configure(state=tk.DISABLED)
        self.input_stats_text.pack(fill=tk.X, padx=8, pady=(0,8))

        # Right: Output
        right = tk.LabelFrame(body, text="Output Image (Levels/Gamma Applied)")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0))

        self.output_preview = tk.Label(right, bg="#f8f8f8", relief=tk.SOLID, bd=1)
        self.output_preview.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.output_hist = HistogramView(right)
        self.output_hist.pack(fill=tk.X, padx=8, pady=(0,8))

        self.output_stats_text = tk.Text(right, height=8, wrap=tk.WORD)
        self.output_stats_text.configure(state=tk.DISABLED)
        self.output_stats_text.pack(fill=tk.X, padx=8, pady=(0,8))

        # Bottom: Change metrics
        bottom = tk.LabelFrame(self, text="Change Metrics (Input → Output)")
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0,10))

        self.metrics_label = tk.Label(bottom, text="Open an image to see analysis (auto).")
        self.metrics_label.pack(anchor="w", padx=8, pady=8)

    # ---- Actions ----
    def on_open(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror("Open Image", f"Failed to open image:\n{e}")
            return

        self.input_path = path
        self.input_img = to_grayscale(img)
        self.output_img = None
        self.input_stats = None
        self.output_stats = None

        # Update previews
        self._update_input_preview()
        self._clear_output_preview()
        self._set_actions_enabled(opened=True)

        # Auto-analyze
        self._auto_analyze_and_update()

        self.metrics_label.configure(text="Image analyzed. Adjust sliders; output updates when you click Normalize or move sliders.")

    def _auto_analyze_and_update(self):
        if not self.input_img:
            return
        fname = os.path.basename(self.input_path) if self.input_path else None
        self.input_stats = compute_stats(self.input_img, filename=fname)
        self._render_stats(self.input_stats_text, self.input_stats, label="Input")
        self.input_hist.draw(self.input_stats["hist"])

        # Set default sliders to current min/max
        self.var_black.set(self.input_stats["min"])
        self.var_white.set(self.input_stats["max"])
        self.var_gamma.set(1.0)

    def on_normalize(self):
        if not self.input_img:
            return
        black = self.var_black.get()
        white = self.var_white.get()
        gamma = self.var_gamma.get()

        normalized = normalize_with_levels(self.input_img, black=black, white=white, gamma=gamma)
        self.output_img = normalized
        fname = os.path.basename(self.input_path) if self.input_path else None
        self.output_stats = compute_stats(self.output_img, filename=fname + " (normalized)" if fname else "(normalized)")

        self._update_output_preview()
        self._render_stats(self.output_stats_text, self.output_stats, label="Output")
        self.output_hist.draw(self.output_stats["hist"])
        self._update_change_metrics()
        self._set_save_enabled(True)

    def on_save_as(self):
        if not self.output_img:
            messagebox.showinfo("Save", "There is no output image to save. Click Normalize first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save processed image",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("TIFF", "*.tif;*.tiff"),
                ("Bitmap", "*.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            save_params = {"quality": 95} if ext in {".jpg", ".jpeg"} else {}
            self.output_img.save(path, **save_params)
            messagebox.showinfo("Save", f"Saved processed image to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save", f"Failed to save image:\n{e}")

    # ---- Helpers ----
    def _on_slider_change(self, _value=None):
        # Keep invariants: black < white
        b = self.var_black.get()
        w = self.var_white.get()
        if w <= b:
            # Nudge white just above black to maintain order
            self.var_white.set(min(255, b + 1))
        # Live-preview normalization
        if self.input_img is not None:
            self.on_normalize()

    def _set_actions_enabled(self, opened: bool):
        state = tk.NORMAL if opened else tk.DISABLED
        self.btn_normalize.configure(state=state)
        self._action_menu.entryconfig("Normalize", state=state)
        # disable save until we have output
        self._file_menu.entryconfig("Save Output As…", state=tk.DISABLED)
        self.btn_save.configure(state=tk.DISABLED)

    def _set_save_enabled(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self._file_menu.entryconfig("Save Output As…", state=state)
        self.btn_save.configure(state=state)

    def _update_input_preview(self):
        if not self.input_img:
            self.input_preview.configure(image="", text="")
            return
        tkimg = pil_to_tk(self.input_img)
        self.input_preview.image = tkimg  # keep ref
        self.input_preview.configure(image=tkimg)

    def _update_output_preview(self):
        if not self.output_img:
            self.output_preview.configure(image="", text="")
            return
        tkimg = pil_to_tk(self.output_img)
        self.output_preview.image = tkimg
        self.output_preview.configure(image=tkimg)

    def _clear_output_preview(self):
        self.output_preview.configure(image="", text="(No output yet)")
        self.output_hist.draw(None)
        self._set_save_enabled(False)
        self._clear_stats(self.output_stats_text)

    def _render_stats(self, widget: tk.Text, stats: dict, label: str = ""):
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        if not stats:
            widget.insert(tk.END, "No statistics available.")
        else:
            fname = stats.get("filename", "")
            lines = []
            if label:
                lines.append(f"{label} metrics for: {fname}\n")
            lines.extend([
                f"Size: {stats['width']} × {stats['height']} px ({stats['pixels']} pixels)",
                f"Min: {stats['min']}  Max: {stats['max']}  Dynamic range: {stats['dynamic_range']}",
                f"Mean: {stats['mean']:.2f}  Std dev: {stats['stddev']:.2f}",
                f"Utilized brightness span: {stats['utilized_range']} levels  (bins used: {stats['bins_used_pct']:.1f}%)",
                f"Entropy: {stats['entropy']:.3f} bits/pixel",
            ])
            widget.insert(tk.END, "\n".join(lines))
        widget.configure(state=tk.DISABLED)

    def _clear_stats(self, widget: tk.Text):
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.configure(state=tk.DISABLED)

    def _update_change_metrics(self):
        if not (self.input_stats and self.output_stats):
            self.metrics_label.configure(text="")
            return
        inp = self.input_stats
        out = self.output_stats

        def safe_ratio(a, b):
            if b == 0:
                return float('inf') if a > 0 else 1.0
            return a / b

        contrast_gain = safe_ratio(out["dynamic_range"], inp["dynamic_range"])
        entropy_delta = out["entropy"] - inp["entropy"]
        mean_delta = out["mean"] - inp["mean"]
        std_gain = safe_ratio(out["stddev"], inp["stddev"])

        msg = (
            f"Dynamic range: {inp['dynamic_range']} → {out['dynamic_range']}  (×{contrast_gain:.2f})\n"
            f"Std dev: {inp['stddev']:.2f} → {out['stddev']:.2f}  (×{std_gain:.2f})\n"
            f"Mean: {inp['mean']:.2f} → {out['mean']:.2f}  (Δ {mean_delta:+.2f})\n"
            f"Entropy: {inp['entropy']:.3f} → {out['entropy']:.3f}  (Δ {entropy_delta:+.3f})"
        )
        self.metrics_label.configure(text=msg)


if __name__ == "__main__":
    App().mainloop()
