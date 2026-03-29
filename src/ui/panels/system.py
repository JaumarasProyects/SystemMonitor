"""
System information panel.
"""
import customtkinter as ctk


class SystemPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Informacion del Sistema",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 15))
        
        scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.frame.pack_propagate(False)
        
        sys_info = self.system_info.get_system_info()
        cpu_info = self.system_info.get_cpu_info()
        boot_info = self.system_info.get_boot_info()
        mb_info = self.system_info.get_motherboard_info()
        bios_info = self.system_info.get_bios_info()
        battery_info = self.system_info.get_battery_info()
        gpu_info_list = self.system_info.get_gpu_info()
        
        general_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        general_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(general_card, text="Informacion General", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        info_items = [
            ("Nombre del equipo:", sys_info['computer_name']),
            ("Sistema operativo:", f"{sys_info['os']} {sys_info['os_version']}"),
            ("Arquitectura:", sys_info['architecture']),
            ("Usuario actual:", self.system_info.get_current_user()),
            ("Fecha de inicio:", boot_info['boot_time']),
            ("Tiempo de actividad:", self.app.format_uptime(boot_info['uptime_seconds'])),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(general_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=self.theme['text_sec'],
                        width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Consolas", 12), text_color=self.theme['text']).pack(side="left")
        
        ctk.CTkLabel(general_card, text="").pack(pady=10)
        
        mb_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        mb_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(mb_card, text="Placa Base", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        mb_items = [
            ("Fabricante:", mb_info['manufacturer']),
            ("Producto:", mb_info['product']),
            ("Version:", mb_info['version']),
            ("Numero de serie:", mb_info['serial']),
        ]
        
        for label, value in mb_items:
            row = ctk.CTkFrame(mb_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=self.theme['text_sec'],
                        width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Consolas", 12), text_color=self.theme['text']).pack(side="left")
        
        ctk.CTkLabel(mb_card, text="").pack(pady=10)
        
        bios_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        bios_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(bios_card, text="BIOS", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        bios_items = [
            ("Fabricante:", bios_info['manufacturer']),
            ("Version:", bios_info['version']),
            ("Fecha:", bios_info['date']),
        ]
        
        for label, value in bios_items:
            row = ctk.CTkFrame(bios_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=self.theme['text_sec'],
                        width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Consolas", 12), text_color=self.theme['text']).pack(side="left")
        
        ctk.CTkLabel(bios_card, text="").pack(pady=10)
        
        cpu_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        cpu_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(cpu_card, text="Procesador (CPU)", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        cpu_items = [
            ("Procesador:", cpu_info['name'][:70] if cpu_info['name'] else "Desconocido"),
            ("Nucleos fisicos:", str(cpu_info['cores_physical'])),
            ("Nucleos logicos:", str(cpu_info['cores_logical'])),
            ("Frecuencia actual:", f"{cpu_info['freq_current']:.0f} MHz"),
            ("Frecuencia maxima:", f"{cpu_info['freq_max']:.0f} MHz"),
            ("Frecuencia minima:", f"{cpu_info['freq_min']:.0f} MHz"),
            ("Uso actual:", f"{cpu_info['usage']:.1f}%"),
        ]
        
        for label, value in cpu_items:
            row = ctk.CTkFrame(cpu_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=self.theme['text_sec'],
                        width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Consolas", 12), text_color=self.theme['text']).pack(side="left")
        
        cores_frame = ctk.CTkFrame(cpu_card, fg_color="transparent")
        cores_frame.pack(fill="x", padx=20, pady=(10, 15))
        ctk.CTkLabel(cores_frame, text="Uso por nucleo:", font=("Segoe UI", 12),
                    text_color=self.theme['text_sec']).pack(anchor="w", pady=(0, 8))
        
        cores_grid = ctk.CTkFrame(cores_frame, fg_color="transparent")
        cores_grid.pack(fill="x")
        
        for i, usage in enumerate(cpu_info['usage_per_core']):
            core_frame = ctk.CTkFrame(cores_grid, fg_color=self.theme['bg_sec'], corner_radius=6)
            core_frame.pack(side="left", padx=3, pady=5)
            
            ctk.CTkLabel(core_frame, text=f"C{i}", font=("Segoe UI", 10),
                        text_color=self.theme['text_sec']).pack(padx=8, pady=(8, 0))
            ctk.CTkLabel(core_frame, text=f"{usage:.0f}%", font=("Segoe UI Semibold", 11),
                        text_color=self.theme['primary']).pack(padx=8, pady=(0, 8))
        
        cpu_times = self.system_info.get_cpu_times()
        times_frame = ctk.CTkFrame(cpu_card, fg_color="transparent")
        times_frame.pack(fill="x", padx=20, pady=(10, 15))
        ctk.CTkLabel(times_frame, text="Tiempos de CPU:", font=("Segoe UI", 12),
                    text_color=self.theme['text_sec']).pack(anchor="w", pady=(0, 8))
        
        times_grid = ctk.CTkFrame(times_frame, fg_color="transparent")
        times_grid.pack(fill="x")
        
        time_items = [
            ("Usuario:", f"{cpu_times['user']:.1f}s"),
            ("Sistema:", f"{cpu_times['system']:.1f}s"),
            ("Inactivo:", f"{cpu_times['idle']:.1f}s"),
        ]
        
        for label, value in time_items:
            time_frame = ctk.CTkFrame(times_grid, fg_color=self.theme['bg_sec'], corner_radius=6)
            time_frame.pack(side="left", padx=3, pady=5)
            ctk.CTkLabel(time_frame, text=label, font=("Segoe UI", 10),
                        text_color=self.theme['text_sec']).pack(padx=10, pady=(8, 0))
            ctk.CTkLabel(time_frame, text=value, font=("Consolas", 11),
                        text_color=self.theme['text']).pack(padx=10, pady=(0, 8))
        
        gpu_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        gpu_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(gpu_card, text="Tarjeta Grafica (GPU)", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        for gpu in gpu_info_list:
            gpu_row = ctk.CTkFrame(gpu_card, fg_color=self.theme['bg_sec'], corner_radius=8)
            gpu_row.pack(fill="x", padx=20, pady=5)
            
            header = ctk.CTkFrame(gpu_row, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 5))
            ctk.CTkLabel(header, text=f"GPU: {gpu.get('name', 'GPU')}",
                        font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(side="left")
            
            status_color = self.theme['success']
            status_text = "Activa"
            if gpu.get('status') and gpu.get('status') != 'OK':
                status_color = self.theme['warning']
                status_text = gpu.get('status')
            ctk.CTkLabel(header, text=status_text, font=("Segoe UI", 11),
                        text_color=status_color).pack(side="right")
            
            gpu_details = ctk.CTkFrame(gpu_row, fg_color="transparent")
            gpu_details.pack(fill="x", padx=15, pady=(0, 12))
            
            mem_gb = gpu.get('memory_gb', 0)
            if isinstance(mem_gb, str):
                try:
                    mem_gb = int(mem_gb) / (1024**3)
                except:
                    mem_gb = 0
            
            gpu_items = [
                ("Memoria:", f"{mem_gb:.2f} GB" if mem_gb else "N/A"),
                ("Driver:", gpu.get('driver', 'N/A')),
                ("Resolucion:", gpu.get('resolution', 'N/A')),
            ]
            
            if 'usage' in gpu:
                gpu_items.append(("Uso GPU:", f"{gpu['usage']:.1f}%"))
            
            for label, value in gpu_items:
                row = ctk.CTkFrame(gpu_details, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=label, font=("Segoe UI", 11), text_color=self.theme['text_sec'],
                            width=100, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=value, font=("Consolas", 11), text_color=self.theme['text']).pack(side="left")
        
        if gpu_info_list and 'usage' in gpu_info_list[0]:
            usage_row = ctk.CTkFrame(gpu_card, fg_color="transparent")
            usage_row.pack(fill="x", padx=20, pady=(0, 15))
            
            usage_label = ctk.CTkLabel(usage_row, text="Uso de GPU:", font=("Segoe UI", 12),
                                     text_color=self.theme['text_sec'])
            usage_label.pack(side="left", padx=(0, 10))
            
            gpu_usage_bar = ctk.CTkProgressBar(usage_row, width=200, height=10, corner_radius=5)
            gpu_usage_bar.set(gpu_info_list[0]['usage'] / 100)
            gpu_usage_bar.pack(side="left")
            gpu_usage_bar.configure(progress_color=self.theme['primary'])
        
        battery_card = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        battery_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(battery_card, text="Bateria", font=("Segoe UI Semibold", 16),
                    text_color=self.theme['primary']).pack(anchor="w", padx=20, pady=(15, 10))
        
        if battery_info['percent'] > 0:
            battery_row = ctk.CTkFrame(battery_card, fg_color="transparent")
            battery_row.pack(fill="x", padx=20, pady=(0, 15))
            
            ctk.CTkLabel(battery_row, text=f"Carga: {battery_info['percent']}%",
                        font=("Consolas", 12), text_color=self.theme['text']).pack(side="left", padx=(0, 20))
            
            plugged_text = "Conectado" if battery_info['plugged_in'] else "Descargando"
            ctk.CTkLabel(battery_row, text=plugged_text,
                        font=("Segoe UI", 12), 
                        text_color=self.theme['success'] if battery_info['plugged_in'] else self.theme['warning']).pack(side="left")
            
            if battery_info['time_left'] > 0 and not battery_info['plugged_in']:
                hours = battery_info['time_left'] // 3600
                minutes = (battery_info['time_left'] % 3600) // 60
                ctk.CTkLabel(battery_row, text=f" ({hours}h {minutes}m restantes)",
                            font=("Segoe UI", 12), text_color=self.theme['text_sec']).pack(side="left")
            
            bat_bar = ctk.CTkProgressBar(battery_row, width=150, height=10, corner_radius=5)
            bat_bar.set(battery_info['percent'] / 100)
            bat_bar.pack(side="left")
            bat_bar.configure(progress_color=self.theme['success'] if battery_info['percent'] > 20 else self.theme['warning'])
        else:
            ctk.CTkLabel(battery_card, text="No hay bateria o no se detecta",
                        font=("Segoe UI", 12), text_color=self.theme['text_sec']).pack(anchor="w", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(scroll, text="").pack(pady=10)
        
        self.app.store_panel_data('system', {
            'computer_name': sys_info['computer_name'],
            'os': f"{sys_info['os']} {sys_info['os_version']}",
            'architecture': sys_info['architecture'],
            'uptime': self.app.format_uptime(boot_info['uptime_seconds']),
            'motherboard': mb_info,
            'bios': bios_info,
            'cpu': cpu_info['name'],
            'cpu_cores_physical': cpu_info['cores_physical'],
            'cpu_cores_logical': cpu_info['cores_logical'],
            'cpu_freq_current_mhz': cpu_info['freq_current'],
            'cpu_usage': cpu_info['usage'],
            'cpu_usage_per_core': cpu_info['usage_per_core'],
            'gpus': gpu_info_list,
            'battery': battery_info
        })
        
        return self.frame
