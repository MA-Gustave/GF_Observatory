# -*- coding: utf-8 -*-
"""Double-click entry point, independent of pip installation."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
try:
    from gf_observatory.config import load_config
    from gf_observatory.desktop import launch
    launch(load_config(Path(__file__).resolve().parent/'observatory.toml'))
except Exception as exc:
    import tkinter as tk
    from tkinter import messagebox
    root=tk.Tk();root.withdraw()
    messagebox.showerror("GF Observatory — erreur",f"{type(exc).__name__}: {exc}")
    root.destroy()
