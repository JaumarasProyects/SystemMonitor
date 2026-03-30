"""
Security panel - security tools for technicians.
"""
import customtkinter as ctk
import hashlib
import os
import requests
import threading
import time


class SecurityPanel:
    SUSPICIOUS_FOLDERS = [
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
        os.path.join(os.environ.get('APPDATA', ''), 'Local', 'Temp'),
        r'C:\Windows\Temp',
        os.path.join(os.environ.get('APPDATA', ''), ''),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), ''),
    ]
    
    SUSPICIOUS_EXTENSIONS = ['.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar']
    
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.current_view = None
        self.checked_programs = self.load_checked_programs()
        self.check_all_progress = None
        self.check_all_btn = None
        
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        self.header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, text="🔒 Seguridad",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        self.title_label.pack(side="left")
        
        self.subtitle_label = ctk.CTkLabel(
            self.frame, text="Herramientas de seguridad para analisis y deteccion de amenazas",
            font=("Segoe UI", 12), text_color=self.theme['text_sec']
        )
        self.subtitle_label.pack(anchor="w", padx=20, pady=(5, 15))
        
        self.menu_frame = ctk.CTkFrame(self.frame, fg_color=self.theme['bg_card'], corner_radius=10)
        self.menu_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.menu_buttons = {}
        menu_items = [
            ("hash", "Hash + VirusTotal", self.show_hash_view),
            ("suspicious", "Procesos Sospechosos", self.show_suspicious_view),
            ("firewall", "Firewall y Defender", self.show_firewall_view),
            ("services", "Servicios Sospechosos", self.show_services_view),
            ("users", "Usuarios Admin", self.show_users_view),
        ]
        
        for key, text, cmd in menu_items:
            btn = ctk.CTkButton(
                self.menu_frame, text=text, height=36, width=140,
                fg_color=self.theme['bg_sec'],
                text_color=self.theme['text'],
                hover_color=self.theme['hover'],
                command=cmd
            )
            btn.pack(side="left", padx=2, pady=10)
            self.menu_buttons[key] = btn
        
        self.content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.content_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)
        
        self.show_hash_view()
        
        return self.frame
    
    def clear_content(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    def set_active_menu(self, key):
        for k, btn in self.menu_buttons.items():
            if k == key:
                btn.configure(fg_color=self.theme['primary'])
            else:
                btn.configure(fg_color=self.theme['bg_sec'])
    
    def show_hash_view(self):
        self.current_view = "hash"
        self.set_active_menu("hash")
        self.clear_content()
        
        info_frame = ctk.CTkFrame(self.content_container, fg_color=self.theme['bg_card'], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text="🔍 Analisis de Hash con VirusTotal",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkLabel(info_frame, text="Selecciona un proceso para calcular su hash SHA256 y consultar en VirusTotal",
                    font=("Segoe UI", 11), text_color=self.theme['text_sec']).pack(anchor="w", padx=15, pady=(0, 12))
        
        controls = ctk.CTkFrame(self.content_container, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 10))
        
        self.vt_status = ctk.CTkLabel(controls, text="API Key: No configurada",
                                       font=("Segoe UI", 11), text_color=self.theme['warning'])
        self.vt_status.pack(side="left")
        
        self.check_all_progress = ctk.CTkLabel(controls, text="",
                                       font=("Segoe UI", 11), text_color=self.theme['text_sec'])
        self.check_all_progress.pack(side="left", padx=20)
        
        self.check_vt_btn = ctk.CTkButton(
            controls, text="Configurar API Key", width=140, height=32,
            fg_color=self.theme['secondary'],
            command=self.open_settings
        )
        self.check_vt_btn.pack(side="right")
        
        self.check_all_btn = ctk.CTkButton(
            controls, text="🔍 Verificar Todos", width=140, height=32,
            fg_color=self.theme['primary'],
            command=self.check_all_virustotal
        )
        self.check_all_btn.pack(side="right", padx=10)
        
        self.process_list_frame = ctk.CTkScrollableFrame(
            self.content_container, fg_color="transparent", height=400
        )
        self.process_list_frame.pack(fill="both", expand=True)
        
        self.vt_result_frame = None
        
        api_key = self.get_virustotal_api_key()
        if api_key:
            self.vt_status.configure(text="API Key: Configurada ✓", text_color=self.theme['success'])
            self.check_vt_btn.pack_forget()
        else:
            self.check_vt_btn.pack(side="right")
        
        self.checked_programs = self.load_checked_programs()
        
        if self.checked_programs:
            malicious = [(n, d) for n, d in [(d.get('name', '?'), d) for d in self.checked_programs.values()] 
                       if 'MALICIOSO' in d.get('status', '')]
            suspicious = [(n, d) for n, d in [(d.get('name', '?'), d) for d in self.checked_programs.values()] 
                        if 'SOSPECHOSO' in d.get('status', '')]
            unknown = [(n, d) for n, d in [(d.get('name', '?'), d) for d in self.checked_programs.values()] 
                     if 'No encontrado' in d.get('status', '')]
            
            summary_scroll = ctk.CTkScrollableFrame(
                self.content_container, fg_color="transparent", height=200
            )
            summary_scroll.pack(fill="x", pady=(0, 10))
            
            header_frame = ctk.CTkFrame(summary_scroll, fg_color="transparent")
            header_frame.pack(fill="x", padx=5, pady=(5, 5))
            
            ctk.CTkLabel(header_frame, text="📊 Resumen de Verificacion",
                        font=("Segoe UI Semibold", 12), text_color=self.theme['text']).pack(side="left")
            
            total_label = ctk.CTkLabel(header_frame, text=f"({len(self.checked_programs)} programas analizados)",
                                      font=("Segoe UI", 10), text_color=self.theme['text_sec'])
            total_label.pack(side="left", padx=(5, 0))
            
            if malicious:
                danger_frame = ctk.CTkFrame(summary_scroll, fg_color=self.theme['secondary'], corner_radius=6)
                danger_frame.pack(fill="x", padx=5, pady=3)
                
                ctk.CTkLabel(danger_frame, text=f"⚠️ MALICIOSOS ({len(malicious)})",
                            font=("Segoe UI Semibold", 11), text_color='#ffffff').pack(anchor="w", padx=10, pady=(5, 3))
                
                for name, data in malicious:
                    status = data.get('status', '')
                    ctk.CTkLabel(danger_frame, text=f"  • {name}: {status}",
                                font=("Consolas", 9), text_color='#ffffff', wraplength=500).pack(anchor="w", padx=15, pady=1)
                ctk.CTkLabel(danger_frame, text="", font=("Segoe UI", 5)).pack(pady=(0, 3))
            
            if suspicious:
                sus_frame = ctk.CTkFrame(summary_scroll, fg_color=self.theme['warning'], corner_radius=6)
                sus_frame.pack(fill="x", padx=5, pady=3)
                
                ctk.CTkLabel(sus_frame, text=f"⚠️ SOSPECHOSOS ({len(suspicious)})",
                            font=("Segoe UI Semibold", 11), text_color='#000000').pack(anchor="w", padx=10, pady=(5, 3))
                
                for name, data in suspicious:
                    status = data.get('status', '')
                    ctk.CTkLabel(sus_frame, text=f"  • {name}: {status}",
                                font=("Consolas", 9), text_color='#000000', wraplength=500).pack(anchor="w", padx=15, pady=1)
                ctk.CTkLabel(sus_frame, text="", font=("Segoe UI", 5)).pack(pady=(0, 3))
            
            if unknown and not malicious and not suspicious:
                unk_frame = ctk.CTkFrame(summary_scroll, fg_color=self.theme['bg_sec'], corner_radius=6)
                unk_frame.pack(fill="x", padx=5, pady=3)
                
                ctk.CTkLabel(unk_frame, text=f"❓ NO ENCONTRADOS ({len(unknown)}) - Posibles 0-day",
                            font=("Segoe UI Semibold", 11), text_color=self.theme['warning']).pack(anchor="w", padx=10, pady=(5, 3))
                
                for name, data in unknown[:10]:
                    ctk.CTkLabel(unk_frame, text=f"  • {name}",
                                font=("Consolas", 9), text_color=self.theme['text_sec']).pack(anchor="w", padx=15, pady=1)
                if len(unknown) > 10:
                    ctk.CTkLabel(unk_frame, text=f"  ... y {len(unknown) - 10} más",
                                font=("Consolas", 9), text_color=self.theme['text_sec']).pack(anchor="w", padx=15, pady=1)
                ctk.CTkLabel(unk_frame, text="", font=("Segoe UI", 5)).pack(pady=(0, 3))
        
        self.load_processes()
    
    def show_suspicious_view(self):
        self.current_view = "suspicious"
        self.set_active_menu("suspicious")
        self.clear_content()
        
        info_frame = ctk.CTkFrame(self.content_container, fg_color=self.theme['bg_card'], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text="⚠️ Procesos en Carpetas Sospechosas",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkLabel(info_frame, text="Procesos ejecutandose desde carpetas temporales o de usuario",
                    font=("Segoe UI", 11), text_color=self.theme['text_sec']).pack(anchor="w", padx=15, pady=(0, 12))
        
        self.suspicious_scroll = ctk.CTkScrollableFrame(
            self.content_container, fg_color="transparent"
        )
        self.suspicious_scroll.pack(fill="both", expand=True)
        
        self.load_suspicious_processes()
    
    def show_firewall_view(self):
        self.current_view = "firewall"
        self.set_active_menu("firewall")
        self.clear_content()
        
        info_frame = ctk.CTkFrame(self.content_container, fg_color=self.theme['bg_card'], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text="🛡️ Estado del Firewall y Antivirus",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(anchor="w", padx=15, pady=(12, 5))
        
        self.firewall_content = ctk.CTkScrollableFrame(
            self.content_container, fg_color="transparent"
        )
        self.firewall_content.pack(fill="both", expand=True)
        
        self.load_firewall_status()
    
    def show_services_view(self):
        self.current_view = "services"
        self.set_active_menu("services")
        self.clear_content()
        
        info_frame = ctk.CTkFrame(self.content_container, fg_color=self.theme['bg_card'], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text="🚀 Servicios de Inicio Automático",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkLabel(info_frame, text="Servicios que se ejecutan automaticamente al iniciar Windows",
                    font=("Segoe UI", 11), text_color=self.theme['text_sec']).pack(anchor="w", padx=15, pady=(0, 12))
        
        controls = ctk.CTkFrame(self.content_container, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 10))
        
        self.show_only_suspicious_var = ctk.BooleanVar(value=False)
        filter_btn = ctk.CTkSwitch(
            controls, text="Solo sospechosos", variable=self.show_only_suspicious_var,
            command=self.filter_services
        )
        filter_btn.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            controls, text="Actualizar", width=100, height=32,
            fg_color=self.theme['bg_card'],
            command=self.load_services
        )
        refresh_btn.pack(side="right")
        
        self.services_scroll = ctk.CTkScrollableFrame(
            self.content_container, fg_color="transparent"
        )
        self.services_scroll.pack(fill="both", expand=True)
        
        self.all_services = []
        self.load_services()
    
    def show_users_view(self):
        self.current_view = "users"
        self.set_active_menu("users")
        self.clear_content()
        
        info_frame = ctk.CTkFrame(self.content_container, fg_color=self.theme['bg_card'], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(info_frame, text="👥 Usuarios con Permisos Elevados",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['text']).pack(anchor="w", padx=15, pady=(12, 5))
        ctk.CTkLabel(info_frame, text="Usuarios administradores y grupos con privilegios elevados",
                    font=("Segoe UI", 11), text_color=self.theme['text_sec']).pack(anchor="w", padx=15, pady=(0, 12))
        
        self.users_scroll = ctk.CTkScrollableFrame(
            self.content_container, fg_color="transparent"
        )
        self.users_scroll.pack(fill="both", expand=True)
        
        self.load_users()
    
    def open_settings(self):
        self.app.show_panel('settings')
    
    def get_virustotal_api_key(self):
        return self.app.settings.get('virustotal_api_key', '')
    
    def calculate_sha256(self, filepath):
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None
    
    def check_virustotal(self, filepath):
        api_key = self.get_virustotal_api_key()
        if not api_key:
            return None, "API Key no configurada"
        
        file_hash = self.calculate_sha256(filepath)
        if not file_hash:
            return None, "No se pudo calcular hash"
        
        try:
            url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
            headers = {"x-apikey": api_key}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                total = stats.get('total', 0)
                
                if malicious > 0:
                    return file_hash, f"⚠️ {malicious}/{total} detectores - MALICIOSO"
                elif suspicious > 0:
                    return file_hash, f"⚠️ {suspicious}/{total} detectores - SOSPECHOSO"
                else:
                    return file_hash, f"✅ {total} detectores - LIMPIO"
            elif response.status_code == 404:
                return file_hash, "❓ No encontrado en VirusTotal (posible 0-day)"
            else:
                return file_hash, f"Error: {response.status_code}"
        except Exception as e:
            return file_hash, f"Error: {str(e)[:50]}"
    
    def load_checked_programs(self):
        data = self.app.settings.get('virustotal_report', {})
        return data if data else {}
    
    def save_checked_programs(self):
        if self.checked_programs:
            self.app.settings.set('virustotal_report', self.checked_programs)
            self.generate_virustotal_report()
    
    def generate_virustotal_report(self):
        if not self.checked_programs:
            return None
        if not isinstance(self.checked_programs, dict):
            return None
        
        malicious = []
        suspicious = []
        clean = []
        unknown = []
        malicious_names = []
        suspicious_names = []
        
        for hash_val, data in self.checked_programs.items():
            status = data.get('status', '')
            name = data.get('name', 'Unknown')
            exe = data.get('exe', '')
            
            entry = f"- **{name}**: {status}"
            
            if 'MALICIOSO' in status:
                malicious.append(entry)
                malicious_names.append(name)
            elif 'SOSPECHOSO' in status:
                suspicious.append(entry)
                suspicious_names.append(name)
            elif 'LIMPIO' in status:
                clean.append(entry)
            else:
                unknown.append(entry)
        
        report = []
        report.append(f"## INFORME VIRUSTOTAL ({len(self.checked_programs)} programas analizados)")
        report.append("")
        
        if malicious:
            report.append(f"### ⚠️ MALICIOSOS ({len(malicious)})")
            report.extend(malicious)
            report.append("")
        
        if suspicious:
            report.append(f"### ⚠️ SOSPECHOSOS ({len(suspicious)})")
            report.extend(suspicious)
            report.append("")
        
        if unknown:
            report.append(f"### ❓ NO ENCONTRADOS ({len(unknown)}) - Posibles 0-day")
            report.extend(unknown[:20])
            if len(unknown) > 20:
                report.append(f"... y {len(unknown) - 20} más")
            report.append("")
        
        if clean:
            report.append(f"### ✅ LIMPIOS ({len(clean)})")
            report.extend(clean[:20])
            if len(clean) > 20:
                report.append(f"... y {len(clean) - 20} más")
        
        report_text = "\n".join(report)
        
        existing_data = self.app.shared_data.get('security') or {}
        
        self.app.store_panel_data('security', {
            **existing_data,
            'virustotal_report': report_text,
            'malicious': malicious_names,
            'suspicious': suspicious_names
        })
        
        return report_text
    
    def _safe_update(self, widget, **kwargs):
        try:
            if widget and widget.winfo_exists():
                widget.configure(**kwargs)
        except:
            pass
    
    def _safe_pack(self, widget, **kwargs):
        try:
            if widget and widget.winfo_exists():
                widget.pack(**kwargs)
        except:
            pass
    
    def check_all_virustotal(self):
        api_key = self.get_virustotal_api_key()
        if not api_key:
            self.vt_status.configure(text="API Key no configurada", text_color=self.theme['secondary'])
            return
        
        self.check_all_progress.configure(text="Analizando... 0%", text_color=self.theme['text_sec'])
        self.check_all_btn.configure(state="disabled")
        
        process_items = getattr(self, 'process_items', [])
        if not process_items:
            self.check_all_progress.configure(text="No hay procesos para verificar", text_color=self.theme['warning'])
            self.check_all_btn.configure(state="normal")
            return
        
        threading.Thread(target=self._check_all_thread, args=(process_items,), daemon=True).start()
    
    def _check_all_thread(self, process_items):
        total = len(process_items)
        checked = 0
        new_checked = 0
        
        for i, item in enumerate(process_items):
            proc = item.get('proc', {})
            exe = proc.get('exe', '')
            if not exe:
                continue
            
            hash_val = self.calculate_sha256(exe)
            if not hash_val:
                continue
            
            name = proc.get('name', 'Unknown')
            result_label = item.get('result_label')
            hash_label = item.get('hash_label')
            
            if hash_val in self.checked_programs:
                cached = self.checked_programs[hash_val]
                result = cached.get('status', '')
                checked += 1
                
                if result_label:
                    result_color = self.theme['success']
                    if 'MALICIOSO' in result:
                        result_color = self.theme['secondary']
                    elif 'SOSPECHOSO' in result or 'No encontrado' in result:
                        result_color = self.theme['warning']
                    self.frame.after(0, lambda l=result_label, r=result, c=result_color: (
                        self._safe_update(l, text=r, text_color=c)
                    ))
                
                self.frame.after(0, lambda c=checked, t=total: self._safe_update(
                    self.check_all_progress, text=f"Ya verificado... {c}/{t}", text_color=self.theme['success']))
            else:
                file_hash, result = self.check_virustotal(exe)
                
                self.checked_programs[hash_val] = {
                    'name': name,
                    'exe': exe,
                    'pid': proc.get('pid', 0),
                    'status': result,
                    'hash': file_hash,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                new_checked += 1
                checked += 1
                
                if result_label:
                    result_color = self.theme['success']
                    if 'MALICIOSO' in result:
                        result_color = self.theme['secondary']
                    elif 'SOSPECHOSO' in result:
                        result_color = self.theme['warning']
                    elif 'No encontrado' in result:
                        result_color = self.theme['warning']
                    self.frame.after(0, lambda l=result_label, r=result, c=result_color: (
                        self._safe_update(l, text=r, text_color=c)
                    ))
                
                if hash_label and file_hash:
                    self.frame.after(0, lambda l=hash_label, h=file_hash: (
                        self._safe_update(l, text=f"Hash: {h[:32]}..."),
                        self._safe_pack(l, anchor="w", padx=12)
                    ))
                
                self.frame.after(0, lambda c=checked, t=total: self._safe_update(
                    self.check_all_progress, text=f"Analizando... {c}/{t}", text_color=self.theme['text_sec']))
            
            time.sleep(1.2)
        
        self.save_checked_programs()
        
        self.frame.after(0, lambda: self._check_all_complete(checked, new_checked, total))
    
    def _check_all_complete(self, checked, new_checked, total):
        self._safe_update(self.check_all_progress,
            text=f"✓ {new_checked} nuevos / {checked} total verificados",
            text_color=self.theme['success']
        )
        self._safe_update(self.check_all_btn, state="normal")
    
    def load_processes(self):
        for widget in self.process_list_frame.winfo_children():
            widget.destroy()
        
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
                try:
                    info = proc.info
                    if info.get('exe'):
                        processes.append(info)
                except:
                    pass
            
            processes.sort(key=lambda x: x.get('name', '').lower())
            
            self.process_items = []
            for proc in processes[:100]:
                self.add_process_item(proc)
        except Exception as e:
            ctk.CTkLabel(self.process_list_frame, text=f"Error: {str(e)}",
                        text_color=self.theme['secondary']).pack(pady=20)
    
    def add_process_item(self, proc):
        pid = proc.get('pid', 0)
        name = proc.get('name', 'Unknown')
        exe = proc.get('exe', '')
        
        item_frame = ctk.CTkFrame(self.process_list_frame, fg_color=self.theme['bg_card'], corner_radius=8)
        item_frame.pack(fill="x", pady=3)
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=8)
        
        ctk.CTkLabel(info_frame, text=f"{name}",
                    font=("Segoe UI Semibold", 12), text_color=self.theme['text']).pack(anchor="w")
        
        ctk.CTkLabel(info_frame, text=f"PID: {pid} | {exe[:60]}..." if len(exe) > 60 else f"PID: {pid} | {exe}",
                    font=("Consolas", 9), text_color=self.theme['text_sec']).pack(anchor="w")
        
        result_label = ctk.CTkLabel(item_frame, text="", font=("Segoe UI", 10), text_color=self.theme['text_sec'], anchor="w")
        result_label.pack(fill="x", padx=12, pady=(0, 5))
        
        hash_label = ctk.CTkLabel(item_frame, text="", font=("Consolas", 8), text_color=self.theme['text_sec'], anchor="w")
        
        check_btn = ctk.CTkButton(
            item_frame, text="Verificar en VT", width=120, height=28,
            fg_color=self.theme['primary'],
            command=lambda p=proc: self.check_process_virustotal(p)
        )
        check_btn.pack(side="right", padx=10, pady=5)
        
        self.process_items.append({
            'pid': pid,
            'proc': proc,
            'result_label': result_label,
            'hash_label': hash_label
        })
        
        file_hash = self.calculate_sha256(exe)
        if file_hash and file_hash in self.checked_programs:
            cached = self.checked_programs[file_hash]
            result = cached.get('status', '')
            result_color = self.theme['success']
            if 'MALICIOSO' in result:
                result_color = self.theme['secondary']
            elif 'SOSPECHOSO' in result or 'No encontrado' in result:
                result_color = self.theme['warning']
            result_label.configure(text=result, text_color=result_color)
            hash_label.configure(text=f"Hash: {file_hash[:32]}...")
            hash_label.pack(anchor="w", padx=12)
    
    def check_process_virustotal(self, proc):
        exe = proc.get('exe', '')
        if not exe:
            return
        
        pid = proc.get('pid', 0)
        for widget in self.process_list_frame.winfo_children():
            try:
                info = widget.winfo_children()
                if info and len(info) > 0:
                    name_label = info[1] if len(info) > 1 else None
                    if name_label:
                        name_text = name_label.cget("text")
                        proc_pid = proc.get('pid', 0)
                        for p in self.process_items:
                            if p.get('pid') == proc_pid:
                                result_label = p.get('result_label')
                                if result_label:
                                    result_label.configure(text="⏳ Consultando...")
                                break
            except:
                pass
        
        threading.Thread(target=self._check_vt_thread, args=(proc,), daemon=True).start()
    
    def _check_vt_thread(self, proc):
        exe = proc.get('exe', '')
        file_hash, result = self.check_virustotal(exe)
        
        self.frame.after(0, lambda: self._update_vt_result(proc, file_hash, result))
    
    def _update_vt_result(self, proc, file_hash, result):
        pid = proc.get('pid', 0)
        
        for p in self.process_items:
            if p.get('pid') == pid:
                result_label = p.get('result_label')
                if result_label:
                    result_color = self.theme['success']
                    if 'MALICIOSO' in result:
                        result_color = self.theme['secondary']
                    elif 'SOSPECHOSO' in result:
                        result_color = self.theme['warning']
                    elif 'No encontrado' in result:
                        result_color = self.theme['warning']
                    elif 'Error' in result:
                        result_color = self.theme['text_sec']
                    
                    self._safe_update(result_label, text=result, text_color=result_color)
                
                hash_label = p.get('hash_label')
                if hash_label and file_hash:
                    self._safe_update(hash_label, text=f"Hash: {file_hash[:32]}...")
                    self._safe_pack(hash_label, anchor="w", padx=12)
                break
    
    def is_suspicious_path(self, path):
        if not path:
            return False
        path_lower = path.lower()
        for sus_folder in self.SUSPICIOUS_FOLDERS:
            if sus_folder and sus_folder.lower() in path_lower:
                return True
        return False
    
    def load_suspicious_processes(self):
        for widget in self.suspicious_scroll.winfo_children():
            widget.destroy()
        
        suspicious_found = []
        
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
                try:
                    info = proc.info
                    exe = info.get('exe', '')
                    if exe and self.is_suspicious_path(exe):
                        suspicious_found.append(info)
                except:
                    pass
        except Exception as e:
            ctk.CTkLabel(self.suspicious_scroll, text=f"Error: {str(e)}",
                        text_color=self.theme['secondary']).pack(pady=20)
            return
        
        if not suspicious_found:
            no_sus = ctk.CTkFrame(self.suspicious_scroll, fg_color=self.theme['bg_card'], corner_radius=10)
            no_sus.pack(fill="x", pady=10)
            ctk.CTkLabel(no_sus, text="✅ No se encontraron procesos en carpetas sospechosas",
                        font=("Segoe UI", 14), text_color=self.theme['success']).pack(pady=20)
            self.app.store_panel_data('security', {'suspicious_processes': 0, 'processes': []})
            return
        
        summary = ctk.CTkFrame(self.suspicious_scroll, fg_color=self.theme['secondary'], corner_radius=10)
        summary.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(summary, text=f"⚠️ {len(suspicious_found)} procesos en carpetas sospechosas",
                    font=("Segoe UI Semibold", 14), text_color='#ffffff').pack(pady=10)
        
        proc_list = []
        for proc in suspicious_found:
            proc_list.append({'name': proc.get('name'), 'pid': proc.get('pid'), 'exe': proc.get('exe')})
            self.add_suspicious_item(proc)
        
        self.app.store_panel_data('security', {'suspicious_processes': len(suspicious_found), 'processes': proc_list})
    
    def add_suspicious_item(self, proc):
        name = proc.get('name', 'Unknown')
        exe = proc.get('exe', '')
        pid = proc.get('pid', 0)
        
        item_frame = ctk.CTkFrame(self.suspicious_scroll, fg_color=self.theme['bg_card'], corner_radius=8)
        item_frame.pack(fill="x", pady=4)
        
        header = ctk.CTkFrame(item_frame, fg_color=self.theme['warning'], corner_radius=6)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header, text=f"⚠️ {name}",
                    font=("Segoe UI Semibold", 12), text_color='#000000').pack(side="left", padx=10, pady=6)
        
        ctk.CTkLabel(header, text=f"PID: {pid}",
                    font=("Segoe UI", 10), text_color='#000000').pack(side="right", padx=10, pady=6)
        
        ctk.CTkLabel(item_frame, text=f"Ruta: {exe}",
                    font=("Consolas", 10), text_color=self.theme['text_sec'], wraplength=700).pack(anchor="w", padx=12, pady=(5, 10))
    
    def load_firewall_status(self):
        for widget in self.firewall_content.winfo_children():
            widget.destroy()
        
        status_items = []
        
        try:
            import subprocess
            
            fw_check = subprocess.run(
                'netsh advfirewall show allprofiles state',
                shell=True, capture_output=True, text=True
            )
            if "On" in fw_check.stdout:
                status_items.append(("Firewall de Windows", "🟢 Activado", self.theme['success']))
            else:
                status_items.append(("Firewall de Windows", "🔴 Desactivado", self.theme['secondary']))
        except:
            status_items.append(("Firewall de Windows", "⚠️ No disponible", self.theme['warning']))
        
        try:
            import subprocess
            defender_check = subprocess.run(
                'powershell -Command "Get-MpComputerStatus" | Select-String "AntivirusEnabled"',
                shell=True, capture_output=True, text=True
            )
            if "True" in defender_check.stdout:
                status_items.append(("Windows Defender", "🟢 Activado", self.theme['success']))
            else:
                status_items.append(("Windows Defender", "🔴 Desactivado", self.theme['secondary']))
        except:
            status_items.append(("Windows Defender", "⚠️ No disponible", self.theme['warning']))
        
        try:
            uac_check = subprocess.run(
                'powershell -Command "Get-ItemProperty -Path \'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\' | Select-Object EnableLUA"',
                shell=True, capture_output=True, text=True
            )
            if "1" in uac_check.stdout:
                status_items.append(("Control de Cuentas de Usuario (UAC)", "🟢 Activado", self.theme['success']))
            else:
                status_items.append(("Control de Cuentas de Usuario (UAC)", "🔴 Desactivado", self.theme['secondary']))
        except:
            status_items.append(("Control de Cuentas de Usuario (UAC)", "⚠️ No disponible", self.theme['warning']))
        
        try:
            secure_boot = subprocess.run(
                'powershell -Command "(Get-ComputerInfo).BiosInfo.SecureBootState"',
                shell=True, capture_output=True, text=True
            )
            if "On" in secure_boot.stdout:
                status_items.append(("Secure Boot", "🟢 Activado", self.theme['success']))
            else:
                status_items.append(("Secure Boot", "🟠 Desactivado", self.theme['warning']))
        except:
            status_items.append(("Secure Boot", "⚠️ No disponible", self.theme['warning']))
        
        import subprocess
        
        commands = {
            "Firewall de Windows": "control firewall.cpl",
            "Windows Defender": "ms-settings:windowsdefender",
            "Control de Cuentas de Usuario (UAC)": "UserAccountControlSettings.exe",
            "Secure Boot": None,
        }
        
        for name, status, color in status_items:
            card = ctk.CTkFrame(self.firewall_content, fg_color=self.theme['bg_card'], corner_radius=10)
            card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=15)
            
            ctk.CTkLabel(info_frame, text=name, font=("Segoe UI", 13), text_color=self.theme['text']).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=status, font=("Segoe UI Semibold", 13), text_color=color).pack(anchor="w")
            
            cmd = commands.get(name)
            if cmd:
                ctk.CTkButton(
                    card, text="Abrir", width=70, height=28,
                    fg_color=self.theme['primary'],
                    command=lambda c=cmd: subprocess.Popen(c, shell=True)
                ).pack(side="right", padx=(0, 10), pady=15)
            else:
                ctk.CTkLabel(
                    card, text="(UEFI)", font=("Segoe UI", 10), text_color=self.theme['text_sec']
                ).pack(side="right", padx=(0, 10), pady=15)
        
        security_status = {name: status for name, status, _ in status_items}
        self.app.store_panel_data('security', {'security_status': security_status})
    
    def load_services(self):
        for widget in self.services_scroll.winfo_children():
            widget.destroy()
        
        self.all_services = []
        
        try:
            import subprocess
            result = subprocess.run(
                'powershell -Command "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table -AutoSize"',
                shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore'
            )
            
            lines = result.stdout.strip().split('\n')
            for line in lines[2:]:
                if line.strip() and '---' not in line:
                    self.all_services.append({'raw': line.strip()})
        except Exception as e:
            ctk.CTkLabel(self.services_scroll, text=f"Error: {str(e)}",
                        text_color=self.theme['secondary']).pack(pady=20)
            return
        
        self.filter_services()
    
    def filter_services(self):
        for widget in self.services_scroll.winfo_children():
            widget.destroy()
        
        show_only = self.show_only_suspicious_var.get()
        
        suspicious_keywords = ['temp', 'tmp', 'appdata', 'download', 'unknown', 'temp', 'appdata', 'local']
        
        filtered = self.all_services
        
        if filtered:
            count_label = ctk.CTkLabel(self.services_scroll, 
                                       text=f"Total de servicios de inicio: {len(filtered)}",
                                       font=("Segoe UI", 12), text_color=self.theme['text_sec'])
            count_label.pack(anchor="w", pady=(0, 10))
        
        for svc in filtered:
            raw = svc.get('raw', '')
            is_suspicious = any(kw in raw.lower() for kw in suspicious_keywords)
            
            if show_only and not is_suspicious:
                continue
            
            card = ctk.CTkFrame(self.services_scroll, fg_color=self.theme['bg_card'], corner_radius=8)
            card.pack(fill="x", pady=4)
            
            if is_suspicious:
                header_color = self.theme['warning']
            else:
                header_color = self.theme['bg_sec']
            
            header = ctk.CTkFrame(card, fg_color=header_color, corner_radius=6)
            header.pack(fill="x", padx=10, pady=(8, 5))
            
            if is_suspicious:
                ctk.CTkLabel(header, text="⚠️", font=("Segoe UI", 12)).pack(side="left", padx=(10, 0))
            
            ctk.CTkLabel(header, text=raw[:80] + "..." if len(raw) > 80 else raw,
                        font=("Consolas", 10), text_color=self.theme['text']).pack(side="left", padx=5, pady=6)
        
        suspicious_count = sum(1 for s in self.all_services if any(kw in s.get('raw', '').lower() for kw in suspicious_keywords))
        self.app.store_panel_data('security', {'startup_services': len(self.all_services), 'suspicious_services': suspicious_count})
    
    def load_users(self):
        for widget in self.users_scroll.winfo_children():
            widget.destroy()
        
        users_found = []
        
        try:
            import subprocess
            result = subprocess.run(
                'net localgroup Administradores',
                shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore'
            )
            
            lines = result.stdout.strip().split('\n')
            in_list = False
            for line in lines:
                if 'Los miembros' in line or 'Members' in line:
                    in_list = True
                    continue
                if in_list and line.strip() and '-------' not in line:
                    user = line.strip()
                    if user and '\\' in user or '.' not in user:
                        users_found.append({'name': user, 'group': 'Administradores', 'suspicious': False})
        except Exception as e:
            ctk.CTkLabel(self.users_scroll, text=f"Error: {str(e)}",
                        text_color=self.theme['secondary']).pack(pady=20)
            return
        
        if not users_found:
            no_users = ctk.CTkFrame(self.users_scroll, fg_color=self.theme['bg_card'], corner_radius=10)
            no_users.pack(fill="x", pady=10)
            ctk.CTkLabel(no_users, text="No se encontraron usuarios administradores",
                        font=("Segoe UI", 14), text_color=self.theme['warning']).pack(pady=20)
            return
        
        summary = ctk.CTkFrame(self.users_scroll, fg_color=self.theme['warning'], corner_radius=10)
        summary.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(summary, text=f"👥 {len(users_found)} usuarios con permisos de Administrador",
                    font=("Segoe UI Semibold", 14), text_color='#000000').pack(pady=10)
        
        for user in users_found:
            card = ctk.CTkFrame(self.users_scroll, fg_color=self.theme['bg_card'], corner_radius=8)
            card.pack(fill="x", pady=4)
            
            header = ctk.CTkFrame(card, fg_color=self.theme['bg_sec'], corner_radius=6)
            header.pack(fill="x", padx=10, pady=(8, 5))
            
            ctk.CTkLabel(header, text=f"👤 {user['name']}",
                        font=("Segoe UI Semibold", 13), text_color=self.theme['text']).pack(side="left", padx=10, pady=8)
            
            ctk.CTkLabel(card, text=f"Grupo: {user['group']}",
                        font=("Segoe UI", 11), text_color=self.theme['text_sec']).pack(anchor="w", padx=12, pady=(0, 8))
        
        self.app.store_panel_data('security', {'admin_users': len(users_found), 'users': users_found})
