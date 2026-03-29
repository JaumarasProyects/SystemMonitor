"""
Memory and storage panel.
"""
import customtkinter as ctk
from ui.components import InfoCard


class MemoryPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Memoria y Almacenamiento",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 15))
        
        scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ram_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        ram_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(ram_card, text="Memoria RAM", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        mem_info = self.system_info.get_memory_info()
        total_gb = mem_info['total'] / (1024**3)
        used_gb = mem_info['used'] / (1024**3)
        free_gb = mem_info['free'] / (1024**3)
        
        ram_grid = ctk.CTkFrame(ram_card, fg_color="transparent")
        ram_grid.pack(fill="x", padx=20, pady=(0, 15))
        ram_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        InfoCard(ram_grid, self.theme, "Total", f"{total_gb:.1f} GB", "GB").grid(row=0, column=0, padx=5)
        InfoCard(ram_grid, self.theme, "Usada", f"{used_gb:.1f} GB", "GB", color=self.theme['secondary']).grid(row=0, column=1, padx=5)
        InfoCard(ram_grid, self.theme, "Libre", f"{free_gb:.1f} GB", "GB", color=self.theme['success']).grid(row=0, column=2, padx=5)
        
        progress_bar = ctk.CTkProgressBar(ram_card, height=12, corner_radius=6)
        progress_bar.set(mem_info['percent'] / 100)
        progress_bar.pack(fill="x", padx=20, pady=(0, 15))
        progress_bar.configure(progress_color=self.theme['warning'])
        
        ctk.CTkLabel(ram_card, text=f"Uso: {mem_info['percent']:.1f}%",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(pady=(0, 15))
        
        disk_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        disk_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(disk_card, text="Almacenamiento", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        disks = self.system_info.get_disk_info()
        for disk in disks:
            disk_row = ctk.CTkFrame(disk_card, fg_color=self.theme['bg_sec'], corner_radius=8)
            disk_row.pack(fill="x", padx=20, pady=5)
            
            total_tb = disk['total'] / (1024**4)
            used_tb = disk['used'] / (1024**4)
            free_tb = disk['free'] / (1024**4)
            
            header = ctk.CTkFrame(disk_row, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 5))
            ctk.CTkLabel(header, text=f"{disk['device']} ({disk['mountpoint']})",
                        font=("Segoe UI Semibold", 13), text_color=self.theme['text']).pack(side="left")
            ctk.CTkLabel(header, text=f"{disk['fstype']}", font=("Segoe UI", 10),
                        text_color=self.theme['text_sec']).pack(side="right")
            
            prog = ctk.CTkProgressBar(disk_row, height=8, corner_radius=4)
            prog.set(disk['percent'] / 100)
            prog.pack(fill="x", padx=15, pady=5)
            
            color = self.theme['success']
            if disk['percent'] > 90:
                color = self.theme['secondary']
            elif disk['percent'] > 75:
                color = self.theme['warning']
            prog.configure(progress_color=color)
            
            info = ctk.CTkLabel(disk_row, text=f"{used_tb:.2f} TB usados de {total_tb:.2f} TB ({disk['percent']:.1f}%)  |  {free_tb:.2f} TB libres",
                               font=("Segoe UI", 11), text_color=self.theme['text_sec'])
            info.pack(padx=15, pady=(0, 12))
        
        self.app.store_panel_data('memory', {
            'ram_total_gb': total_gb,
            'ram_used_gb': used_gb,
            'ram_free_gb': free_gb,
            'ram_percent': mem_info['percent'],
            'disks': [{'device': d['device'], 'total_tb': d['total']/(1024**4), 
                      'used_tb': d['used']/(1024**4), 'free_tb': d['free']/(1024**4), 
                      'percent': d['percent'], 'fstype': d['fstype']} for d in disks]
        })
        
        return self.frame
