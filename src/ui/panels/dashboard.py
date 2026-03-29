"""
Dashboard panel showing system overview with charts and cards.
"""
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class DashboardPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.update_job = None
        
        self.cpu_history = app_ref.cpu_history
        self.ram_history = app_ref.ram_history
        
        self.cpu_card = None
        self.ram_card = None
        self.disk_card = None
        self.net_card = None
        
        self.canvas_cpu = None
        self.canvas_ram = None
        self.ax_cpu = None
        self.ax_ram = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        from ui.components import InfoCard
        
        title = ctk.CTkLabel(
            self.frame, text="Dashboard",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 15))
        
        cards_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=(0, 15))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.cpu_card = InfoCard(cards_frame, self.theme, "CPU", "0%", "Procesador")
        self.cpu_card.grid(row=0, column=0, padx=5)
        
        self.ram_card = InfoCard(cards_frame, self.theme, "RAM", "0%", "Memoria")
        self.ram_card.grid(row=0, column=1, padx=5)
        
        self.disk_card = InfoCard(cards_frame, self.theme, "Disco C:", "0%", "Almacenamiento")
        self.disk_card.grid(row=0, column=2, padx=5)
        
        self.net_card = InfoCard(cards_frame, self.theme, "Red", "Activa", "Conexion")
        self.net_card.grid(row=0, column=3, padx=5)
        
        charts_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        from ui.components import ChartFrame
        
        cpu_chart_frame = ChartFrame(charts_frame, self.theme)
        cpu_chart_frame.grid(row=0, column=0, padx=(0, 7), sticky="nsew")
        
        ram_chart_frame = ChartFrame(charts_frame, self.theme)
        ram_chart_frame.grid(row=0, column=1, padx=(7, 0), sticky="nsew")
        
        self.fig_cpu = Figure(figsize=(4, 3), facecolor=self.theme['bg_card'])
        self.ax_cpu = self.fig_cpu.add_subplot(111)
        self.ax_cpu.set_facecolor(self.theme['bg_card'])
        
        self.fig_ram = Figure(figsize=(4, 3), facecolor=self.theme['bg_card'])
        self.ax_ram = self.fig_ram.add_subplot(111)
        self.ax_ram.set_facecolor(self.theme['bg_card'])
        
        self.canvas_cpu = FigureCanvasTkAgg(self.fig_cpu, master=cpu_chart_frame)
        self.canvas_cpu.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_ram = FigureCanvasTkAgg(self.fig_ram, master=ram_chart_frame)
        self.canvas_ram.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update()
        
        return self.frame
    
    def update(self):
        try:
            cpu_info = self.system_info.get_cpu_info()
            mem_info = self.system_info.get_memory_info()
            disk_info = self.system_info.get_disk_info()
            net_info = self.system_info.get_network_info()
            
            self.cpu_card.value_label.configure(text=f"{cpu_info['usage']:.1f}%")
            self.ram_card.value_label.configure(text=f"{mem_info['percent']:.1f}%")
            
            disk_c = next((d for d in disk_info if 'C:' in d['device']), disk_info[0] if disk_info else None)
            if disk_c:
                self.disk_card.value_label.configure(text=f"{disk_c['percent']:.1f}%")
            
            connected_nets = [k for k, v in net_info['interfaces'].items() if v.get('connected')]
            self.net_card.value_label.configure(text=f"{len(connected_nets)} Activa(s)")
            
            self.update_charts()
            
            import time
            self.app.footer_label.configure(text=f"Ultima actualizacion: {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error updating dashboard: {e}")
        
        self.update_job = self.frame.after(1000, self.update)
    
    def update_charts(self):
        self.ax_cpu.clear()
        self.ax_cpu.set_facecolor(self.theme['bg_card'])
        
        history_list = list(self.cpu_history)
        self.ax_cpu.plot(history_list, color=self.theme['primary'], linewidth=2)
        self.ax_cpu.fill_between(range(len(history_list)), history_list, alpha=0.3, color=self.theme['primary'])
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_title('CPU %', color=self.theme['text'], fontsize=10)
        self.ax_cpu.tick_params(colors=self.theme['text_sec'], labelsize=8)
        self.ax_cpu.spines['bottom'].set_color(self.theme['border'])
        self.ax_cpu.spines['left'].set_color(self.theme['border'])
        self.ax_cpu.spines['top'].set_visible(False)
        self.ax_cpu.spines['right'].set_visible(False)
        
        self.canvas_cpu.draw()
        
        self.ax_ram.clear()
        self.ax_ram.set_facecolor(self.theme['bg_card'])
        
        mem_info = self.system_info.get_memory_info()
        used = mem_info['used'] / (1024**3)
        free = mem_info['free'] / (1024**3)
        
        self.ax_ram.pie([used, free], labels=['Usado', 'Libre'], autopct='%1.1f%%',
                       colors=[self.theme['secondary'], self.theme['success']],
                       textprops={'color': self.theme['text']})
        self.ax_ram.set_title('Memoria RAM', color=self.theme['text'], fontsize=10)
        
        self.canvas_ram.draw()
    
    def destroy(self):
        if self.update_job:
            self.frame.after_cancel(self.update_job)
        if self.frame:
            self.frame.destroy()
