"""
Settings panel for configuration.
"""
import customtkinter as ctk


class SettingsPanel:
    def __init__(self, parent, theme, app_ref):
        self.parent = parent
        self.theme = theme
        self.app = app_ref
        self.frame = None
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(self.frame, text="Configuracion",
                             font=("Segoe UI Semibold", 24), text_color=self.theme['primary'])
        title.pack(pady=(20, 10))
        
        main_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent",
                                             width=600, height=500)
        main_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        section_llm = ctk.CTkLabel(main_frame, text="Proveedor de LLM",
                                    font=("Segoe UI Semibold", 14), text_color=self.theme['primary'])
        section_llm.pack(anchor="w", pady=(10, 5))
        
        llm_frame = ctk.CTkFrame(main_frame, fg_color=self.theme['bg_sec'])
        llm_frame.pack(fill="x", pady=(0, 15))
        llm_frame.grid_columnconfigure(1, weight=1)
        
        provider_label = ctk.CTkLabel(llm_frame, text="Proveedor:",
                                       font=("Segoe UI", 12), text_color=self.theme['text'])
        provider_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        providers = ["ollama", "openai", "deepseek", "anthropic", "gemini", "groq", "grok", "mistral", "azure"]
        self.provider_var = ctk.StringVar(value=self.app.llm_provider.get())
        provider_menu = ctk.CTkOptionMenu(llm_frame, variable=self.provider_var,
                                          values=providers, width=150,
                                          command=self.on_provider_changed)
        provider_menu.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        
        section_api = ctk.CTkLabel(main_frame, text="Claves API",
                                     font=("Segoe UI Semibold", 14), text_color=self.theme['primary'])
        section_api.pack(anchor="w", pady=(5, 5))
        
        api_frame = ctk.CTkFrame(main_frame, fg_color=self.theme['bg_sec'])
        api_frame.pack(fill="x", pady=(0, 15))
        api_frame.grid_columnconfigure(1, weight=1)
        
        self.api_entries = {}
        api_services = [
            ('openai', 'OpenAI (GPT):'),
            ('deepseek', 'DeepSeek:'),
            ('anthropic', 'Anthropic (Claude):'),
            ('gemini', 'Google Gemini:'),
            ('groq', 'Groq:'),
            ('grok', 'Grok (xAI):'),
            ('mistral', 'Mistral:'),
            ('azure', 'Azure OpenAI:'),
        ]
        
        for i, (key, label) in enumerate(api_services):
            lbl = ctk.CTkLabel(api_frame, text=label, font=("Segoe UI", 11),
                               text_color=self.theme['text'])
            lbl.grid(row=i, column=0, padx=15, pady=(10, 5), sticky="w")
            
            self.api_entries[key] = ctk.StringVar(value=self.app.api_keys[key].get())
            entry = ctk.CTkEntry(api_frame, font=("Segoe UI", 11),
                                 textvariable=self.api_entries[key], show="●")
            entry.grid(row=i, column=1, padx=(0, 15), pady=(10, 5), sticky="ew")
        
        save_api_btn = ctk.CTkButton(api_frame, text="Guardar API Keys",
                                      font=("Segoe UI", 11), height=32,
                                      fg_color=self.theme['primary'],
                                      command=self.save_api_keys)
        save_api_btn.grid(row=len(api_services), column=1, padx=(0, 15), pady=(10, 5), sticky="ew")
        
        section_theme = ctk.CTkLabel(main_frame, text="Tema",
                                      font=("Segoe UI Semibold", 14), text_color=self.theme['primary'])
        section_theme.pack(anchor="w", pady=(5, 5))
        
        from config.themes import ThemeManager
        
        theme_frame = ctk.CTkFrame(main_frame, fg_color=self.theme['bg_sec'])
        theme_frame.pack(fill="x", pady=(0, 15))
        theme_frame.grid_columnconfigure(1, weight=1)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Tema:",
                                    font=("Segoe UI", 12), text_color=self.theme['text'])
        theme_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        
        self.theme_var = ctk.StringVar(value=self.app.theme_manager.theme_name)
        theme_menu = ctk.CTkOptionMenu(theme_frame, variable=self.theme_var,
                                       values=list(ThemeManager.COLORS.keys()), width=150)
        theme_menu.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        
        apply_btn = ctk.CTkButton(theme_frame, text="Aplicar",
                                    font=("Segoe UI", 12), height=32,
                                    fg_color=self.theme['primary'],
                                    command=self.apply_theme)
        apply_btn.grid(row=0, column=2, padx=15, pady=12)
        
        return self.frame
    
    def on_provider_changed(self, value):
        self.app.llm_provider.set(value)
    
    def save_api_keys(self):
        for key, var in self.api_entries.items():
            self.app.api_keys[key].set(var.get())
    
    def apply_theme(self):
        self.app.toggle_theme()
