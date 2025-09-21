"""
Anime Downloader - Interfaz Gráfica con Tkinter (Versión Corregida)
GUI simple y funcional para el downloader
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import logging
from urllib.parse import urlparse
from datetime import datetime

from downloader import AnimeDownloader
from config import Config
from utils import validate_url, format_bytes, format_duration

class AnimeDownloaderGUI:
    """Interfaz gráfica principal para el Anime Downloader"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        self.setup_logging()
        
        # Downloader instance
        self.downloader = None
        self.download_thread = None
        self.is_downloading = False
        
    def setup_window(self):
        """Configuración inicial de la ventana"""
        self.root.title("Anime Downloader v1.0.0")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(600, 500)
        
        # Configurar el ícono (si existe)
        try:
            # self.root.iconbitmap('icon.ico')  # Descomentar si tienes un ícono
            pass
        except:
            pass
        
        # Hacer la ventana responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def setup_variables(self):
        """Inicializar variables de Tkinter"""
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value=Config.DEFAULT_QUALITY)
        self.output_path_var = tk.StringVar(value=Config.DOWNLOAD_PATH)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Listo para descargar")
        self.download_info_var = tk.StringVar(value="")
        self.enable_subtitles_var = tk.BooleanVar(value=False)
        
    def setup_widgets(self):
        """Crear y configurar todos los widgets"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # === Sección de URL ===
        url_frame = ttk.LabelFrame(main_frame, text="URL del Episodio", padding="10")
        url_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Arial', 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(url_frame, text="Obtener Info", command=self.get_video_info).grid(row=0, column=1)
        
        # === Sección de Configuración ===
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Calidad
        ttk.Label(config_frame, text="Calidad:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        quality_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.quality_var,
            values=list(Config.QUALITY_PREFERENCES.keys()),
            state="readonly",
            width=10
        )
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Checkbox para subtítulos
        self.subtitles_check = ttk.Checkbutton(
            config_frame, 
            text="Subtítulos (puede causar errores)", 
            variable=self.enable_subtitles_var
        )
        self.subtitles_check.grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        # Ruta de descarga
        ttk.Label(config_frame, text="Destino:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        path_frame = ttk.Frame(config_frame)
        path_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.output_path_var, width=40)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(path_frame, text="Buscar", command=self.browse_folder).grid(row=0, column=1)
        
        # === Información del Video ===
        info_frame = ttk.LabelFrame(main_frame, text="Información del Video", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        # === Progreso de Descarga ===
        progress_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100,
            style="TProgressbar"
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Etiqueta de estado
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # === Botones de Control ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        self.download_button = ttk.Button(
            button_frame,
            text="Iniciar Descarga",
            command=self.start_download
        )
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.cancel_download,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Limpiar", command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón modo seguro
        ttk.Button(button_frame, text="Modo Seguro", command=self.enable_safe_mode).pack(side=tk.LEFT)
        
        # === Log de Actividad ===
        log_frame = ttk.LabelFrame(main_frame, text="Log de Actividad", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Courier', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # === Menú ===
        self.setup_menu()
        
        # Configurar grid weights para hacer la interfaz responsive
        main_frame.rowconfigure(5, weight=1)  # El frame del log se expande
        
    def setup_menu(self):
        """Crear menú de la aplicación"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir carpeta de descargas", command=self.open_download_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Limpiar logs", command=self.clear_logs)
        tools_menu.add_command(label="Modo seguro", command=self.enable_safe_mode)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
    def setup_logging(self):
        """Configurar logging para mostrar en la GUI"""
        # Handler personalizado para mostrar logs en la GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget, root):
                super().__init__()
                self.text_widget = text_widget
                self.root = root
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    try:
                        self.text_widget.configure(state=tk.NORMAL)
                        self.text_widget.insert(tk.END, msg + '\n')
                        self.text_widget.configure(state=tk.DISABLED)
                        self.text_widget.see(tk.END)
                    except tk.TclError:
                        pass  # Widget fue destruido
                self.root.after(0, append)
        
        # Configurar el handler
        gui_handler = GUILogHandler(self.log_text, self.root)
        gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
        gui_handler.setFormatter(formatter)
        
        # Agregar handler al logger principal
        logging.getLogger().addHandler(gui_handler)
        
    def log_message(self, message, level="INFO"):
        """Agregar mensaje al log de la GUI"""
        def append():
            try:
                self.log_text.configure(state=tk.NORMAL)
                timestamp = datetime.now().strftime('%H:%M:%S')
                formatted_message = f"[{timestamp}] {level}: {message}\n"
                self.log_text.insert(tk.END, formatted_message)
                self.log_text.configure(state=tk.DISABLED)
                self.log_text.see(tk.END)
            except tk.TclError:
                pass  # Widget fue destruido
        
        self.root.after(0, append)
        
    def browse_folder(self):
        """Abrir diálogo para seleccionar carpeta de descarga"""
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de descarga",
            initialdir=self.output_path_var.get()
        )
        if folder:
            self.output_path_var.set(folder)
            
    def get_video_info(self):
        """Obtener información del video desde la URL"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Advertencia", "Por favor ingresa una URL")
            return
            
        if not validate_url(url):
            messagebox.showerror("Error", "URL inválida")
            return
            
        # Deshabilitar botón mientras se obtiene info
        self.download_button.configure(state=tk.DISABLED)
        self.status_var.set("Obteniendo información del video...")
        
        def fetch_info():
            error_occurred = None
            info_result = None
            
            try:
                # Crear downloader temporal
                temp_downloader = AnimeDownloader(
                    output_path=self.output_path_var.get(),
                    quality=self.quality_var.get()
                )
                
                info_result = temp_downloader.get_video_info(url)
                
            except Exception as e:
                error_occurred = str(e)
            
            # Actualizar GUI en el hilo principal
            def update_gui():
                try:
                    if info_result:
                        self.display_video_info(info_result)
                    else:
                        messagebox.showerror(
                            "Error", 
                            f"No se pudo obtener información del video.\nError: {error_occurred or 'Desconocido'}"
                        )
                finally:
                    self.download_button.configure(state=tk.NORMAL)
                    self.status_var.set("Listo para descargar")
            
            self.root.after(0, update_gui)
        
        # Ejecutar en hilo separado
        threading.Thread(target=fetch_info, daemon=True).start()
        
    def display_video_info(self, info):
        """Mostrar información del video en la GUI"""
        try:
            self.info_text.configure(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            
            info_text = f"Título: {info.get('title', 'N/A')}\n"
            
            if info.get('duration'):
                info_text += f"Duración: {format_duration(info['duration'])}\n"
                
            if info.get('uploader'):
                info_text += f"Subido por: {info['uploader']}\n"
                
            if info.get('upload_date'):
                info_text += f"Fecha: {info['upload_date']}\n"
                
            if info.get('description'):
                desc = info['description'][:200]  # Truncar descripción
                if len(info['description']) > 200:
                    desc += "..."
                info_text += f"Descripción: {desc}\n"
            
            self.info_text.insert(1.0, info_text)
            self.info_text.configure(state=tk.DISABLED)
        except Exception as e:
            self.log_message(f"Error mostrando información: {e}", "ERROR")
        
    def start_download(self):
        """Iniciar descarga del video"""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Advertencia", "Por favor ingresa una URL")
            return
            
        if not validate_url(url):
            messagebox.showerror("Error", "URL inválida")
            return
            
        if self.is_downloading:
            messagebox.showwarning("Advertencia", "Ya hay una descarga en progreso")
            return
            
        # Configurar UI para descarga
        self.is_downloading = True
        self.download_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Iniciando descarga...")
        
        # Crear downloader
        self.downloader = AnimeDownloader(
            output_path=self.output_path_var.get(),
            quality=self.quality_var.get(),
            max_retries=Config.MAX_RETRIES,
            concurrent_downloads=1
        )
        
        def download_worker():
            success = False
            error_msg = None
            
            try:
                # Decidir si usar subtítulos
                enable_subs = self.enable_subtitles_var.get()
                
                if enable_subs:
                    self.log_message("Descarga con subtítulos activada", "WARNING")
                    success = self.downloader.download_episode_with_subtitles(url, self.progress_callback)
                else:
                    self.log_message("Descarga en modo seguro (sin subtítulos)", "INFO")
                    success = self.downloader.download_episode_safe(url, self.progress_callback)
                    
            except Exception as e:
                error_msg = str(e)
                success = False
            
            # Actualizar GUI en hilo principal
            def update_gui():
                if success:
                    self.download_complete(True)
                else:
                    self.download_error(error_msg or "Error desconocido")
                    
            self.root.after(0, update_gui)
        
        # Iniciar descarga en hilo separado
        self.download_thread = threading.Thread(target=download_worker, daemon=True)
        self.download_thread.start()
        
    def progress_callback(self, data):
        """Callback para actualizar progreso de descarga"""
        def update_ui():
            try:
                status = data.get('status', 'unknown')
                
                if status == 'downloading':
                    percentage = data.get('percentage', 0)
                    self.progress_var.set(percentage)
                    
                    downloaded = data.get('downloaded_bytes', 0)
                    total = data.get('total_bytes', 0)
                    speed = data.get('speed', 0)
                    eta = data.get('eta', 0)
                    
                    status_text = f"Descargando... {percentage:.1f}%"
                    
                    if total > 0:
                        status_text += f" ({format_bytes(downloaded)} / {format_bytes(total)})"
                        
                    if speed:
                        status_text += f" - {format_bytes(speed)}/s"
                        
                    if eta:
                        status_text += f" - ETA: {eta}s"
                        
                    self.status_var.set(status_text)
                    
                elif status == 'finished':
                    self.progress_var.set(100)
                    self.status_var.set("Descarga completada")
                    
                elif status == 'error':
                    self.status_var.set(f"Error: {data.get('error', 'Error desconocido')}")
            except Exception as e:
                self.log_message(f"Error en callback de progreso: {e}", "ERROR")
        
        self.root.after(0, update_ui)
        
    def download_complete(self, success):
        """Callback cuando la descarga se completa"""
        self.is_downloading = False
        self.download_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        
        if success:
            self.status_var.set("✅ Descarga completada exitosamente")
            self.log_message("Descarga completada exitosamente", "SUCCESS")
            messagebox.showinfo("Éxito", "Descarga completada exitosamente")
        else:
            self.status_var.set("❌ Error en la descarga")
            messagebox.showerror("Error", "Error en la descarga. Revisa el log para más detalles.")
            
    def download_error(self, error_msg):
        """Callback cuando ocurre un error en la descarga"""
        self.is_downloading = False
        self.download_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        self.status_var.set(f"❌ Error: {error_msg}")
        self.log_message(f"Error en descarga: {error_msg}", "ERROR")
        messagebox.showerror("Error", f"Error en la descarga: {error_msg}")
        
    def cancel_download(self):
        """Cancelar descarga en progreso"""
        if self.is_downloading:
            # Nota: yt-dlp no tiene cancelación directa, esto es más bien para la UI
            self.is_downloading = False
            self.download_button.configure(state=tk.NORMAL)
            self.cancel_button.configure(state=tk.DISABLED)
            self.status_var.set("Descarga cancelada")
            self.log_message("Descarga cancelada por el usuario", "WARNING")
            
    def enable_safe_mode(self):
        """Activar modo seguro"""
        self.enable_subtitles_var.set(False)
        self.status_var.set("Modo seguro activado")
        self.log_message("Modo seguro activado - sin subtítulos, sin thumbnails", "INFO")
        messagebox.showinfo("Modo Seguro", "Modo seguro activado.\n\n- Sin subtítulos\n- Sin thumbnails\n- Rate limiting activado\n\nEsto evita errores 429.")
            
    def clear_fields(self):
        """Limpiar todos los campos"""
        self.url_var.set("")
        self.progress_var.set(0)
        self.status_var.set("Listo para descargar")
        
        try:
            self.info_text.configure(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.configure(state=tk.DISABLED)
        except:
            pass
        
    def clear_logs(self):
        """Limpiar el log de actividad"""
        try:
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.configure(state=tk.DISABLED)
        except:
            pass
        
    def open_download_folder(self):
        """Abrir la carpeta de descargas"""
        import subprocess
        import platform
        
        path = self.output_path_var.get()
        if not os.path.exists(path):
            messagebox.showwarning("Advertencia", f"La carpeta no existe: {path}")
            return
            
        try:
            if platform.system() == "Windows":
                subprocess.Popen(['explorer', path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', path])
            else:  # Linux
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")
            
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """
Anime Downloader v1.0.0

Un downloader de anime simple y eficiente.

Características:
• Descarga de videos en múltiples calidades
• Modo seguro para evitar rate limiting
• Interfaz gráfica intuitiva
• Manejo de errores y reintentos
• Soporte opcional para subtítulos

Desarrollado con Python y Tkinter.

Tip: Usa el "Modo Seguro" para evitar 
errores 429 (Too Many Requests).
        """
        
        messagebox.showinfo("Acerca de Anime Downloader", about_text.strip())
        
    def run(self):
        """Ejecutar la aplicación"""
        self.log_message("Anime Downloader GUI iniciado", "INFO")
        self.log_message("Tip: Usa 'Modo Seguro' para evitar errores de rate limiting", "INFO")
        self.root.mainloop()

if __name__ == "__main__":
    app = AnimeDownloaderGUI()
    app.run()
