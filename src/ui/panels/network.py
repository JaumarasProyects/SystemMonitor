"""
Network panel.
"""
import customtkinter as ctk
from ui.components import InfoCard


class NetworkPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Red y Conexiones",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 15))
        
        scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        net_info = self.system_info.get_network_info()
        
        stats_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        stats_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(stats_card, text="Estadisticas de Red", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        stats_grid = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=(0, 15))
        stats_grid.grid_columnconfigure((0, 1), weight=1)
        
        sent_gb = net_info['bytes_sent'] / (1024**3)
        recv_gb = net_info['bytes_recv'] / (1024**3)
        
        InfoCard(stats_grid, self.theme, "Enviados", f"{sent_gb:.2f} GB", "Bytes totales",
                color=self.theme['success']).grid(row=0, column=0, padx=5)
        InfoCard(stats_grid, self.theme, "Recibidos", f"{recv_gb:.2f} GB", "Bytes totales",
                color=self.theme['primary']).grid(row=0, column=1, padx=5)
        
        adapters_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        adapters_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(adapters_card, text="Adaptadores de Red", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        for iface, data in net_info['interfaces'].items():
            iface_row = ctk.CTkFrame(adapters_card, fg_color=self.theme['bg_sec'], corner_radius=8)
            iface_row.pack(fill="x", padx=20, pady=5)
            
            status_color = self.theme['success'] if data.get('connected') else self.theme['secondary']
            status_text = "Conectado" if data.get('connected') else "Desconectado"
            
            header = ctk.CTkFrame(iface_row, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 5))
            ctk.CTkLabel(header, text=iface, font=("Segoe UI Semibold", 13),
                        text_color=self.theme['text']).pack(side="left")
            ctk.CTkLabel(header, text=status_text, font=("Segoe UI", 11),
                        text_color=status_color).pack(side="right")
            
            details = ctk.CTkFrame(iface_row, fg_color="transparent")
            details.pack(fill="x", padx=15, pady=(0, 12))
            
            if data.get('ipv4'):
                ctk.CTkLabel(details, text=f"IP: {data['ipv4']}", font=("Consolas", 11),
                            text_color=self.theme['text_sec']).pack(anchor="w")
            if data.get('netmask'):
                ctk.CTkLabel(details, text=f"Mask: {data['netmask']}", font=("Consolas", 11),
                            text_color=self.theme['text_sec']).pack(anchor="w")
            if data.get('speed'):
                ctk.CTkLabel(details, text=f"Velocidad: {data['speed']} Mbps",
                            font=("Consolas", 11), text_color=self.theme['text_sec']).pack(anchor="w")
        
        self.app.store_panel_data('network', {
            'bytes_sent_gb': sent_gb,
            'bytes_recv_gb': recv_gb,
            'interfaces': net_info['interfaces']
        })
        
        return self.frame
