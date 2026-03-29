"""
Caches panel - browser cache management.
"""
import customtkinter as ctk
import os
import shutil
import sqlite3
import threading


class CachesPanel:
    def __init__(self, parent, theme, system_info, app_ref):
        self.parent = parent
        self.theme = theme
        self.system_info = system_info
        self.app = app_ref
        self.frame = None
        self.browser_cards = []
    
    def create(self, nav_buttons):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame, text="Caches y Cookies de Navegadores",
            font=("Segoe UI Semibold", 24), text_color=self.theme['text']
        )
        title.pack(anchor="w", padx=25, pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.frame, text="Gestiona el almacenamiento local de los navegadores web",
            font=("Segoe UI", 12), text_color=self.theme['text_sec']
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 15))
        
        controls_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.refresh_caches_btn = ctk.CTkButton(
            controls_frame, text="Actualizar", font=("Segoe UI", 12),
            height=36, fg_color=self.theme['bg_card'],
            command=self.load_browser_caches
        )
        self.refresh_caches_btn.pack(side="left", padx=(0, 10))
        
        self.clear_all_btn = ctk.CTkButton(
            controls_frame, text="Limpiar Todo", font=("Segoe UI Semibold", 12),
            height=36, fg_color=self.theme['secondary'],
            hover_color='#c73a52',
            command=self.clear_all_caches
        )
        self.clear_all_btn.pack(side="left")
        
        self.cache_status_label = ctk.CTkLabel(controls_frame, text="",
                                               font=("Segoe UI", 11), text_color=self.theme['text_sec'])
        self.cache_status_label.pack(side="left", padx=15)
        
        self.cache_scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.cache_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.load_browser_caches()
        
        return self.frame
    
    def get_folder_size(self, path):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
        except:
            pass
        return total_size / (1024 * 1024)
    
    def get_cookies_info(self, db_path, is_firefox=False):
        info = {'count': 0, 'size_kb': 0, 'cookies': []}
        try:
            if os.path.exists(db_path):
                info['size_kb'] = os.path.getsize(db_path) / 1024
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cookies")
                result = cursor.fetchone()
                info['count'] = result[0] if result else 0
                
                try:
                    cursor.execute("""
                        SELECT host, name, value, path, expires_utc, isSecure, isHttpOnly 
                        FROM cookies 
                        ORDER BY host, name 
                        LIMIT 200
                    """)
                    rows = cursor.fetchall()
                    for row in rows:
                        info['cookies'].append({
                            'host': row[0] or '',
                            'name': row[1] or '',
                            'value': (row[2] or '')[:50] + '...' if row[2] and len(row[2]) > 50 else (row[2] or ''),
                            'path': row[3] or '/',
                            'secure': bool(row[5]),
                            'http_only': bool(row[6])
                        })
                except:
                    pass
                
                conn.close()
        except:
            pass
        return info
    
    def get_browser_cache_info(self):
        browsers = []
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')
        
        browser_paths = {
            'Google Chrome': {
                'base': os.path.join(local_appdata, 'Google', 'Chrome', 'User Data', 'Default'),
                'cache': ['Cache', 'Code Cache', 'GPUCache'],
                'cookies_db': 'Network\\Cookies',
            },
            'Microsoft Edge': {
                'base': os.path.join(local_appdata, 'Microsoft', 'Edge', 'User Data', 'Default'),
                'cache': ['Cache', 'Code Cache', 'GPUCache'],
                'cookies_db': 'Network\\Cookies',
            },
            'Mozilla Firefox': {
                'base': os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
                'cache': ['cache2'],
                'cookies_db': 'cookies.sqlite',
                'is_firefox': True
            },
        }
        
        for browser_name, config in browser_paths.items():
            browser_data = {
                'name': browser_name,
                'installed': False,
                'cache_size_mb': 0,
                'cookies_count': 0,
                'cookies_size_kb': 0,
                'cookies': [],
                'paths_found': [],
                'base': config['base']
            }
            
            base_path = config['base']
            if config.get('is_firefox'):
                if os.path.exists(base_path):
                    for profile in os.listdir(base_path):
                        profile_path = os.path.join(base_path, profile)
                        if os.path.isdir(profile_path):
                            browser_data['installed'] = True
                            for cache_name in config['cache']:
                                cache_path = os.path.join(profile_path, cache_name)
                                if os.path.exists(cache_path):
                                    size = self.get_folder_size(cache_path)
                                    browser_data['cache_size_mb'] += size
                                    browser_data['paths_found'].append(cache_path)
                            cookies_path = os.path.join(profile_path, config['cookies_db'])
                            if os.path.exists(cookies_path):
                                cookies_info = self.get_cookies_info(cookies_path, True)
                                browser_data['cookies_count'] += cookies_info['count']
                                browser_data['cookies_size_kb'] += cookies_info['size_kb']
                                browser_data['cookies'] = cookies_info['cookies']
            else:
                if os.path.exists(base_path):
                    browser_data['installed'] = True
                    for cache_name in config['cache']:
                        cache_path = os.path.join(base_path, cache_name)
                        if os.path.exists(cache_path):
                            size = self.get_folder_size(cache_path)
                            browser_data['cache_size_mb'] += size
                            browser_data['paths_found'].append(cache_path)
                    cookies_path = os.path.join(base_path, config['cookies_db'])
                    if os.path.exists(cookies_path):
                        cookies_info = self.get_cookies_info(cookies_path, False)
                        browser_data['cookies_count'] = cookies_info['count']
                        browser_data['cookies_size_kb'] = cookies_info['size_kb']
                        browser_data['cookies'] = cookies_info['cookies']
            
            if browser_data['installed']:
                browsers.append(browser_data)
        
        return browsers
    
    def load_browser_caches(self):
        for widget in self.cache_scroll.winfo_children():
            widget.destroy()
        
        self.browser_cards = []
        
        total_cache = 0
        total_cookies = 0
        
        browsers = self.get_browser_cache_info()
        
        if not browsers:
            no_browsers = ctk.CTkLabel(
                self.cache_scroll, text="No se detectaron navegadores instalados",
                font=("Segoe UI", 14), text_color=self.theme['text_sec']
            )
            no_browsers.pack(pady=50)
            return
        
        for browser in browsers:
            card = ctk.CTkFrame(self.cache_scroll, fg_color=self.theme['bg_card'], corner_radius=12)
            card.pack(fill="x", pady=(0, 12))
            
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(15, 10))
            
            browser_title = ctk.CTkLabel(
                header, text=browser['name'],
                font=("Segoe UI Semibold", 16), text_color=self.theme['text']
            )
            browser_title.pack(side="left")
            
            total_cache += browser['cache_size_mb']
            total_cookies += browser['cookies_count']
            
            cache_mb = browser['cache_size_mb']
            cache_label = f"{cache_mb:.1f} MB"
            if cache_mb > 1024:
                cache_label = f"{cache_mb/1024:.2f} GB"
            
            cache_frame = ctk.CTkFrame(card, fg_color=self.theme['bg_sec'], corner_radius=8)
            cache_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(cache_frame, text="Cache", font=("Segoe UI Semibold", 12),
                        text_color=self.theme['primary']).place(x=15, y=10)
            ctk.CTkLabel(cache_frame, text=cache_label, font=("Segoe UI Semibold", 14),
                        text_color=self.theme['text']).place(x=150, y=10)
            
            clear_cache_btn = ctk.CTkButton(
                cache_frame, text="Limpiar", width=80, height=28,
                fg_color=self.theme['warning'], hover_color='#cc8800',
                command=lambda b=browser: self.clear_browser_cache(b)
            )
            clear_cache_btn.place(x=280, y=8)
            
            cookies_kb = browser['cookies_size_kb']
            cookies_mb = cookies_kb / 1024
            cookies_label = f"{cookies_mb:.2f} MB ({browser['cookies_count']} cookies)"
            
            cookies_frame = ctk.CTkFrame(card, fg_color=self.theme['bg_sec'], corner_radius=8)
            cookies_frame.pack(fill="x", padx=20, pady=(0, 5))
            
            ctk.CTkLabel(cookies_frame, text="Cookies", font=("Segoe UI Semibold", 12),
                        text_color=self.theme['success']).place(x=15, y=10)
            ctk.CTkLabel(cookies_frame, text=cookies_label, font=("Segoe UI", 11),
                        text_color=self.theme['text']).place(x=150, y=10)
            
            clear_cookies_btn = ctk.CTkButton(
                cookies_frame, text="Limpiar", width=80, height=28,
                fg_color=self.theme['secondary'], hover_color='#c73a52',
                command=lambda b=browser: self.clear_browser_cookies(b)
            )
            clear_cookies_btn.place(x=280, y=8)
            
            cookies_btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            cookies_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            show_cookies_btn = ctk.CTkButton(
                cookies_btn_frame, text="Ver Cookies", width=120, height=32,
                fg_color=self.theme['primary'],
                command=lambda b=browser: self.show_cookies_dialog(b)
            )
            show_cookies_btn.pack(side="left")
            
            browser['card'] = card
            self.browser_cards.append(browser)
        
        total_label = f"Total: {total_cache:.1f} MB en cache | {total_cookies} cookies"
        self.cache_status_label.configure(text=total_label)
        
        self.app.store_panel_data('caches', {
            'total_cache_mb': total_cache,
            'total_cookies': total_cookies,
            'browsers': [{'name': b['name'], 'cache_mb': b['cache_size_mb'], 
                         'cookies': b['cookies_count']} for b in browsers]
        })
    
    def show_cookies_dialog(self, browser):
        dialog = ctk.CTkToplevel(self.frame)
        dialog.title(f"Cookies - {browser['name']}")
        dialog.geometry("800x600")
        dialog.transient(self.frame)
        
        dialog.grid_rowconfigure(1, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(dialog, height=50, fg_color=self.theme['bg_sec'])
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(header_frame, text=f"Cookies de {browser['name']} ({browser['cookies_count']} total)",
                    font=("Segoe UI Semibold", 14), text_color=self.theme['primary']).pack(side="left", padx=15, pady=10)
        
        search_frame = ctk.CTkFrame(dialog, fg_color=self.theme['bg_sec'])
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar cookies...",
                                    font=("Segoe UI", 12))
        search_entry.pack(fill="x", padx=10, pady=10)
        
        cookies_container = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        cookies_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cookies_container.grid_columnconfigure(0, weight=1)
        
        def filter_cookies(search_text=""):
            for widget in cookies_container.winfo_children():
                widget.destroy()
            
            cookies = browser.get('cookies', [])
            if not cookies:
                ctk.CTkLabel(cookies_container, text="No se pudieron leer las cookies",
                            font=("Segoe UI", 12), text_color=self.theme['text_sec']).pack(pady=20)
                return
            
            filtered = cookies
            if search_text:
                search_text = search_text.lower()
                filtered = [c for c in cookies if search_text in c['host'].lower() or search_text in c['name'].lower()]
            
            if not filtered:
                ctk.CTkLabel(cookies_container, text=f"No se encontraron cookies para '{search_text}'",
                            font=("Segoe UI", 12), text_color=self.theme['text_sec']).pack(pady=20)
                return
            
            for i, cookie in enumerate(filtered[:100]):
                cookie_frame = ctk.CTkFrame(cookies_container, fg_color=self.theme['bg_card'], corner_radius=8)
                cookie_frame.pack(fill="x", pady=3)
                
                host_text = cookie['host']
                if cookie['secure']:
                    host_text = "🔒 " + host_text
                if cookie['http_only']:
                    host_text += " [HTTP]"
                
                ctk.CTkLabel(cookie_frame, text=host_text,
                            font=("Segoe UI Semibold", 11), text_color=self.theme['primary']).pack(anchor="w", padx=12, pady=(8, 2))
                
                name_text = f"Nombre: {cookie['name']}"
                ctk.CTkLabel(cookie_frame, text=name_text,
                            font=("Consolas", 10), text_color=self.theme['text']).pack(anchor="w", padx=12, pady=1)
                
                if cookie['value']:
                    value_text = f"Valor: {cookie['value']}"
                    ctk.CTkLabel(cookie_frame, text=value_text,
                                font=("Consolas", 9), text_color=self.theme['text_sec']).pack(anchor="w", padx=12, pady=(0, 8))
                else:
                    ctk.CTkLabel(cookie_frame, text="Valor: (vacio)",
                                font=("Consolas", 9), text_color=self.theme['text_sec']).pack(anchor="w", padx=12, pady=(0, 8))
            
            if len(filtered) > 100:
                ctk.CTkLabel(cookies_container, text=f"Mostrando 100 de {len(filtered)} cookies",
                            font=("Segoe UI", 10), text_color=self.theme['text_sec']).pack(pady=10)
        
        def on_search(*args):
            filter_cookies(search_entry.get())
        
        search_entry.bind("<KeyRelease>", on_search)
        
        filter_cookies("")
        
        close_btn = ctk.CTkButton(dialog, text="Cerrar", command=dialog.destroy)
        close_btn.grid(row=3, column=0, pady=10)
    
    def clear_browser_cache(self, browser):
        try:
            for path in browser['paths_found']:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                        os.makedirs(path, exist_ok=True)
                    except:
                        pass
            
            self.cache_status_label.configure(
                text=f"Cache de {browser['name']} limpiada",
                text_color=self.theme['success']
            )
            self.frame.after(2000, lambda: self.cache_status_label.configure(text=""))
            self.load_browser_caches()
        except Exception as e:
            self.cache_status_label.configure(
                text=f"Error: {str(e)[:50]}",
                text_color=self.theme['secondary']
            )
    
    def clear_browser_cookies(self, browser):
        try:
            base_path = browser.get('base', '')
            cookies_path = os.path.join(base_path, 'Network', 'Cookies')
            
            if os.path.exists(cookies_path):
                conn = sqlite3.connect(cookies_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cookies")
                conn.commit()
                conn.close()
                
                self.cache_status_label.configure(
                    text=f"Cookies de {browser['name']} eliminadas",
                    text_color=self.theme['success']
                )
            else:
                firefox_profiles = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
                if os.path.exists(firefox_profiles):
                    for profile in os.listdir(firefox_profiles):
                        cookies_file = os.path.join(firefox_profiles, profile, 'cookies.sqlite')
                        if os.path.exists(cookies_file):
                            conn = sqlite3.connect(cookies_file)
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM cookies")
                            conn.commit()
                            conn.close()
                
                self.cache_status_label.configure(
                    text=f"Cookies de {browser['name']} eliminadas",
                    text_color=self.theme['success']
                )
            
            self.frame.after(2000, lambda: self.cache_status_label.configure(text=""))
            self.load_browser_caches()
        except Exception as e:
            self.cache_status_label.configure(
                text=f"Error: {str(e)[:50]}",
                text_color=self.theme['secondary']
            )
    
    def clear_all_caches(self):
        for browser in self.browser_cards:
            self.clear_browser_cache(browser)
