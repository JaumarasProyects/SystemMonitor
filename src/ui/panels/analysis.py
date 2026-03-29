"""
Analysis panel - AI-powered system analysis with Ollama.
"""
import customtkinter as ctk
import threading


class AnalysisPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.ollama_models = []
        self.analysis_in_progress = False
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Analisis con Inteligencia Artificial",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.frame, text="Usa un modelo de lenguaje local (Ollama) para analizar tu sistema. "
                              "Abre el Chat IA desde el boton del footer para conversar.",
            font=("Segoe UI", 12), text_color=self.theme['text_sec']
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 15))
        
        main_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        controls_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.model_var = ctk.StringVar(value="Cargando...")
        model_label = ctk.CTkLabel(controls_frame, text="Modelo:", font=("Segoe UI", 12),
                                   text_color=self.theme['text'])
        model_label.pack(side="left", padx=(0, 10))
        
        self.model_menu = ctk.CTkOptionMenu(controls_frame, variable=self.model_var,
                                            values=["Cargando modelos..."],
                                            width=150, height=32)
        self.model_menu.pack(side="left", padx=(0, 10))
        
        self.ollama_status_label = ctk.CTkLabel(controls_frame, text="",
                                                 font=("Segoe UI", 11), text_color=self.theme['text_sec'])
        self.ollama_status_label.pack(side="left", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(controls_frame, text="", font=("Segoe UI", 11),
                                         text_color=self.theme['text_sec'])
        self.status_label.pack(side="left", padx=10)
        
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.grid(row=0, column=0, sticky="e")
        
        self.analyze_btn = ctk.CTkButton(
            buttons_frame, text="Analisis General", font=("Segoe UI Semibold", 12),
            height=38, width=160, fg_color=self.theme['primary'], hover_color=self.theme['hover'],
            command=self.start_analysis, state="disabled"
        )
        self.analyze_btn.pack(side="left", padx=(8, 0))
        
        self.security_btn = ctk.CTkButton(
            buttons_frame, text="Seguridad", font=("Segoe UI Semibold", 12),
            height=38, width=140, fg_color=self.theme['secondary'], hover_color='#c73a52',
            command=self.start_security_analysis, state="disabled"
        )
        self.security_btn.pack(side="left")
        
        self.analysis_progress = ctk.CTkProgressBar(buttons_frame, width=150, height=8)
        self.analysis_progress.pack(side="left", padx=10)
        self.analysis_progress.pack_forget()
        
        result_card = ctk.CTkFrame(main_container, fg_color=self.theme['bg_card'], corner_radius=12)
        result_card.grid(row=1, column=0, sticky="nsew")
        
        result_header = ctk.CTkFrame(result_card, fg_color=self.theme['bg_sec'], height=35)
        result_header.pack(fill="x", padx=5, pady=(5, 0))
        result_header.pack_propagate(False)
        self.result_header_label = ctk.CTkLabel(result_header, text="Resultados de Analisis", font=("Segoe UI Semibold", 13),
                    text_color=self.theme['primary'])
        self.result_header_label.place(x=15, y=8)
        
        self.analysis_text = ctk.CTkTextbox(result_card, font=("Consolas", 11),
                                            fg_color=self.theme['bg_card'],
                                            text_color=self.theme['text'], wrap="word",
                                            scrollbar_button_color=self.theme['bg_sec'],
                                            border_width=0)
        self.analysis_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.analysis_text.insert("1.0", "Buscando modelos de Ollama instalados...\n\n"
                                          "Asegurate de que Ollama este ejecutandose.\n\n"
                                          "Usa el boton 'Chat IA' en el footer para abrir el chat.")
        
        threading.Thread(target=self.load_models_async, daemon=True).start()
        
        return self.frame
    
    def load_models_async(self):
        models = self.get_ollama_models()
        if models:
            self.ollama_models = models
            self.frame.after(0, self.update_models_ui)
    
    def get_ollama_models(self):
        import requests
        models = []
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
        except:
            pass
        return models
    
    def update_models_ui(self):
        if self.ollama_models:
            self.model_menu.configure(values=self.ollama_models)
            self.model_var.set(self.ollama_models[-1])
            self.ollama_status_label.configure(
                text=f"{len(self.ollama_models)} modelo(s) disponible(s)",
                text_color=self.theme['success']
            )
            self.analyze_btn.configure(state="normal")
            self.security_btn.configure(state="normal")
        else:
            self.ollama_status_label.configure(
                text="No se encontraron modelos",
                text_color=self.theme['secondary']
            )
    
    def start_analysis(self):
        self.run_analysis(analysis_type='general')
    
    def start_security_analysis(self):
        self.run_analysis(analysis_type='security')
    
    def run_analysis(self, analysis_type='general'):
        if self.analysis_in_progress:
            return
        
        self.analysis_in_progress = True
        self.analyze_btn.configure(state="disabled")
        self.security_btn.configure(state="disabled")
        self.analysis_progress.pack()
        self.analysis_progress.set(0)
        self.status_label.configure(text="Analizando...", text_color=self.theme['warning'])
        
        threading.Thread(target=self._analysis_thread, args=(analysis_type,), daemon=True).start()
    
    def _analysis_thread(self, analysis_type):
        try:
            model = self.model_var.get()
            system_data = self.app.get_all_system_data()
            
            self.frame.after(10, lambda: self.analysis_progress.set(0.2))
            
            if analysis_type == 'general':
                prompt = self.build_general_prompt(system_data)
            else:
                prompt = self.build_security_prompt(system_data)
            
            self.frame.after(10, lambda: self.analysis_progress.set(0.4))
            
            import requests
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.3, 'num_predict': 8192}
                },
                timeout=180
            )
            
            self.frame.after(10, lambda: self.analysis_progress.set(0.8))
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('response', 'No se pudo generar el analisis.')
                
                self.frame.after(0, lambda: self.analysis_text.delete("1.0", "end"))
                self.frame.after(0, lambda: self.analysis_text.insert("1.0", analysis))
                
                if analysis_type == 'general':
                    self.app.store_panel_data('analysis', {'general': analysis})
                else:
                    self.app.store_panel_data('analysis', {'security': analysis})
            else:
                self.frame.after(0, lambda: self.analysis_text.delete("1.0", "end"))
                self.frame.after(0, lambda: self.analysis_text.insert("1.0", f"Error: {response.status_code}"))
        
        except Exception as e:
            error_msg = str(e)
            self.frame.after(0, lambda: self.analysis_text.delete("1.0", "end"))
            self.frame.after(0, lambda msg=error_msg: self.analysis_text.insert("1.0", f"Error: {msg}"))
        finally:
            self.frame.after(10, lambda: self.analysis_progress.set(1.0))
            self.frame.after(500, lambda: self.analysis_progress.pack_forget())
            self.analysis_in_progress = False
            self.frame.after(0, lambda: self.analyze_btn.configure(state="normal"))
            self.frame.after(0, lambda: self.security_btn.configure(state="normal"))
            self.frame.after(0, lambda: self.status_label.configure(text="Completado", text_color=self.theme['success']))
    
    def build_general_prompt(self, data):
        sys_info = data['sistema']
        cpu = data['cpu']
        gpu = data['gpu']
        mem = data['memoria']
        disks = data['discos']
        red = data['red']
        
        prompt = f"""Analiza el siguiente informe del sistema y proporciona:
1. Un resumen general del estado del sistema
2. Posibles problemas de rendimiento
3. Recomendaciones de optimizacion
4. Sugerencias de mantenimiento

INFORME DEL SISTEMA:

Equipo: {sys_info['computer_name']}
SO: {sys_info['os']} {sys_info['os_version']}
Arquitectura: {sys_info['architecture']}

CPU:
- Modelo: {cpu['name']}
- Nucleos: {cpu['cores_physical']} fisicos, {cpu['cores_logical']} logicos
- Uso actual: {cpu['usage']:.1f}%

GPU: {gpu[0].get('name', 'N/A') if gpu else 'No detectada'}

Memoria RAM:
- Total: {mem['total'] / (1024**3):.1f} GB
- Usada: {mem['used'] / (1024**3):.1f} GB ({mem['percent']:.1f}%)

Almacenamiento:"""
        
        for disk in disks:
            prompt += f"\n- {disk['device']}: {disk['total'] / (1024**4):.1f} TB total, {disk['percent']:.1f}% usado"
        
        prompt += f"""

Red: {len([i for i in red['interfaces'].values() if i.get('connected')])} adaptador(es) conectado(s))

Proporciona tu analisis en espanol, de forma clara y util."""
        
        return prompt
    
    def build_security_prompt(self, data):
        sys_info = self.system_info.get_security_info()
        
        prompt = f"""Analiza la siguiente informacion de seguridad de un sistema Windows y proporciona:
1. Resumen del estado de seguridad
2. Posibles vulnerabilidades o riesgos
3. Recomendaciones para mejorar la seguridad
4. Alertas importantes si hay procesos sospechosos

ESTADO DE SEGURIDAD:

Firewall: {sys_info['firewall_status']}
Antivirus: {sys_info['antivirus_status']}

Puertos abiertos ({len(sys_info['open_ports'])}):"""
        
        for port in sys_info['open_ports'][:15]:
            prompt += f"\n- Puerto {port['port']} (PID: {port['pid']})"
        
        prompt += f"\n\nProgramas de inicio ({len(sys_info['startup_programs'])}):"
        for prog in sys_info['startup_programs'][:10]:
            prompt += f"\n- {prog['name']}"
        
        if sys_info['suspicious_processes']:
            prompt += "\n\nPROCESOS SOSPECHOSOS DETECTADOS:"
            for proc in sys_info['suspicious_processes']:
                prompt += f"\n- {proc['name']} (PID: {proc['pid']})"
        
        prompt += "\n\nProporciona tu analisis en espanol, de forma clara y priorizando los riesgos mas importantes."""
        
        return prompt
