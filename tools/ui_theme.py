# -*- coding: utf-8 -*-
"""GF Observatory visual language, adapted from Mécanismes Abstraits brand v1.

No additional package, font, external web asset or hidden process is required.
"""
from __future__ import annotations

from tkinter import ttk

PALETTE = {
    'paper': '#F3EFE4',
    'white': '#FFFEFA',
    'ink': '#1B1C1A',
    'navy': '#24455B',
    'vermilion': '#D95B38',
    'sage': '#91A18C',
    'sage_pale': '#E8EFE7',
    'ochre': '#C4A25A',
    'ochre_pale': '#F8F1DC',
    'cold': '#C9D8DD',
    'graphite': '#777873',
    'border': '#DAD7CC',
    'muted': '#5F655F',
    'error_pale': '#F7E8E2',
    'row_alt': '#F8F7F2',
}


def apply_theme(root) -> None:
    """Modernise the native ttk UI without changing the underlying commands."""
    p = PALETTE
    root.configure(bg=p['paper'])
    s = ttk.Style(root)
    s.theme_use('clam')
    s.configure('.', font=('Segoe UI', 10), foreground=p['ink'], background=p['paper'])
    s.configure('TFrame', background=p['paper'])
    s.configure('Card.TFrame', background=p['white'], borderwidth=1, relief='solid')
    s.configure('Panel.TFrame', background=p['white'])
    s.configure('TLabel', background=p['paper'], foreground=p['ink'])
    s.configure('Title.TLabel', font=('Segoe UI Semibold', 21), foreground=p['ink'])
    s.configure('Eyebrow.TLabel', font=('Segoe UI Semibold', 9), foreground=p['navy'])
    s.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground=p['muted'])
    s.configure('Section.TLabel', font=('Segoe UI Semibold', 11), foreground=p['navy'])
    s.configure('Small.TLabel', font=('Segoe UI', 9), foreground=p['muted'])
    s.configure('Status.TLabel', font=('Segoe UI', 9), foreground=p['navy'])
    s.configure('Panel.TLabel', background=p['white'])
    s.configure('PanelSmall.TLabel', font=('Segoe UI', 9), foreground=p['muted'], background=p['white'])
    s.configure('TButton', font=('Segoe UI Semibold', 10), padding=(12, 8),
                foreground=p['navy'], background=p['white'], borderwidth=1,
                bordercolor=p['border'], focusthickness=1, focuscolor=p['cold'])
    s.map('TButton', background=[('disabled', '#E9E6DF'), ('pressed', p['cold']), ('active', '#F0F5F5')],
          foreground=[('disabled', p['graphite'])])
    s.configure('Accent.TButton', foreground=p['white'], background=p['vermilion'],
                bordercolor=p['vermilion'], padding=(14, 9))
    s.map('Accent.TButton', background=[('disabled', '#CFB2A9'), ('pressed', '#A74129'), ('active', '#C94E2C')],
          foreground=[('disabled', '#F8F0EB')])
    s.configure('Primary.TButton', foreground=p['white'], background=p['navy'],
                bordercolor=p['navy'], padding=(12, 8))
    s.map('Primary.TButton', background=[('disabled', '#9AA9B1'), ('pressed', '#182E3D'), ('active', '#31596F')])
    s.configure('Quiet.TButton', background=p['paper'], foreground=p['navy'],
                borderwidth=0, padding=(7, 6))
    s.map('Quiet.TButton', background=[('active', p['cold']), ('pressed', p['cold'])])
    s.configure('TEntry', fieldbackground=p['white'], foreground=p['ink'],
                bordercolor=p['border'], padding=(8, 7), lightcolor=p['cold'])
    s.configure('TCombobox', fieldbackground=p['white'], foreground=p['ink'],
                background=p['white'], arrowcolor=p['navy'], bordercolor=p['border'], padding=(7, 6))
    s.map('TCombobox', fieldbackground=[('readonly', p['white'])],
          background=[('readonly', p['white'])], foreground=[('readonly', p['ink'])])
    s.configure('Treeview', background=p['white'], fieldbackground=p['white'],
                foreground=p['ink'], borderwidth=0, rowheight=33, font=('Segoe UI', 10))
    s.configure('Treeview.Heading', background='#E7ECEB', foreground=p['navy'],
                borderwidth=0, font=('Segoe UI Semibold', 9), padding=(8, 9))
    s.map('Treeview', background=[('selected', p['navy'])], foreground=[('selected', p['white'])])
    s.map('Treeview.Heading', background=[('active', p['cold'])])
    s.configure('TNotebook', background=p['paper'], borderwidth=0, tabmargins=(0, 10, 0, 1))
    s.configure('TNotebook.Tab', background='#E9E6DF', foreground=p['muted'],
                padding=(18, 10), font=('Segoe UI Semibold', 10), borderwidth=0)
    s.map('TNotebook.Tab', background=[('selected', p['white']), ('active', p['cold'])],
          foreground=[('selected', p['navy'])])
    s.configure('Horizontal.TProgressbar', background=p['vermilion'], troughcolor=p['border'],
                borderwidth=0, thickness=5)
    s.configure('TSeparator', background=p['border'])
