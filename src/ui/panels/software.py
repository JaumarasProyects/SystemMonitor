"""
Software panel - installed programs list.
"""
import customtkinter as ctk
import threading


class SoftwarePanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.loading_label = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Software Instalado",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 15))
        
        self.loading_label = ctk.CTkLabel(
            self.frame, text="Cargando lista de software...",
            font=("Segoe UI", 14), text_color=self.theme['text_sec']
        )
        self.loading_label.pack(pady=50)
        
        threading.Thread(target=self.load_software_async, daemon=True).start()
        
        return self.frame
    
    def load_software_async(self):
        try:
            software = self.system_info.get_installed_software()
            self.frame.after(0, lambda: self.display_software(software))
        except Exception as e:
            self.frame.after(0, lambda: self.loading_label.configure(text=f"Error al cargar: {e}"))
    
    def display_software(self, software):
        self.loading_label.destroy()
        
        search_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar programa...",
            font=("Segoe UI", 12), height=38
        )
        search_entry.pack(fill="x")
        
        count_label = ctk.CTkLabel(
            search_frame, text=f"{len(software)} programas encontrados",
            font=("Segoe UI", 11), text_color=self.theme['text_sec']
        )
        count_label.pack(pady=(5, 0))
        
        scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        list_frame = ctk.CTkFrame(scroll, fg_color=self.theme['bg_card'], corner_radius=12)
        list_frame.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(list_frame, fg_color=self.theme['bg_sec'], height=35)
        header.pack(fill="x", padx=5, pady=(5, 0))
        header.pack_propagate(False)
        
        headers = [("Programa", 350), ("Version", 150), ("Editor", 250), ("Fecha", 120)]
        for text, width in headers:
            ctk.CTkLabel(header, text=text, font=("Segoe UI Semibold", 11),
                        text_color=self.theme['text']).place(x=headers.index((text, width)) * (width + 20) + 15, y=8)
        
        items_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        items_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        def update_list(items):
            for widget in items_frame.winfo_children():
                widget.destroy()
            
            for i, item in enumerate(items[:100]):
                bg = self.theme['bg_card'] if i % 2 == 0 else self.theme['bg_sec']
                row = ctk.CTkFrame(items_frame, fg_color=bg, height=30)
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                
                values = [
                    item['name'][:50],
                    item.get('version', 'N/A')[:20],
                    (item.get('publisher', 'N/A') or 'N/A')[:35],
                    item.get('install_date', 'N/A')
                ]
                
                x_pos = 15
                for val in values:
                    ctk.CTkLabel(row, text=val, font=("Consolas", 10),
                                text_color=self.theme['text'], anchor="w").place(x=x_pos, y=6)
                    x_pos += (150 if val == values[0] else 120) + 20
        
        def filter_software():
            query = search_entry.get().lower()
            filtered = [s for s in software if query in s['name'].lower() or query in (s.get('publisher', '') or '').lower()]
            count_label.configure(text=f"{len(filtered)} programas encontrados")
            update_list(filtered)
        
        search_entry.bind("<KeyRelease>", lambda e: filter_software())
        
        update_list(software)
        
        self.app.store_panel_data('software', {
            'count': len(software),
            'programs': [{'name': s['name'], 'version': s.get('version', 'N/A'), 
                        'publisher': s.get('publisher', 'N/A')} for s in software[:50]]
        })
