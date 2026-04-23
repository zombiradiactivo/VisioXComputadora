import customtkinter as ctk
import json
import os
from tkinter import filedialog, ttk
from PIL import Image

from core.ollama import clasificar_imagenes
from core.status import verificar_ollama
app = None

# --- Configuraciones Globales de Estilo Cyberpunk ---
PALETA = {
    "fondo": "#0a0a0a",       # Casi negro
    "gris_oscuro": "#161616", # Fondos de marcos
    "gris_medio": "#2d2d2d",  # Elementos secundarios
    "cian": "#00ffff",        # Color primario neón / Texto activo
    "cian_tenue": "#008b8b",  # Para bordes
    "magenta": "#ff00ff",     # Acentos / Errores / Botones críticos
    "amarillo": "#ffff00",    # Advertencias / Estado conectando
    "verde_neon": "#39ff14",  # Éxito / Conectado / Botón Ejecutar
    "texto": "#e0e0e0"        # Texto general
}

FUENTES = {
    "titulo": ("Bahnschrift Condensed", 28, "bold"),
    "subtitulo": ("Bahnschrift SemiLight", 16),
    "interfaz": ("Verdana", 11),
    "codigo": ("Courier New", 12),
    "boton": ("Verdana", 11, "bold")
}

ctk.set_appearance_mode("dark")
# No usamos tema por defecto para controlar nosotros cada color

