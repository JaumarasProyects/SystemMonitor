"""
SystemMonitor - Main Application Window
Refactored with modular architecture.
"""
import customtkinter as ctk
import threading
import time
from collections import deque

from config.themes import ThemeManager
from config.settings import Settings
from models.system_info import SystemInfo
from services.llm_providers import LLMService
from services.tts_service import TTSService
from ui.panels import (
    DashboardPanel, ChatPanel, SystemPanel, MemoryPanel,
    ProcessesPanel, NetworkPanel, PortsPanel, SoftwarePanel,
    CachesPanel, SecurityPanel, AnalysisPanel, SettingsPanel
)


class SystemMonitorApp(ctk.CTk):
    """Main application window for SystemMonitor."""
    
    def __init__(self):
        super().__init__()
        
        self.settings = Settings()
        saved_theme = self.settings.get('theme', 'dark') or 'dark'
        self.theme_manager = ThemeManager(saved_theme)
        self.settings.set('theme', self.theme_manager.theme_name)
        
        ctk.set_appearance_mode(self.theme_manager.theme_name)
        ctk.set_default_color_theme("blue")
        
        self.title("SystemMonitor - Monitor del Sistema")
        self.geometry("1200x750")
        self.minsize(900, 600)
        
        self.cpu_history = deque(maxlen=60)
        self.ram_history = deque(maxlen=60)
        self.gpu_history = deque(maxlen=60)
        
        self.system_info = SystemInfo()
        self.llm_service = LLMService()
        self.tts_service = TTSService()
        
        self.shared_data = {
            'dashboard': None,
            'system': None,
            'memory': None,
            'processes': None,
            'network': None,
            'ports': None,
            'software': None,
            'caches': None,
            'security': None,
            'analysis': {'general': None, 'security': None}
        }
        
        self.panels = {}
        self.current_panel = None
        self.nav_buttons = []
        
        self.tts_enabled = False
        self.tts_voice = "es-ES-AlvaroNeural"
        self.tts_rate = "+0%"
        self.tts_volume = "+0%"
        
        self.chat_visible = False
        
        self.llm_provider = ctk.StringVar(value="ollama")
        self.api_keys = {
            'openai': ctk.StringVar(value=""),
            'deepseek': ctk.StringVar(value=""),
            'anthropic': ctk.StringVar(value=""),
            'gemini': ctk.StringVar(value=""),
            'groq': ctk.StringVar(value=""),
            'grok': ctk.StringVar(value=""),
            'mistral': ctk.StringVar(value=""),
            'azure': ctk.StringVar(value=""),
        }
        
        self.setup_ui()
        self.initialize_data()
        
        self.update_running = True
        self.update_thread = threading.Thread(target=self.background_update, daemon=True)
        self.update_thread.start()
    
    def initialize_data(self):
        for _ in range(60):
            cpu = self.system_info.get_cpu_info()['usage']
            ram = self.system_info.get_memory_info()['percent']
            gpu = self.system_info.get_gpu_info()[0].get('usage', 0) if self.system_info.get_gpu_info() else 0
            self.cpu_history.append(cpu)
            self.ram_history.append(ram)
            self.gpu_history.append(gpu)
    
    def background_update(self):
        while self.update_running:
            cpu = self.system_info.get_cpu_info()['usage']
            ram = self.system_info.get_memory_info()['percent']
            gpu = self.system_info.get_gpu_info()[0].get('usage', 0) if self.system_info.get_gpu_info() else 0
            self.cpu_history.append(cpu)
            self.ram_history.append(ram)
            self.gpu_history.append(gpu)
            time.sleep(1)
    
    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        
        self.sidebar = ctk.CTkFrame(
            self, width=220, 
            fg_color=self.theme_manager.theme['bg_sec'], 
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        self.sidebar_header = None
        self.setup_sidebar_header()
        self.setup_nav_buttons()
        
        self.content_frame = ctk.CTkFrame(
            self, 
            fg_color=self.theme_manager.theme['bg_main'], 
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        
        self.setup_footer()
        self.setup_chat_panel()
        
        self.show_panel('dashboard')
    
    def setup_sidebar_header(self):
        self.sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_header.pack(pady=(20, 10))
        
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_header, text="SystemMonitor",
            font=("Segoe UI Semibold", 22), 
            text_color=self.theme_manager.theme['primary']
        )
        self.sidebar_title.pack()
        
        self.sidebar_subtitle = ctk.CTkLabel(
            self.sidebar_header, text="Monitor del Sistema",
            font=("Segoe UI", 11), 
            text_color=self.theme_manager.theme['text_sec']
        )
        self.sidebar_subtitle.pack(pady=(0, 20))
    
    def setup_nav_buttons(self):
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("💻", "Sistema", "system"),
            ("🧠", "Memoria", "memory"),
            ("⚡", "Procesos", "processes"),
            ("🌐", "Red", "network"),
            ("🔌", "Puertos", "ports"),
            ("📦", "Software", "software"),
            ("🗑️", "Cachés y Cookies", "caches"),
            ("🔒", "Seguridad", "security"),
            ("🤖", "Análisis IA", "analysis"),
            ("⚙️", "Configuración", "settings"),
        ]
        
        self.nav_buttons = []
        self.nav_button_refs = {}
        
        for icon, text, panel_id in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {text}",
                font=("Segoe UI", 13), height=42,
                fg_color="transparent", 
                text_color=self.theme_manager.theme['text'],
                hover_color=self.theme_manager.theme['hover'], 
                anchor="w",
                command=lambda p=panel_id: self.show_panel(p)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons.append(btn)
            self.nav_button_refs[panel_id] = btn
    
    def setup_footer(self):
        self.footer = ctk.CTkFrame(
            self, height=30, 
            fg_color=self.theme_manager.theme['bg_sec'], 
            corner_radius=0
        )
        self.footer.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.footer.grid_propagate(False)
        
        self.footer_label = ctk.CTkLabel(
            self.footer, text="Última actualización: --",
            font=("Segoe UI", 10), 
            text_color=self.theme_manager.theme['text_sec']
        )
        self.footer_label.pack(side="right", padx=15)
    
    def setup_chat_panel(self):
        self.panels['chat'] = ChatPanel(
            self, 
            self.theme_manager.theme,
            self
        )
        self.panels['chat'].create()
    
    def show_panel(self, panel_id):
        if self.current_panel == panel_id:
            return
        
        self.clear_content()
        
        for i, btn in enumerate(self.nav_buttons):
            btn.configure(fg_color="transparent")
        
        panel_map = {
            'dashboard': 0, 'system': 1, 'memory': 2, 'processes': 3,
            'network': 4, 'ports': 5, 'software': 6, 'caches': 7,
            'security': 8, 'analysis': 9, 'settings': 10
        }
        
        if panel_id in panel_map:
            self.nav_buttons[panel_map[panel_id]].configure(
                fg_color=self.theme_manager.theme['bg_card']
            )
        
        if panel_id not in self.panels:
            self.create_panel(panel_id)
        
        panel = self.panels[panel_id]
        
        if hasattr(panel, 'create'):
            frame = panel.create(self.nav_buttons)
            if frame:
                frame.pack(fill="both", expand=True)
        
        self.current_panel = panel_id
    
    def create_panel(self, panel_id):
        theme = self.theme_manager.theme
        
        panels_with_system_info = {'dashboard', 'system', 'memory', 'processes', 'network', 'ports', 'software', 'caches', 'security', 'analysis'}
        
        panel_classes = {
            'dashboard': DashboardPanel,
            'system': SystemPanel,
            'memory': MemoryPanel,
            'processes': ProcessesPanel,
            'network': NetworkPanel,
            'ports': PortsPanel,
            'software': SoftwarePanel,
            'caches': CachesPanel,
            'security': SecurityPanel,
            'analysis': AnalysisPanel,
            'settings': SettingsPanel,
        }
        
        if panel_id in panel_classes:
            if panel_id in panels_with_system_info:
                self.panels[panel_id] = panel_classes[panel_id](
                    self.content_frame,
                    theme,
                    self.system_info,
                    self
                )
            else:
                self.panels[panel_id] = panel_classes[panel_id](
                    self.content_frame,
                    theme,
                    self
                )
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except (AttributeError, RuntimeError):
                pass
    
    def toggle_theme(self):
        new_theme = "light" if self.theme_manager.theme_name == "dark" else "dark"
        self.theme_manager.switch_theme(new_theme)
        self.settings.set('theme', new_theme)
        ctk.set_appearance_mode(new_theme)
        
        self.refresh_sidebar()
        
        if 'chat' in self.panels and hasattr(self.panels['chat'], 'refresh'):
            self.panels['chat'].frame.destroy()
            self.panels['chat'].create()
        
        for panel_id in list(self.panels.keys()):
            if panel_id != 'chat':
                del self.panels[panel_id]
        
        if self.current_panel:
            self.show_panel(self.current_panel)
    
    def refresh_sidebar(self):
        theme = self.theme_manager.theme
        
        self.sidebar.configure(fg_color=theme['bg_sec'])
        self.footer.configure(fg_color=theme['bg_sec'])
        
        if hasattr(self, 'sidebar_title'):
            self.sidebar_title.configure(text_color=theme['primary'])
        if hasattr(self, 'sidebar_subtitle'):
            self.sidebar_subtitle.configure(text_color=theme['text_sec'])
        
        for btn in self.nav_buttons:
            btn.configure(
                text_color=theme['text'],
                hover_color=theme['hover'],
                fg_color="transparent"
            )
        
        panel_map = {
            'dashboard': 0, 'system': 1, 'memory': 2, 'processes': 3,
            'network': 4, 'ports': 5, 'software': 6, 'caches': 7,
            'security': 8, 'analysis': 9, 'settings': 10
        }
        
        if self.current_panel and self.current_panel in panel_map:
            self.nav_buttons[panel_map[self.current_panel]].configure(
                fg_color=theme['bg_card']
            )
    
    def refresh_panels(self):
        for panel in self.panels.values():
            if hasattr(panel, 'theme'):
                panel.theme = self.theme_manager.theme
        
        if self.current_panel:
            self.show_panel(self.current_panel)
    
    def store_panel_data(self, key, data):
        """Store panel data for chat context."""
        if key in self.shared_data:
            if key == 'analysis':
                self.shared_data[key] = {**self.shared_data[key], **data}
            else:
                self.shared_data[key] = data
    
    def format_uptime(self, seconds):
        """Format uptime seconds to human readable string."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        return " ".join(parts) if parts else "0m"
    
    def get_all_system_data(self):
        """Gather all system data for analysis."""
        return {
            'sistema': {
                'computer_name': self.system_info.get_system_info()['computer_name'],
                'os': self.system_info.get_system_info()['os'],
                'os_version': self.system_info.get_system_info()['os_version'],
                'architecture': self.system_info.get_system_info()['architecture'],
            },
            'cpu': self.system_info.get_cpu_info(),
            'gpu': self.system_info.get_gpu_info(),
            'memoria': self.system_info.get_memory_info(),
            'discos': self.system_info.get_disk_info(),
            'red': self.system_info.get_network_info(),
        }
    
    def on_close(self):
        self.update_running = False
        
        for panel in self.panels.values():
            if hasattr(panel, 'destroy'):
                panel.destroy()
        
        if 'chat' in self.panels and hasattr(self.panels['chat'], 'stop_audio'):
            self.panels['chat'].stop_audio()
        
        self.destroy()
