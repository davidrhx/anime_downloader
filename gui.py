"""
Anime Downloader - Interfaz Gráfica con Tkinter
GUI simple y funcional para el downloader
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import logging
from urllib.parse import urlparse

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
        
        # Ruta de descarga
        ttk.Label(config_frame, text="Destino:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        path_frame = ttk.Frame(config_frame)
        path_frame.grid(row=0, column=3, sticky=(tk.W, tk.E))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.output_path_var, width=30)
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
            command=self.start_download,
            style="Accent.TButton"
        )
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.cancel_download,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Limpiar", command=self.clear_fields).pack(side=tk.LEFT)
        
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
        tools_menu.add_command(label="Configuración", command=self.show_settings)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
    def setup_logging(self):
        """Configurar logging para mostrar en la GUI"""
        # Handler personalizado para mostrar logs en la GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state=tk.NORMAL)
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.configure(state=tk.DISABLED)
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        # Configurar el handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
        gui_handler.setFormatter(formatter)
        
        # Agregar handler al logger principal
        logging.getLogger().addHandler(gui_handler)
        
    def log_message(self, message, level="INFO"):
        """Agregar mensaje al log de la GUI"""
        def append():
            self.log_text.configure(state=tk.NORMAL)
            timestamp = tk.datetime.now().strftime('%H:%M:%S')
            formatted_message = f"[{timestamp}] {level}: {message}\n"
            self.log_text.insert(tk.END, formatted_message)
            self.log_text.configure(state=tk.DISABLED)
            self.log_text.see(tk.END)
        
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
            try:
                # Crear downloader temporal
                temp_downloader = AnimeDownloader(
                    output_path=self.output_path_var.get(),
                    quality=self.quality_var.get()
                )
                
                info = temp_downloader.get_video_info(url)
                
                if info:
                    # Actualizar información en la GUI
                    self.root.after(0, lambda: self.display_video_info(info))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", "No se pudo obtener información del video"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Error obteniendo información: {str(e)}"
                ))
            finally:
                self.root.after(0, lambda: self.download_button.configure(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_var.set("Listo para descargar"))
        
        # Ejecutar en hilo separado
        threading.Thread(target=fetch_info, daemon=True).start()
        
    def display_video_info(self, info):
        """Mostrar información del video en la GUI"""
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
            try:
                success = self.downloader.download_episode(url, self.progress_callback)
                
                if success:
                    self.root.after(0, lambda: self.download_complete(True))
                else:
                    self.root.after(0, lambda: self.download_complete(False))
                    
            except Exception as e:
                self.root.after(0, lambda: self.download_error(str(e)))
        
        # Iniciar descarga en hilo separado
        self.download_thread = threading.Thread(target=download_worker, daemon=True)
        self.download_thread.start()
        
    def progress_callback(self, data):
        """Callback para actualizar progreso de descarga"""
        def update_ui():
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
        
        self.root.after(0, update_ui)
        
    def download_complete(self, success):
        """Callback cuando la descarga se completa"""
        self.is_downloading = False
        self.download_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        
        if success:
            self.status_var.set("✅ Descarga completada exitosamente")
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
            
    def clear_fields(self):
        """Limpiar todos los campos"""
        self.url_var.set("")
        self.progress_var.set(0)
        self.status_var.set("Listo para descargar")
        
        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.configure(state=tk.DISABLED)
        
    def clear_logs(self):
        """Limpiar el log de actividad"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
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
            
    def show_settings(self):
        """Mostrar ventana de configuración"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configuración")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Centrar la ventana
        settings_window.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab de Descarga
        download_frame = ttk.Frame(notebook, padding="10")
        notebook.add(download_frame, text="Descarga")
        
        ttk.Label(download_frame, text="Reintentos máximos:").grid(row=0, column=0, sticky=tk.W, pady=5)
        retries_var = tk.StringVar(value=str(Config.MAX_RETRIES))
        ttk.Spinbox(download_frame, from_=1, to=10, textvariable=retries_var, width=10).grid(row=0, column=1, pady=5)
        
        ttk.Label(download_frame, text="Descargas simultáneas:").grid(row=1, column=0, sticky=tk.W, pady=5)
        concurrent_var = tk.StringVar(value=str(Config.CONCURRENT_DOWNLOADS))
        ttk.Spinbox(download_frame, from_=1, to=5, textvariable=concurrent_var, width=10).grid(row=1, column=1, pady=5)
        
        # Tab de Subtítulos
        subs_frame = ttk.Frame(notebook, padding="10")
        notebook.add(subs_frame, text="Subtítulos")
        
        download_subs_var = tk.BooleanVar(value=Config.DOWNLOAD_SUBTITLES)
        ttk.Checkbutton(subs_frame, text="Descargar subtítulos", variable=download_subs_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        embed_subs_var = tk.BooleanVar(value=Config.EMBED_SUBTITLES)
        ttk.Checkbutton(subs_frame, text="Incrustar subtítulos", variable=embed_subs_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Botones
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_settings():
            try:
                Config.MAX_RETRIES = int(retries_var.get())
                Config.CONCURRENT_DOWNLOADS = int(concurrent_var.get())
                Config.DOWNLOAD_SUBTITLES = download_subs_var.get()
                Config.EMBED_SUBTITLES = embed_subs_var.get()
                messagebox.showinfo("Éxito", "Configuración guardada")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Valores inválidos en la configuración")
        
        ttk.Button(button_frame, text="Guardar", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancelar", command=settings_window.destroy).pack(side=tk.RIGHT)
        
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """
Anime Downloader v1.0.0

Un downloader de anime simple y eficiente.

Características:
• Descarga de videos en múltiples calidades
• Soporte para subtítulos
• Interfaz gráfica intuitiva
• Descargas por lotes
• Manejo de errores y reintentos

Desarrollado con Python y Tkinter.
        """
        
        messagebox.showinfo("Acerca de Anime Downloader", about_text.strip())
        
    def run(self):
        """Ejecutar la aplicación"""
        self.log_message("Anime Downloader iniciado", "INFO")
        self.root.mainloop()

if __name__ == "__main__":
    app = AnimeDownloaderGUI()
    app.run()
        