class VisionXCyberpunk(ctk.CTk):
    def __init__(self):
        global app
        super().__init__()
        app = self
        self.title("VISION_X :: NEURAL_CLASSIFIER_v1.0")
        self.geometry("1400x800")
        self.minsize(1300, 750)
        self.configure(fg_color=PALETA["fondo"])

        # Datos (idéntico a tu lógica original)
        self.imagenes_seleccionadas = []
        self.categorias = ["gato", "perro", "pajaro", "auto", "comida", "persona", "flor", "desconocido"]
        self.resultados = []
        self.ollama_conectado = False

        # --- Layout Principal ---
        self.grid_columnconfigure(1, weight=1) # Columna derecha expandible
        self.grid_rowconfigure(1, weight=1)    # Contenedor principal expandible

        self.setup_header()
        self.setup_left_panel()
        self.setup_right_panel()

        self.after(100, lambda a=self: verificar_ollama(a, self.ip_entry.get()))


    # ===========================
    # UI SECTIONS setup
    # ===========================

    def setup_header(self):
        # Header con borde inferior cian
        self.header_frame = ctk.CTkFrame(self, fg_color=PALETA["gris_oscuro"], height=70, corner_radius=0, border_width=1, border_color=PALETA["cian_tenue"])
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_propagate(False)

        # -- Sección Izquierda: Conexión --
        self.conn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.conn_frame.pack(side="left", padx=20, fill="y")

        ctk.CTkLabel(self.conn_frame, text="CORE_IP:", font=FUENTES["codigo"], text_color=PALETA["cian"]).pack(side="left", padx=(0, 5))
        
        self.ip_entry = ctk.CTkEntry(self.conn_frame, placeholder_text="localhost", width=130, height=28, 
                                     font=FUENTES["codigo"], fg_color=PALETA["fondo"], border_color=PALETA["gris_medio"], text_color=PALETA["texto"])
        self.ip_entry.insert(0, "localhost")
        self.ip_entry.pack(side="left", padx=5)

        self.connect_btn = ctk.CTkButton(self.conn_frame, text="[ RECONNECT ]", width=100, height=28, 
                                        font=FUENTES["boton"], fg_color="transparent", border_width=1, border_color=PALETA["cian"], 
                                        text_color=PALETA["cian"], hover_color=PALETA["gris_medio"],
                                        command=self._protocolo_conexion)
        self.connect_btn.pack(side="left", padx=10)

        # -- Sección Central: Título con Efecto "Glow" --
        self.title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_container.pack(side="left", expand=True)

        # Efecto sombra/glow magenta detrás del título cian
        ctk.CTkLabel(self.title_container, text="VISION_X_COMPUTADORA", font=FUENTES["titulo"], text_color=PALETA["magenta"]).place(relx=0.51, rely=0.42, anchor="center")
        self.title_label = ctk.CTkLabel(self.title_container, text="VISION_X_COMPUTADORA", font=FUENTES["titulo"], text_color=PALETA["cian"])
        self.title_label.pack(pady=(5,0))

        self.status_label = ctk.CTkLabel(self.title_container, text="> INICIALIZANDO_PROTOCOLO...", text_color=PALETA["amarillo"], font=FUENTES["codigo"])
        self.status_label.pack()

    def setup_left_panel(self):
        # Panel izquierdo sin grid para usar pack interno
        self.left_column = ctk.CTkFrame(self, fg_color="transparent", width=320)
        self.left_column.grid(row=1, column=0, sticky="ns", padx=20, pady=20)
        self.left_column.pack_propagate(False)

        # Estilo común para los marcos de sección (Borde cian tenaz)
        estilo_seccion = {"fg_color": PALETA["gris_oscuro"], "corner_radius": 0, "border_width": 1, "border_color": PALETA["cian_tenue"]}

        # 1. Categorías
        cat_frame = ctk.CTkFrame(self.left_column, **estilo_seccion)
        cat_frame.pack(fill="x", pady=(0, 15))
        
        self._crear_subtitulo(cat_frame, " // CLASSIFICATION_TAGS")

        self.cat_btn_frame = ctk.CTkScrollableFrame(cat_frame, fg_color="transparent", height=100, orientation="horizontal")
        self.cat_btn_frame.pack(fill="x", padx=10, pady=5)
        self.actualizar_botones_categorias()

        entry_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.new_cat_entry = ctk.CTkEntry(entry_frame, placeholder_text="Añadir_tag...", height=32, 
                                          font=FUENTES["interfaz"], fg_color=PALETA["fondo"], border_color=PALETA["gris_medio"])
        self.new_cat_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(entry_frame, text="[ + ]", width=35, height=32, font=FUENTES["boton"],
                      fg_color=PALETA["cian"], text_color=PALETA["fondo"], hover_color="#00cccc",
                      command=self.agregar_categoria).pack(side="right")

        # 2. Imágenes
        img_frame = ctk.CTkFrame(self.left_column, **estilo_seccion)
        img_frame.pack(fill="both", expand=True, pady=(0, 15))

        self._crear_subtitulo(img_frame, " // INPUT_BUFFER")

        action_frame = ctk.CTkFrame(img_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=5)

        # Botones estilo outline
        btn_style = {"font": FUENTES["boton"], "fg_color": "transparent", "border_width": 1, "height": 30}
        
        ctk.CTkButton(action_frame, text="CARGAR_DATA", border_color=PALETA["cian"], text_color=PALETA["cian"],
                  hover_color=PALETA["gris_medio"], **btn_style,
                  command=self.seleccionar_imagenes).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(action_frame, text="PURGAR", border_color=PALETA["magenta"], text_color=PALETA["magenta"],
                  hover_color=PALETA["gris_medio"], **btn_style,
                  command=self.limpiar_imagenes).pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Lista de imágenes (reemplazando Canvas por CTkScrollableFrame moderno)
        self.img_list_container = ctk.CTkScrollableFrame(img_frame, fg_color=PALETA["fondo"], corner_radius=0, 
                                                          scrollbar_fg_color=PALETA["gris_oscuro"], scrollbar_button_color=PALETA["gris_medio"],
                                                          scrollbar_button_hover_color=PALETA["cian_tenue"])
        self.img_list_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.empty_label = ctk.CTkLabel(self.img_list_container, text="> BUFFER_VACÍO.\nESPERANDO_INPUT...", text_color=PALETA["gris_medio"], font=FUENTES["codigo"])
        self.empty_label.pack(expand=True, pady=50)

        # 3. Botón Ejecutar (GRANDE y NEÓN)
        self.classify_button = ctk.CTkButton(self.left_column, text="RUN_NEURAL_NET.exe", 
                                            fg_color=PALETA["verde_neon"], text_color="#000000",
                                            font=("Bahnschrift Condensed", 18, "bold"), height=50, corner_radius=0,
                                            hover_color="#32cd32",
                                            command=self._protocolo_clasificacion)
        self.classify_button.pack(fill="x")

    def setup_right_panel(self):
        # Panel derecho con borde cian
        self.right_column = ctk.CTkFrame(self, fg_color=PALETA["gris_oscuro"], corner_radius=0, border_width=1, border_color=PALETA["cian_tenue"])
        self.right_column.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=20)

        # Pestañas falsas (Fake Tabs) estilo Cyberpunk
        tab_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        tab_frame.pack(fill="x", padx=15, pady=(10, 0))

        btn_tab_style = {"font": FUENTES["boton"], "height": 30, "corner_radius": 0, "border_width": 1}
        
        self.btn_resultados = ctk.CTkButton(tab_frame, text="[ VISUAL_OUTPUT ]", fg_color=PALETA["gris_medio"], border_color=PALETA["cian"], text_color=PALETA["cian"],
                                          hover_color=PALETA["fondo"], **btn_tab_style, command=lambda: self.cambiar_tabla("resultados"))
        self.btn_resultados.pack(side="left", padx=(0, 2))
        
        self.btn_json = ctk.CTkButton(tab_frame, text="DATA.JSON", fg_color="transparent", border_color=PALETA["gris_medio"], text_color=PALETA["texto"],
                                   hover_color=PALETA["gris_medio"], **btn_tab_style, command=lambda: self.cambiar_tabla("json"))
        self.btn_json.pack(side="left", padx=2)
        
        self.btn_txt = ctk.CTkButton(tab_frame, text="LOG.TXT", fg_color="transparent", border_color=PALETA["gris_medio"], text_color=PALETA["texto"],
                                   hover_color=PALETA["gris_medio"], **btn_tab_style, command=lambda: self.cambiar_tabla("txt"))
        self.btn_txt.pack(side="left", padx=2)

        # Contenedor de texto
        self.results_view = ctk.CTkFrame(self.right_column, fg_color=PALETA["fondo"], corner_radius=0, border_width=1, border_color=PALETA["gris_medio"])
        self.results_view.pack(fill="both", expand=True, padx=15, pady=15)

        self.result_text = ctk.CTkTextbox(self.results_view, fg_color="transparent", text_color=PALETA["verde_neon"], 
                                         font=FUENTES["codigo"], wrap="none", corner_radius=0)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.result_text.insert("0.0", "> Esperando ejecución de red neuronal...\n> Matriz de resultados lista.")

        self.tabla_actual = "resultados"

    # ===========================
    # HELPER methods
    # ===========================

    def _crear_subtitulo(self, master, texto):
        # Subtítulo con barra lateral magenta
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(anchor="w", padx=10, pady=(8, 5))
        
        ctk.CTkFrame(frame, width=4, height=20, fg_color=PALETA["magenta"], corner_radius=0).pack(side="left")
        ctk.CTkLabel(frame, text=texto, font=FUENTES["subtitulo"], text_color=PALETA["texto"]).pack(side="left", padx=5)

    # ===========================
    # LOGIC (Adapted from original)
    # ===========================

    # --- Lógica de Backend (Reemplazar con tus importaciones core) ---
    def _simular_conexion(self):
        # Simula lo que haría verificar_ollama
        self.ollama_conectado = True
        self.status_label.configure(text="● CORE_NET::ONLINE", text_color=PALETA["verde_neon"])
        self._log_sistema("Conexión establecida con Ollama en localhost.")

    def _protocolo_conexion(self):
        self.status_label.configure(text="> RECONECTANDO...", text_color=PALETA["amarillo"])
        verificar_ollama(app, self.ip_entry.get())

    def _protocolo_clasificacion(self):
        if not self.imagenes_seleccionadas:
            self._log_sistema("ERROR: No hay input data en el buffer.", PALETA["magenta"])
            return
        self._log_sistema("INICIANDO CLASIFICACIÓN NEURAL...", PALETA["amarillo"])
        self._log_sistema(clasificar_imagenes(self, self.ip_entry.get()))
        # Y en el callback de esa función, rellenarías self.resultados y llamarías a self.mostrar_resultados()
        
        # Simulación de resultados para ver estética
        # self.after(2000, self._simular_resultados)

    def _log_sistema(self, msg, color=None):
        color = color if color else PALETA["texto"]
        # Implementación simple de log en la consola de resultados
        self.result_text.insert("end", f"\n[SYS_LOG] > {msg}")
        self.result_text.see("end")

    # def _simular_resultados(self):
    #     # Solo para testing visual
    #     self.resultados = []
    #     for img in self.imagenes_seleccionadas:
    #         import random
    #         cat = random.choice(self.categorias)
    #         conf = random.random()
    #         self.resultados.append({
    #             "imagen": img,
    #             "resultado": {"categoria": cat, "confianza": conf, "razones": "Análisis sintáctico de patrones visuales completado. Coincidencia de características detectada mediante modelo LLaVA subyacente simulado."}
    #         })
    #     self.mostrar_resultados()
    #     self._log_sistema("Clasificación completada.", PALETA["verde_neon"])

    # --- Lógica de GUI pura (Original modificada) ---

    def actualizar_botones_categorias(self):
        for widget in self.cat_btn_frame.winfo_children():
            widget.destroy()
        for cat in self.categorias:
            # Botones de categoría estilo outline cian
            ctk.CTkButton(self.cat_btn_frame, text=f"{cat.upper()} [x]", width=70, height=24,
                        font=("Verdana", 9), fg_color="transparent", border_width=1, border_color=PALETA["cian_tenue"], text_color=PALETA["cian"],
                        hover_color=PALETA["gris_medio"], corner_radius=10,
                        command=lambda c=cat: self.eliminar_categoria(c)).pack(side="left", padx=3)

    def agregar_categoria(self):
        nueva = self.new_cat_entry.get().strip().lower()
        if nueva and nueva not in self.categorias:
            self.categorias.append(nueva)
            self.new_cat_entry.delete(0, "end")
            self.actualizar_botones_categorias()

    def eliminar_categoria(self, cat):
        if cat in self.categorias:
            self.categorias.remove(cat)
            self.actualizar_botones_categorias()

    def seleccionar_imagenes(self):
        rutas = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")])
        if rutas:
            nuevas = [r for r in rutas if r not in self.imagenes_seleccionadas]
            self.imagenes_seleccionadas.extend(nuevas)
            self.mostrar_lista_imagenes()

    def mostrar_lista_imagenes(self):
        for widget in self.img_list_container.winfo_children():
            widget.destroy()

        if not self.imagenes_seleccionadas:
            self.empty_label = ctk.CTkLabel(self.img_list_container, text="> BUFFER_VACÍO.\nESPERANDO_INPUT...", text_color=PALETA["gris_medio"], font=FUENTES["codigo"])
            self.empty_label.pack(expand=True, pady=50)
        else:
            for ruta in self.imagenes_seleccionadas:
                self._crear_thumbnail_cyberpunk(ruta)

    def _crear_thumbnail_cyberpunk(self, ruta):
        nombre = os.path.basename(ruta)
        ext = os.path.splitext(nombre)[1].upper()
        try:
            img = Image.open(ruta)
            thumb = ctk.CTkImage(img, size=(60, 60))
        except:
            thumb = None

        # Frame de ítem con fondo gris oscuro
        frame = ctk.CTkFrame(self.img_list_container, fg_color=PALETA["gris_oscuro"], corner_radius=0, border_width=1, border_color=PALETA["gris_medio"])
        frame.pack(fill="x", pady=2, padx=2)

        if thumb:
            preview = ctk.CTkLabel(frame, image=thumb, text="", width=60, height=60)
            preview.pack(side="left", padx=5, pady=5)
        else:
            # Placeholder si no carga imagen
            preview = ctk.CTkLabel(frame, text=ext, width=60, height=60, font=FUENTES["codigo"], fg_color=PALETA["fondo"], text_color=PALETA["magenta"])
            preview.pack(side="left", padx=5, pady=5)

        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=5)

        # Cortar nombre si es muy largo
        nombre_show = (nombre[:20] + '..') if len(nombre) > 22 else nombre
        ctk.CTkLabel(info_frame, text=nombre_show, text_color=PALETA["texto"], font=("Verdana", 10, "bold"), anchor="w").pack(fill="x", padx=5)
        ctk.CTkLabel(info_frame, text=f"Type: {ext}", text_color=PALETA["cian_tenue"], font=FUENTES["codigo"], anchor="w").pack(fill="x", padx=5)

        # Botón remover magenta
        remove_btn = ctk.CTkButton(frame, text="✕", width=25, height=25, fg_color="transparent",
                                text_color=PALETA["magenta"], hover_color=PALETA["gris_medio"], font=("Verdana", 12, "bold"), corner_radius=0,
                                command=lambda r=ruta: self._deseleccionar_imagen(r))
        remove_btn.pack(side="right", padx=5)

    def _deseleccionar_imagen(self, ruta):
        if ruta in self.imagenes_seleccionadas:
            self.imagenes_seleccionadas.remove(ruta)
            self.mostrar_lista_imagenes()

    def limpiar_imagenes(self):
        self.imagenes_seleccionadas = []
        self.mostrar_lista_imagenes()

    def cambiar_tabla(self, tipo):
        self.tabla_actual = tipo
        
        # Actualizar estilo de pestañas (outline cian para activa, gris para inactivas)
        tabs = [
            (self.btn_resultados, "resultados", "[ VISUAL_OUTPUT ]"),
            (self.btn_json, "json", "DATA.JSON"),
            (self.btn_txt, "txt", "LOG.TXT")
        ]
        
        for btn, t_tipo, texto_orig in tabs:
            if t_tipo == tipo:
                btn.configure(fg_color=PALETA["gris_medio"], border_color=PALETA["cian"], text_color=PALETA["cian"])
            else:
                btn.configure(fg_color="transparent", border_color=PALETA["gris_medio"], text_color=PALETA["texto"])
                
        self.mostrar_resultados()

    def mostrar_resultados(self):
        self.result_text.delete("0.0", "end")
        
        # Color de texto por defecto para consola
        self.result_text.configure(text_color=PALETA["verde_neon"])

        if not self.resultados:
            self.result_text.insert("0.0", "> BUFFER_RESULTADOS_VACÍO.\n> Ejecute RUN_NEURAL_NET.exe para procesar.")
            return

        if self.tabla_actual == "resultados":
            self.result_text.insert("end", f"// --- NEURAL_NET_OUTPUT_STREAM ---\n\n")
            for r in self.resultados:
                nombre = os.path.basename(r["imagen"])
                cat = r["resultado"].get("categoria", "desconocido").upper()
                conf = r["resultado"].get("confianza", 0)
                razones = r["resultado"].get("razones", "")
                
                # Formateo visual Cyberpunk
                self.result_text.insert("end", f"ID_ARCHIVO: ", PALETA["texto"])
                self.result_text.insert("end", f"{nombre}\n", PALETA["cian"])
                
                # Color basado en confianza (opcional, aquí cian por defecto)
                self.result_text.insert("end", f"└─> DETECTADO: ", PALETA["texto"])
                self.result_text.insert("end", f"[{cat}]", PALETA["magenta"])
                self.result_text.insert("end", f" - CONFIDENCIA: ", PALETA["texto"])
                self.result_text.insert("end", f"{conf:.1%}\n", PALETA["verde_neon"])
                
                self.result_text.insert("end", f"└─> ANÁLISIS: ", PALETA["texto"])
                self.result_text.insert("end", f"{razones}\n", "#aaaaaa")
                self.result_text.insert("end", f"{'-'*60}\n\n", PALETA["gris_medio"])

        elif self.tabla_actual == "json":
            self.result_text.configure(text_color="#ce9178") # Color JSON típico
            self.result_text.insert("0.0", json.dumps(self.resultados, indent=2, ensure_ascii=False))
        
        else: # TXT
            self.result_text.configure(text_color=PALETA["texto"])
            self.result_text.insert("end", f"// RAW_LOG_DUMP - {os.name.upper()}\n\n")
            for r in self.resultados:
                nombre = os.path.basename(r["imagen"])
                cat = r["resultado"].get("categoria", "desconocido")
                conf = r["resultado"].get("confianza", 0)
                self.result_text.insert("end", f"{nombre} | TAG:{cat} | CONF:{conf:.4f}\n")

        self.result_text.see("0.0") # Volver arriba


if __name__ == "__main__":
    app = VisionXCyberpunk()
    app.mainloop()