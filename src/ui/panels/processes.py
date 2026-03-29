"""
Processes panel.
"""
import customtkinter as ctk
import threading
import time
from ui.components import ProcessTable


class ProcessesPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.process_table = None
        self.update_job = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Procesos en Ejecucion",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 15))
        
        table_container = ctk.CTkFrame(self.frame, fg_color=self.theme['bg_card'], corner_radius=12)
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.process_table = ProcessTable(table_container, self.theme)
        self.process_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.process_table.set_refresh_callback(self.refresh_processes)
        
        self.refresh_processes()
        
        return self.frame
    
    def refresh_processes(self):
        threading.Thread(target=self.load_processes_async, daemon=True).start()
    
    def load_processes_async(self):
        processes = self.system_info.get_processes()
        self.frame.after(0, lambda: self.update_processes(processes))
    
    def update_processes(self, processes):
        if self.process_table:
            self.process_table.update_processes(processes)
            
            self.app.store_panel_data('processes', {
                'top_10': [{'name': p['name'], 'pid': p['pid'], 'cpu': p['cpu'], 
                           'memory_mb': p['memory_mb']} for p in processes[:10]]
            })
        
        self.update_job = self.frame.after(3000, self.refresh_processes)
    
    def destroy(self):
        if self.update_job:
            self.frame.after_cancel(self.update_job)
        if self.frame:
            self.frame.destroy()
