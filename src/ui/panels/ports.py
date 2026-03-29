"""
Ports panel - network connections.
"""
import customtkinter as ctk
import threading
import psutil


class PortsPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.all_connections = []
        self.filtered_connections = []
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Estado de Puertos de Red",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.frame, text="Monitorea y gestiona las conexiones de red activas",
            font=("Segoe UI", 12), text_color=self.theme['text_sec']
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 15))
        
        from ui.components import InfoCard
        
        stats_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(0, 15))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.ports_listen_card = InfoCard(stats_frame, self.theme, "Listening", "0", "Puertos escuchando")
        self.ports_listen_card.grid(row=0, column=0, padx=5)
        
        self.ports_established_card = InfoCard(stats_frame, self.theme, "Establecidas", "0", "Conexiones activas", color=self.theme['success'])
        self.ports_established_card.grid(row=0, column=1, padx=5)
        
        self.ports_timewait_card = InfoCard(stats_frame, self.theme, "Time Wait", "0", "Esperando cierre", color=self.theme['warning'])
        self.ports_timewait_card.grid(row=0, column=2, padx=5)
        
        self.ports_total_card = InfoCard(stats_frame, self.theme, "Total", "0", "Todas las conexiones", color=self.theme['primary'])
        self.ports_total_card.grid(row=0, column=3, padx=5)
        
        controls_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.port_search = ctk.CTkEntry(
            controls_frame, placeholder_text="Buscar puerto, proceso o direccion...",
            font=("Segoe UI", 12), height=36
        )
        self.port_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.port_search.bind("<KeyRelease>", lambda e: self.filter_ports())
        
        self.refresh_ports_btn = ctk.CTkButton(
            controls_frame, text="Actualizar", font=("Segoe UI", 12),
            height=36, width=120, fg_color=self.theme['bg_card'],
            command=self.load_ports
        )
        self.refresh_ports_btn.pack(side="right")
        
        self.ports_status_label = ctk.CTkLabel(controls_frame, text="",
                                               font=("Segoe UI", 11), text_color=self.theme['text_sec'])
        self.ports_status_label.pack(side="right", padx=15)
        
        ports_card = ctk.CTkFrame(self.frame, fg_color=self.theme['bg_card'], corner_radius=12)
        ports_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        header = ctk.CTkFrame(ports_card, fg_color=self.theme['bg_sec'], height=35)
        header.pack(fill="x", padx=5, pady=(5, 0))
        header.pack_propagate(False)
        
        columns = [("Puerto", 80), ("Estado", 100), ("Direccion Local", 180), ("Direccion Remota", 180), ("PID", 60), ("Proceso", 180)]
        for i, (col, width) in enumerate(columns):
            x_pos = 10
            for j in range(i):
                x_pos += columns[j][1] + 10
            ctk.CTkLabel(header, text=col, font=("Segoe UI Semibold", 11),
                        text_color=self.theme['text']).place(x=x_pos, y=8)
        
        self.ports_scroll = ctk.CTkScrollableFrame(ports_card, fg_color="transparent")
        self.ports_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.load_ports()
        
        return self.frame
    
    def get_connections(self):
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                try:
                    proc = psutil.Process(conn.pid) if conn.pid else None
                    process_name = proc.name() if proc else "Unknown"
                except:
                    process_name = "Unknown"
                
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                
                connections.append({
                    'local_addr': local_addr,
                    'remote_addr': remote_addr,
                    'status': conn.status,
                    'pid': conn.pid,
                    'process': process_name
                })
        except:
            pass
        return sorted(connections, key=lambda x: x['pid'] or 0)
    
    def load_ports(self):
        self.ports_status_label.configure(text="Cargando...", text_color=self.theme['warning'])
        threading.Thread(target=self._load_ports_thread, daemon=True).start()
    
    def _load_ports_thread(self):
        connections = self.get_connections()
        self.frame.after(0, lambda: self._update_ui(connections))
    
    def _update_ui(self, connections):
        for widget in self.ports_scroll.winfo_children():
            widget.destroy()
        
        self.all_connections = connections
        self.filtered_connections = connections
        
        listen_count = len([c for c in connections if c['status'] == 'LISTEN'])
        established_count = len([c for c in connections if c['status'] == 'ESTABLISHED'])
        timewait_count = len([c for c in connections if c['status'] == 'TIME_WAIT'])
        
        self.ports_listen_card.value_label.configure(text=str(listen_count))
        self.ports_established_card.value_label.configure(text=str(established_count))
        self.ports_timewait_card.value_label.configure(text=str(timewait_count))
        self.ports_total_card.value_label.configure(text=str(len(connections)))
        
        self.display_connections(connections)
        
        import time
        self.ports_status_label.configure(
            text=f"Ultima actualizacion: {time.strftime('%H:%M:%S')}",
            text_color=self.theme['text_sec']
        )
        
        self.app.store_panel_data('ports', {
            'total': len(connections),
            'listening': listen_count,
            'established': established_count,
            'time_wait': timewait_count,
            'connections': [{'port': c['local_addr'].split(':')[-1] if ':' in c['local_addr'] else c['local_addr'],
                            'status': c['status'], 'pid': c['pid'], 'process': c['process']} for c in connections[:50]]
        })
    
    def display_connections(self, connections):
        for widget in self.ports_scroll.winfo_children():
            widget.destroy()
        
        for i, conn in enumerate(connections[:200]):
            bg = self.theme['bg_card'] if i % 2 == 0 else self.theme['bg_sec']
            row = ctk.CTkFrame(self.ports_scroll, fg_color=bg, height=32)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            
            port = conn['local_addr'].split(':')[-1] if ':' in conn['local_addr'] else conn['local_addr']
            
            status_colors = {
                'LISTEN': self.theme['success'],
                'ESTABLISHED': self.theme['primary'],
                'TIME_WAIT': self.theme['warning'],
                'CLOSE_WAIT': self.theme['secondary'],
            }
            status_color = status_colors.get(conn['status'], self.theme['text_sec'])
            
            values = [
                (port, self.theme['text']),
                (conn['status'], status_color),
                (conn['local_addr'], self.theme['text']),
                (conn['remote_addr'], self.theme['text_sec']),
                (str(conn['pid']), self.theme['text_sec']),
                (conn['process'][:25], self.theme['text']),
            ]
            
            x_pos = 15
            widths = [80, 100, 180, 180, 60, 180]
            for j, (val, color) in enumerate(values):
                ctk.CTkLabel(row, text=val, font=("Consolas", 10),
                            text_color=color, anchor="w").place(x=x_pos, y=7)
                x_pos += widths[j] + 10
    
    def filter_ports(self):
        query = self.port_search.get().lower()
        if not query:
            self.filtered_connections = self.all_connections
        else:
            self.filtered_connections = [
                c for c in self.all_connections
                if query in c['local_addr'].lower() or
                   query in c['remote_addr'].lower() or
                   query in c['process'].lower() or
                   query in str(c['pid']) or
                   query in c['status'].lower()
            ]
        
        self.display_connections(self.filtered_connections)
        self.ports_status_label.configure(
            text=f"Mostrando {len(self.filtered_connections)} de {len(self.all_connections)} conexiones",
            text_color=self.theme['text_sec']
        )
