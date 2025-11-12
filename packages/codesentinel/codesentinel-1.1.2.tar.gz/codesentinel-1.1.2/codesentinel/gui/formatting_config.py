# Document Formatting Configuration
from codesentinel.utils.document_formatter import FormattingScheme
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable

class FormattingSchemeSelector(tk.Frame):
    def __init__(self, parent, compact=False, **kwargs):
        super().__init__(parent, **kwargs)
        self.compact = compact
        self.current_scheme = tk.StringVar(value='black')
        
        schemes = [
            (' Black', 'black', 'Python - Uncompromising formatter'),
            (' AutoPEP8', 'autopep8', 'Python - PEP8 compliant'),
            (' Ruff', 'ruff', 'Python - Fast modern linter'),
            ('++ C++', 'cpp', 'Google C++ style guide'),
            (' Google', 'google', 'General documentation style'),
            ('⚙️ Custom', 'custom', 'Define your own rules')
        ]
        
        for name, key, desc in schemes:
            frame = tk.Frame(self, bg='#f8f8f8', relief=tk.FLAT, bd=1)
            frame.pack(fill=tk.X, pady=2)
            
            inner = ttk.Frame(frame)
            inner.pack(fill=tk.X, padx=6, pady=4)
            
            rb = ttk.Radiobutton(inner, text=name, variable=self.current_scheme, 
                                value=key, command=lambda k=key: self._on_change(k))
            rb.pack(side=tk.LEFT)
            
            ttk.Label(inner, text=desc, font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=8)
        
        self.on_scheme_change = None
    
    def _on_change(self, scheme):
        if self.on_scheme_change:
            self.on_scheme_change(scheme)
    
    def get_scheme(self):
        return self.current_scheme.get()

class FormattingCustomizationPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setting_vars = {}
        self.custom_locked = True
        
        # Container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Two column layout
        left = ttk.Frame(container)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))
        
        right = ttk.Frame(container)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,0))
        
        # Left: Basic Settings
        basic_frame = ttk.LabelFrame(left, text="⚙️ Basic Settings", padding=10)
        basic_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line length
        f1 = ttk.Frame(basic_frame)
        f1.pack(fill=tk.X, pady=5)
        ttk.Label(f1, text="Max line length:", width=16).pack(side=tk.LEFT)
        v1 = tk.IntVar(value=80)
        self.setting_vars['max_line_length'] = v1
        ttk.Spinbox(f1, from_=60, to=200, textvariable=v1, width=6).pack(side=tk.LEFT, padx=3)
        ttk.Label(f1, text="chars", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT)
        
        # Quote style
        f2 = ttk.Frame(basic_frame)
        f2.pack(fill=tk.X, pady=5)
        ttk.Label(f2, text="Quote style:", width=16).pack(side=tk.LEFT)
        v2 = tk.StringVar(value='double')
        self.setting_vars['quote_style'] = v2
        ttk.Combobox(f2, textvariable=v2, values=['single','double','preserve'], 
                     state='readonly', width=12).pack(side=tk.LEFT, padx=3)
        
        # Indentation
        f5 = ttk.Frame(basic_frame)
        f5.pack(fill=tk.X, pady=5)
        ttk.Label(f5, text="Indentation:", width=16).pack(side=tk.LEFT)
        v6 = tk.IntVar(value=4)
        self.setting_vars['indent_spaces'] = v6
        ttk.Spinbox(f5, from_=2, to=8, textvariable=v6, width=6).pack(side=tk.LEFT, padx=3)
        ttk.Label(f5, text="spaces", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT)
        
        # Right: Advanced Settings
        adv_frame = ttk.LabelFrame(right, text=" Advanced Settings", padding=10)
        adv_frame.pack(fill=tk.BOTH, expand=True)
        
        # Operator spacing
        v3 = tk.BooleanVar(value=True)
        self.setting_vars['space_around_operators'] = v3
        ttk.Checkbutton(adv_frame, text="Space around operators", variable=v3).pack(anchor=tk.W, pady=3)
        
        # Trailing whitespace
        v7 = tk.BooleanVar(value=True)
        self.setting_vars['remove_trailing_whitespace'] = v7
        ttk.Checkbutton(adv_frame, text="Remove trailing whitespace", variable=v7).pack(anchor=tk.W, pady=3)
        
        # Final newline
        v8 = tk.BooleanVar(value=True)
        self.setting_vars['ensure_final_newline'] = v8
        ttk.Checkbutton(adv_frame, text="Ensure final newline", variable=v8).pack(anchor=tk.W, pady=3)
        
        # Separator
        ttk.Separator(adv_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        
        # Blank lines
        ttk.Label(adv_frame, text="Blank Lines:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0,5))
        
        f3 = ttk.Frame(adv_frame)
        f3.pack(fill=tk.X, pady=2)
        ttk.Label(f3, text="After method:", width=14).pack(side=tk.LEFT)
        v4 = tk.IntVar(value=1)
        self.setting_vars['blank_lines_after_method'] = v4
        ttk.Spinbox(f3, from_=0, to=3, textvariable=v4, width=5).pack(side=tk.LEFT, padx=2)
        
        f4 = ttk.Frame(adv_frame)
        f4.pack(fill=tk.X, pady=2)
        ttk.Label(f4, text="After class:", width=14).pack(side=tk.LEFT)
        v5 = tk.IntVar(value=2)
        self.setting_vars['blank_lines_after_class'] = v5
        ttk.Spinbox(f4, from_=0, to=3, textvariable=v5, width=5).pack(side=tk.LEFT, padx=2)
        
        # Custom lock notice
        self.lock_label = ttk.Label(container, text="", font=('Arial', 8, 'italic'), 
                                    foreground='#e67e22')
        self.lock_label.pack(side=tk.BOTTOM, pady=(8,0))
    
    def set_scheme(self, scheme):
        """Enable/disable custom options based on scheme selection."""
        if scheme == 'custom':
            self.custom_locked = False
            self.lock_label.config(text="")
            # Enable all widgets
            for widget in self.winfo_children():
                self._enable_children(widget)
        else:
            self.custom_locked = True
            self.lock_label.config(text="ℹ Custom options locked - Select 'Custom' scheme to modify")
            # Disable all widgets except lock label
            for widget in self.winfo_children():
                if widget != self.lock_label:
                    self._disable_children(widget)
    
    def _enable_children(self, widget):
        try:
            widget.configure(state='normal')
        except:
            pass
        for child in widget.winfo_children():
            self._enable_children(child)
    
    def _disable_children(self, widget):
        try:
            if not isinstance(widget, ttk.Label):
                widget.configure(state='disabled')
        except:
            pass
        for child in widget.winfo_children():
            self._disable_children(child)
    
    def get_settings(self):
        return {k: v.get() for k, v in self.setting_vars.items()}
