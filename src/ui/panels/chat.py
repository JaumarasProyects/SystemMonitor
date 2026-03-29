"""
Chat panel module with LLM integration and TTS.
"""
import customtkinter as ctk
import threading
import asyncio
import os
import edge_tts


class ChatPanel:
    def __init__(self, parent, theme, app_ref):
        self.parent = parent
        self.theme = theme
        self.app = app_ref
        self.frame = None
        
        self.tts_enabled = app_ref.tts_enabled
        self.tts_voice = app_ref.tts_voice
        self.tts_rate = app_ref.tts_rate
        self.tts_volume = app_ref.tts_volume
        self.audio_playing = False
        self.stop_audio_flag = threading.Event()
        
        self.ollama_connected = False
        self.ollama_models = []
        self.ollama_model = None
        
        self.chat_model_var = None
        self.chat_model_menu = None
        self.chat_status = None
        self.chat_scroll = None
        self.chat_container = None
        self.chat_input = None
        self.send_btn = None
        self.voice_btn = None
        self.stop_audio_btn = None
    
    def create(self):
        self.frame = ctk.CTkFrame(self.parent, width=380, fg_color=self.theme['bg_sec'], corner_radius=0)
        self.frame.grid(row=0, column=2, sticky="nsew")
        self.frame.grid_propagate(False)
        
        header = ctk.CTkFrame(self.frame, height=50, fg_color=self.theme['bg_card'])
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="🤖 Chat con IA",
                            font=("Segoe UI Semibold", 16), text_color=self.theme['primary'])
        title.pack(side="left", padx=15, pady=10)
        
        self.stop_audio_btn = ctk.CTkButton(header, text="⏹", width=40, height=32,
                                            fg_color=self.theme['bg_sec'], hover_color=self.theme['hover'],
                                            text_color=self.theme['text_sec'], state="disabled",
                                            command=self.stop_audio)
        self.stop_audio_btn.pack(side="right", padx=(0, 5), pady=8)
        
        self.voice_btn = ctk.CTkButton(header, text="🔊", width=40, height=32,
                                       fg_color=self.theme['bg_sec'], hover_color=self.theme['hover'],
                                       text_color=self.theme['text_sec'], state="disabled",
                                       command=self.toggle_voice)
        self.voice_btn.pack(side="right", padx=10, pady=8)
        
        controls_frame = ctk.CTkFrame(self.frame, height=45, fg_color=self.theme['bg_sec'])
        controls_frame.pack(fill="x")
        controls_frame.pack_propagate(False)
        
        model_label = ctk.CTkLabel(controls_frame, text="Modelo:",
                                   font=("Segoe UI", 11), text_color=self.theme['text_sec'])
        model_label.pack(side="left", padx=(10, 5))
        
        self.chat_model_var = ctk.StringVar(value="Cargando...")
        self.chat_model_menu = ctk.CTkOptionMenu(controls_frame, variable=self.chat_model_var,
                                                  values=["Cargando..."], width=140, height=28)
        self.chat_model_menu.pack(side="left", padx=(0, 10))
        
        self.chat_status = ctk.CTkLabel(controls_frame, text="",
                                        font=("Segoe UI", 10), text_color=self.theme['text_sec'])
        self.chat_status.pack(side="right", padx=10)
        
        self.chat_scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.chat_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_container = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        self.chat_container.pack(fill="x", expand=True)
        
        self.show_welcome()
        
        input_frame = ctk.CTkFrame(self.frame, height=60, fg_color=self.theme['bg_sec'])
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        input_frame.pack_propagate(False)
        
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_input = ctk.CTkTextbox(input_frame, font=("Segoe UI", 12), height=40,
                                         fg_color=self.theme['bg_card'], text_color=self.theme['text'],
                                         border_width=0, wrap="word")
        self.chat_input.grid(row=0, column=0, padx=(5, 5), pady=8, sticky="ew")
        self.chat_input.bind("<Return>", lambda e: self.send_message())
        
        self.send_btn = ctk.CTkButton(input_frame, text="➤", width=50, height=40,
                                      font=("Segoe UI", 16), fg_color=self.theme['primary'],
                                      hover_color=self.theme['hover'], state="disabled",
                                      command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=(0, 5), pady=8)
        
        self.app.after(200, lambda: threading.Thread(target=self.load_models_async, daemon=True).start())
        
        return self.frame
    
    def show_welcome(self):
        for widget in self.chat_container.winfo_children():
            widget.destroy()
        
        welcome = ctk.CTkFrame(self.chat_container, fg_color=self.theme['bg_sec'], corner_radius=10)
        welcome.pack(fill="x", pady=5, padx=5)
        
        msg = ctk.CTkLabel(welcome, text="👋 ¡Bienvenido al Chat de IA!\n\n"
                                          "Puedo ayudarte a analizar los datos de tu sistema.\n\n"
                                          "Cada panel ya tiene datos que puedo interpretar:\n"
                                          "• Dashboard: Resumen general\n"
                                          "• Sistema: CPU, GPU, placa base\n"
                                          "• Memoria: RAM y almacenamiento\n"
                                          "• Procesos: Aplicaciones en ejecución\n"
                                          "• Red: Conexiones de red\n"
                                          "• Puertos: Servicios de red\n"
                                          "• Software: Programas instalados\n"
                                          "• Cachés: Datos de navegadores\n"
                                          "• Análisis IA: Informes del LLM",
                                          font=("Segoe UI", 11), text_color=self.theme['text'],
                                          justify="left", wraplength=340)
        msg.pack(padx=12, pady=12)
    
    def update_ui(self):
        if self.ollama_connected and self.ollama_models:
            self.chat_model_menu.configure(values=self.ollama_models)
            self.chat_model_var.set(self.ollama_model or "")
            self.chat_status.configure(
                text=f"✓ {len(self.ollama_models)} modelo(s)", 
                text_color=self.theme['success']
            )
            self.send_btn.configure(state="normal")
            self.voice_btn.configure(state="normal")
        else:
            self.chat_status.configure(
                text="⚠️ Ollama no disponible", 
                text_color=self.theme['secondary']
            )
    
    def load_models_async(self):
        models = self.get_ollama_models()
        if models:
            self.ollama_models = models
            self.ollama_model = models[-1]
            self.ollama_connected = True
        self.app.after(0, self.update_ui)
    
    def get_ollama_models(self):
        import requests
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m['name'] for m in data.get('models', [])]
        except:
            pass
        return []
    
    def toggle_voice(self):
        self.tts_enabled = not self.tts_enabled
        self.app.tts_enabled = self.tts_enabled
        if self.tts_enabled:
            self.voice_btn.configure(fg_color=self.theme['success'], text_color=self.theme['bg_main'])
            self.chat_status.configure(text="🔊 Voz activada", text_color=self.theme['success'])
        else:
            self.voice_btn.configure(fg_color=self.theme['bg_card'], text_color=self.theme['text_sec'])
            self.chat_status.configure(text="Voz desactivada", text_color=self.theme['text_sec'])
    
    def add_message(self, message, is_user=False):
        msg_frame = ctk.CTkFrame(self.chat_container, 
                                  fg_color=self.theme['primary'] if is_user else self.theme['bg_sec'],
                                  corner_radius=10)
        msg_frame.pack(fill="x", pady=4, padx=5, anchor="e" if is_user else "w")
        
        label = ctk.CTkLabel(msg_frame, text=message, font=("Segoe UI", 11),
                            text_color=self.theme['bg_main'] if is_user else self.theme['text'],
                            justify="left", wraplength=340)
        label.pack(padx=12, pady=8)
        
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
    
    def send_message(self):
        message = self.chat_input.get("1.0", "end-1c").strip()
        if not message:
            return
        
        self.chat_input.delete("1.0", "end")
        self.add_message(message, is_user=True)
        
        self.send_btn.configure(state="disabled")
        threading.Thread(target=self.run_request, args=(message,), daemon=True).start()
    
    def build_context(self):
        context_parts = []
        shared_data = self.app.shared_data
        
        if shared_data.get('dashboard'):
            context_parts.append("## DASHBOARD:\n" + str(shared_data['dashboard']))
        if shared_data.get('system'):
            context_parts.append("## SISTEMA:\n" + str(shared_data['system']))
        if shared_data.get('memory'):
            context_parts.append("## MEMORIA:\n" + str(shared_data['memory']))
        if shared_data.get('processes'):
            context_parts.append("## PROCESOS:\n" + str(shared_data['processes']))
        if shared_data.get('network'):
            context_parts.append("## RED:\n" + str(shared_data['network']))
        if shared_data.get('ports'):
            context_parts.append("## PUERTOS:\n" + str(shared_data['ports']))
        if shared_data.get('software'):
            context_parts.append("## SOFTWARE:\n" + str(shared_data['software']))
        if shared_data.get('caches'):
            context_parts.append("## CACHÉS:\n" + str(shared_data['caches']))
        if shared_data.get('analysis', {}).get('general'):
            context_parts.append("## ANÁLISIS GENERAL:\n" + str(shared_data['analysis']['general']))
        if shared_data.get('analysis', {}).get('security'):
            context_parts.append("## ANÁLISIS DE SEGURIDAD:\n" + str(shared_data['analysis']['security']))
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def run_request(self, user_message):
        import requests
        try:
            system_context = """Eres un asistente de IA especializado en análisis de sistemas Windows.
Tienes acceso a datos del sistema del usuario. Responde de forma clara, concisa y útil en español.
Usa listas y emojis para hacer más legible tu respuesta.
Si el usuario pregunta sobre acciones específicas, proporciona comandos concretos cuando sea posible."""
            
            context = self.build_context()
            if context:
                system_context += f"\n\nDatos disponibles del sistema del usuario:\n\n{context}"
            
            self.frame.after(0, lambda: self.add_message("Pensando...", is_user=False))
            
            model = self.chat_model_var.get()
            if model == "Sin modelos" or model == "Cargando..." or not self.ollama_connected:
                self.clear_thinking()
                self.frame.after(0, lambda: self.add_message("⚠️ Ollama no está disponible. Asegúrate de que esté ejecutándose.", is_user=False))
                self.frame.after(0, lambda: self.send_btn.configure(state="normal"))
                return
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': f"{system_context}\n\nUsuario: {user_message}",
                    'system': system_context,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': 2000
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'No pude generar una respuesta.')
                
                self.clear_thinking()
                self.frame.after(0, lambda: self.add_message(ai_response, is_user=False))
                
                if self.tts_enabled:
                    threading.Thread(target=self.speak_text, args=(ai_response,), daemon=True).start()
            else:
                self.clear_thinking()
                self.frame.after(0, lambda: self.add_message(f"❌ Error: {response.status_code}", is_user=False))
                
        except Exception as e:
            self.clear_thinking()
            self.frame.after(0, lambda: self.add_message(f"❌ Error: {str(e)}", is_user=False))
        finally:
            self.frame.after(0, lambda: self.send_btn.configure(state="normal"))
    
    def clear_thinking(self):
        for widget in self.chat_container.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and "Pensando..." in child.cget("text"):
                        widget.destroy()
                        break
    
    def stop_audio(self):
        try:
            self.stop_audio_flag.set()
            import pygame
            if pygame.mixer.get_init():
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                pygame.mixer.quit()
            self.audio_playing = False
            self.stop_audio_flag.clear()
            if self.stop_audio_btn:
                self.stop_audio_btn.configure(state="disabled")
        except Exception as e:
            print(f"Stop audio error: {e}")
            self.audio_playing = False
    
    def speak_text(self, text):
        import re
        try:
            clean_text = self.clean_text_for_tts(text)
            if not clean_text.strip():
                return
            self.audio_playing = True
            self.frame.after(0, lambda: self.stop_audio_btn.configure(state="normal"))
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._speak_async(clean_text))
            loop.close()
            self.audio_playing = False
            self.frame.after(0, lambda: self.stop_audio_btn.configure(state="disabled"))
        except Exception as e:
            print(f"TTS Error: {e}")
            self.audio_playing = False
    
    def clean_text_for_tts(self, text):
        import re
        text = re.sub(r'[*#_~`>]+', ' ', text)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        replacements = {
            '👍': 'me gusta', '👎': 'no me gusta', '✅': 'hecho', '❌': 'error',
            '⚠️': 'atencion', '🔊': '', '💻': '', '🧠': '', '⚡': '', '🌐': '',
            '📊': '', '📦': '', '🗑️': '', '🤖': '', '🔌': '', '👋': 'hola',
            '🎉': 'celebracion', '🚀': 'lanzamiento', '💡': 'idea', '❤️': 'me gusta',
            '🔥': 'fuego', '⭐': 'estrella', '📝': 'nota', '💰': 'dinero',
            '🎯': 'objetivo', '🔒': 'seguro', '🔓': 'desbloqueado',
        }
        for emoji, word in replacements.items():
            text = text.replace(emoji, word)
        text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    async def _speak_async(self, text):
        audio_file = os.path.join(os.path.dirname(__file__), "..", "..", "temp_tts.mp3")
        
        try:
            import pygame
            communicate = edge_tts.Communicate(text, self.tts_voice, 
                                               rate=self.tts_rate, volume=self.tts_volume)
            await communicate.save(audio_file)
            
            if os.path.exists(audio_file) and not self.stop_audio_flag.is_set():
                pygame.mixer.init()
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() and not self.stop_audio_flag.is_set():
                    pygame.time.Clock().tick(10)
                pygame.mixer.quit()
                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                except:
                    pass
        except Exception as e:
            print(f"TTS Error: {e}")
