"""
Reusable UI components for SystemMonitor.
"""
import customtkinter as ctk


class ChartFrame(ctk.CTkFrame):
    """Frame container for charts."""
    
    def __init__(self, parent, theme, **kwargs):
        super().__init__(parent, fg_color=theme['bg_card'], **kwargs)
        self.theme = theme


class InfoCard(ctk.CTkFrame):
    """Card widget displaying a title, value, and optional subtitle and icon."""
    
    def __init__(self, parent, theme, title, value, subtitle="", icon="", color=None, **kwargs):
        super().__init__(parent, fg_color=theme['bg_card'], corner_radius=12, **kwargs)
        self.theme = theme
        self.color = color or theme['primary']
        
        self.grid_columnconfigure(1, weight=1)
        
        if icon:
            icon_label = ctk.CTkLabel(self, text=icon, font=("Segoe UI", 24), text_color=self.color)
            icon_label.grid(row=0, column=0, rowspan=2, padx=(15, 5), pady=15, sticky="nsew")
        
        title_label = ctk.CTkLabel(
            self, text=title, font=("Segoe UI", 12),
            text_color=theme['text_sec']
        )
        title_label.grid(row=0, column=1 if icon else 0, padx=10, pady=(15, 0), sticky="w")
        
        value_label = ctk.CTkLabel(
            self, text=value, font=("Segoe UI Semibold", 24),
            text_color=theme['text']
        )
        value_label.grid(row=1, column=1 if icon else 0, padx=10, pady=(0, 5), sticky="w")
        self.value_label = value_label
        
        if subtitle:
            sub_label = ctk.CTkLabel(
                self, text=subtitle, font=("Segoe UI", 10),
                text_color=theme['text_sec']
            )
            sub_label.grid(row=2, column=1 if icon else 0, padx=10, pady=(0, 10), sticky="w")
    
    def update_value(self, value: str):
        """Update the displayed value."""
        self.value_label.configure(text=value)


class ProgressCard(ctk.CTkFrame):
    """Card widget displaying a progress bar with title and info."""
    
    def __init__(self, parent, theme, title, percent, used, total, **kwargs):
        super().__init__(parent, fg_color=theme['bg_card'], corner_radius=12, **kwargs)
        self.theme = theme
        
        header = ctk.CTkLabel(
            self, text=title, font=("Segoe UI Semibold", 14),
            text_color=theme['text'], anchor="w"
        )
        header.pack(fill="x", padx=15, pady=(12, 5))
        
        self.progress = ctk.CTkProgressBar(self, height=8, corner_radius=4)
        self.progress.set(percent / 100)
        self.progress.pack(fill="x", padx=15, pady=5)
        self.progress.configure(progress_color=theme['primary'])
        
        info_text = f"{used:.1f} GB / {total:.1f} GB ({percent:.1f}%)"
        self.info_label = ctk.CTkLabel(
            self, text=info_text, font=("Segoe UI", 11),
            text_color=theme['text_sec']
        )
        self.info_label.pack(padx=15, pady=(0, 10))
    
    def update(self, percent: float, used: float, total: float):
        """Update progress bar and info."""
        self.progress.set(percent / 100)
        info_text = f"{used:.1f} GB / {total:.1f} GB ({percent:.1f}%)"
        self.info_label.configure(text=info_text)


class ProcessTable(ctk.CTkFrame):
    """Table widget for displaying processes with search functionality."""
    
    def __init__(self, parent, theme, **kwargs):
        super().__init__(parent, fg_color=theme['bg_card'], corner_radius=12, **kwargs)
        self.theme = theme
        self.parent_refresh = None
        
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar proceso...",
            font=("Segoe UI", 12), height=35
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_table)
        
        refresh_btn = ctk.CTkButton(
            search_frame, text="↻", width=40, height=35,
            command=self._do_refresh
        )
        refresh_btn.pack(side="right", padx=(10, 0))
        
        columns = ["Nombre", "PID", "CPU %", "Memoria MB", "Estado"]
        widths = [250, 80, 80, 100, 80]
        
        header_frame = ctk.CTkFrame(self, fg_color=theme['bg_sec'], height=35)
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        header_frame.pack_propagate(False)
        
        for i, (col, width) in enumerate(zip(columns, widths)):
            col_label = ctk.CTkLabel(
                header_frame, text=col, font=("Segoe UI Semibold", 11),
                text_color=theme['text']
            )
            col_label.place(x=10 if i == 0 else sum(widths[:i]) + 15, y=8)
        
        scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=350
        )
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.rows_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True)
        
        self.all_processes = []
        self.filtered_processes = []
    
    def _do_refresh(self):
        """Call parent's refresh callback if set."""
        if self.parent_refresh:
            self.parent_refresh()
    
    def set_refresh_callback(self, callback):
        """Set the callback for refresh button."""
        self.parent_refresh = callback
    
    def filter_table(self, event=None):
        """Filter processes by search text."""
        search_text = self.search_entry.get().lower()
        self.filtered_processes = [
            p for p in self.all_processes
            if search_text in p['name'].lower()
        ]
        self.update_table()
    
    def update_processes(self, processes):
        """Update with new process list."""
        self.all_processes = processes[:100]
        self.filtered_processes = self.all_processes
        self.update_table()
    
    def update_table(self):
        """Render the table with current processes."""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        
        for i, proc in enumerate(self.filtered_processes[:50]):
            bg = self.theme['bg_card'] if i % 2 == 0 else self.theme['bg_sec']
            row = ctk.CTkFrame(self.rows_frame, fg_color=bg, height=28)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            
            values = [
                proc['name'][:40],
                str(proc['pid']),
                f"{proc['cpu']:.1f}",
                f"{proc['memory_mb']:.1f}",
                proc['status']
            ]
            widths = [250, 80, 80, 100, 80]
            
            for j, (val, width) in enumerate(zip(values, widths)):
                color = self.theme['text']
                if j == 2 and proc['cpu'] > 50:
                    color = self.theme['warning']
                elif j == 2 and proc['cpu'] > 80:
                    color = self.theme['secondary']
                
                label = ctk.CTkLabel(
                    row, text=val, font=("Consolas", 10),
                    text_color=color, anchor="w"
                )
                label.place(x=10 if j == 0 else sum(widths[:j]) + 15, y=5)


class NavButton:
    """Factory for creating navigation buttons."""
    
    @staticmethod
    def create(parent, icon: str, text: str, command, theme: dict, height: int = 42) -> ctk.CTkButton:
        """Create a navigation button."""
        return ctk.CTkButton(
            parent, text=f"  {icon}  {text}",
            font=("Segoe UI", 13), height=height,
            fg_color="transparent", text_color=theme['text'],
            hover_color=theme['hover'], anchor="w",
            command=command
        )
