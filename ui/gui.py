import customtkinter as ctk
import json
import os
import sys
from tkinter import filedialog
from tkinter import ttk
from PIL import Image
from customtkinter import CTkImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ollama import clasificar_imagenes
from core.status import verificar_ollama
app = None


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VisionXApp(ctk.CTk):
    def __init__(self):
        global app
        super().__init__()
        app = self
        self.title("VisionXComputadora - Clasificador")
        self.geometry("1300x750")
        self.minsize(1300, 750)
        self.configure(fg_color="#1e1e1e")

        self.imagenes_seleccionadas = []
        self.categorias = ["gato", "perro", "pajaro", "auto", "comida", "persona", "flor", "desconocido"]
        self.resultados = []
        self.ollama_conectado = False

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=10)

        self.conn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.conn_frame.pack(side="left")

        self.ip_entry = ctk.CTkEntry(self.conn_frame, placeholder_text="localhost", width=150, height=30)
        self.ip_entry.insert(0, "localhost")
        self.ip_entry.pack(side="left", padx=(0, 5))

        self.connect_btn = ctk.CTkButton(self.conn_frame, text="Conectar", width=80, height=30, 
                                        fg_color="#1f538d", hover_color="#14375e",
                                        command=lambda a=self: verificar_ollama(a, self.ip_entry.get()))
        self.connect_btn.pack(side="left")

        self.title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_container.pack(expand=True)

        self.title_label = ctk.CTkLabel(self.title_container, text="VisionXComputadora", font=("Segoe UI", 24, "bold"))
        self.title_label.pack()

        self.status_label = ctk.CTkLabel(self.title_container, text="● Conectando...", text_color="#ff9800", font=("Segoe UI", 12))
        self.status_label.pack()

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.left_column = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_column.pack(side="left", fill="both", expand=False, padx=(0, 10))

        self.setup_categories_section()
        self.setup_images_section()

        self.classify_button = ctk.CTkButton(self.left_column, text="CLASIFICAR", 
                                            fg_color="#4caf50", hover_color="#388e3c",
                                            font=("Segoe UI", 14, "bold"), height=45,
                                            command=lambda a=self: clasificar_imagenes(a, self.ip_entry.get()))
        self.classify_button.pack(fill="x", pady=(15, 0))

        self.right_column = ctk.CTkFrame(self.main_container, fg_color="#2b2b2b", corner_radius=10)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.setup_results_section()
        self.after(100, lambda a=self: verificar_ollama(a, self.ip_entry.get()))

    def setup_categories_section(self):
        cat_frame = ctk.CTkFrame(self.left_column, fg_color="#2b2b2b", corner_radius=10)
        cat_frame.pack(fill="x", pady=(0, 10), ipady=5)

        ctk.CTkLabel(cat_frame, text="Categorías", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=5)

        self.cat_btn_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        self.cat_btn_frame.pack(fill="x", padx=15)
        self.actualizar_botones_categorias()

        entry_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=10)
        
        self.new_cat_entry = ctk.CTkEntry(entry_frame, placeholder_text="Nueva categoría", height=35)
        self.new_cat_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(entry_frame, text="+", width=35, height=35, fg_color="#4caf50",
                    command=self.agregar_categoria).pack(side="right")

        self.cat_display = ctk.CTkTextbox(cat_frame, height=60, fg_color="#1a1a1a")
        self.cat_display.pack(fill="x", padx=15, pady=(0, 10))
        self.cat_display.insert("0.0", ", ".join(self.categorias))

    def actualizar_botones_categorias(self):
        for widget in self.cat_btn_frame.winfo_children():
            widget.destroy()
        for cat in self.categorias:
            ctk.CTkButton(self.cat_btn_frame, text=cat, width=80, height=28,
                        command=lambda c=cat: self.eliminar_categoria(c)).pack(side="left", padx=2)

    def agregar_categoria(self):
        nueva = self.new_cat_entry.get().strip().lower()
        if nueva and nueva not in self.categorias:
            self.categorias.append(nueva)
            self.new_cat_entry.delete(0, "end")
            self.actualizar_botones_categorias()
            self.cat_display.delete("0.0", "end")
            self.cat_display.insert("0.0", ", ".join(self.categorias))

    def eliminar_categoria(self, cat):
        if cat in self.categorias:
            self.categorias.remove(cat)
            self.actualizar_botones_categorias()
            self.cat_display.delete("0.0", "end")
            self.cat_display.insert("0.0", ", ".join(self.categorias))

    def setup_images_section(self):
        img_frame = ctk.CTkFrame(self.left_column, fg_color="#2b2b2b", corner_radius=10)
        img_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(img_frame, text="Imágenes", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=5)

        action_frame = ctk.CTkFrame(img_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(action_frame, text="Seleccionar", fg_color="#2196f3",
                  command=self.seleccionar_imagenes).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(action_frame, text="Limpiar", fg_color="#f44336",
                  command=self.limpiar_imagenes).pack(side="right", fill="x", expand=True, padx=(5, 0))

        img_list_canvas = ctk.CTkCanvas(img_frame, bg="#1a1a1a", bd=0, highlightthickness=0)
        img_list_canvas.pack(fill="both", expand=True, padx=15, pady=15)

        self.img_list_scroll = ttk.Scrollbar(img_list_canvas, orient="vertical", command=img_list_canvas.yview)
        self.img_list_scroll.pack(side="right", fill="y", )
        img_list_canvas.configure(yscrollcommand=self.img_list_scroll.set)

        self.img_list_container = ctk.CTkFrame(img_list_canvas, fg_color="transparent")
        self.img_list_window = img_list_canvas.create_window((0, 0), window=self.img_list_container, anchor="nw")

        self.img_list_container.bind("<Configure>", lambda e: img_list_canvas.configure(scrollregion=img_list_canvas.bbox("all")))
        img_list_canvas.bind("<Configure>", lambda e: img_list_canvas.itemconfig(self.img_list_window, width=e.width))
        img_list_canvas.bind_all("<MouseWheel>", lambda e: img_list_canvas.yview_scroll(int(-e.delta/120), "units"))
        img_list_canvas.bind_all("<Button-4>", lambda e: img_list_canvas.yview_scroll(-3, "units"))
        img_list_canvas.bind_all("<Button-5>", lambda e: img_list_canvas.yview_scroll(3, "units"))

        self.empty_label = ctk.CTkLabel(self.img_list_container, text="No hay imágenes seleccionadas", text_color="gray")
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self.thumbnails = {}

    def seleccionar_imagenes(self):
        rutas = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")])
        if rutas:
            nuevas = [r for r in rutas if r not in self.imagenes_seleccionadas]
            self.imagenes_seleccionadas.extend(nuevas)
            self.mostrar_lista_imagenes()

    def mostrar_lista_imagenes(self):
        for widget in self.img_list_container.winfo_children():
            widget.destroy()
        self.thumbnails.clear()

        if not self.imagenes_seleccionadas:
            self.empty_label = ctk.CTkLabel(self.img_list_container, text="No hay imágenes seleccionadas", text_color="gray")
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            for ruta in self.imagenes_seleccionadas:
                self._crear_thumbnail(ruta)

    def _crear_thumbnail(self, ruta):
        nombre = os.path.basename(ruta)
        try:
            img = Image.open(ruta)
            img_w, img_h = img.size
            thumb = CTkImage(img, size=(80, 80))
            tamaño = f"{img_w}x{img_h}"
        except:
            thumb = None
            tamaño = "?"

        frame = ctk.CTkFrame(self.img_list_container, fg_color="#2a2a2a", corner_radius=8)
        frame.pack(fill="x", pady=3)

        if thumb:
            preview = ctk.CTkLabel(frame, image=thumb, text="", width=90, height=90)
            preview.image = thumb # type: ignore
        else:
            preview = ctk.CTkLabel(frame, text="?", width=90, height=90, font=("Segoe UI", 24))
        preview.pack(side="left", padx=5, pady=5)

        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=5)

        nombre_lbl = ctk.CTkLabel(info_frame, text=nombre, text_color="white", font=("Segoe UI", 11, "bold"), anchor="w")
        nombre_lbl.pack(fill="x", padx=5)

        size_lbl = ctk.CTkLabel(info_frame, text=tamaño, text_color="gray", font=("Segoe UI", 9), anchor="w")
        size_lbl.pack(fill="x", padx=5)

        remove_btn = ctk.CTkButton(frame, text="✕", width=30, height=30, fg_color="#f44336",
                                hover_color="#d32f2f", font=("Segoe UI", 14, "bold"),
                                command=lambda r=ruta: self._deseleccionar_imagen(r))
        remove_btn.pack(side="right", padx=5)

        self.thumbnails[ruta] = frame

    def _deseleccionar_imagen(self, ruta):
        self.imagenes_seleccionadas.remove(ruta)
        self.mostrar_lista_imagenes()

    def limpiar_imagenes(self):
        self.imagenes_seleccionadas = []
        self.mostrar_lista_imagenes()

    def setup_results_section(self):
        tab_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        tab_frame.pack(fill="x", padx=15, pady=10)

        self.btn_resultados = ctk.CTkButton(tab_frame, text="Resultados", width=80, height=25, fg_color="#2196f3",
                                          command=lambda: self.cambiar_tabla("resultados"))
        self.btn_resultados.pack(side="left", padx=2)
        self.btn_json = ctk.CTkButton(tab_frame, text="JSON", width=60, height=25, fg_color="#444444",
                                   command=lambda: self.cambiar_tabla("json"))
        self.btn_json.pack(side="left", padx=2)
        self.btn_txt = ctk.CTkButton(tab_frame, text="TXT", width=60, height=25, fg_color="#444444",
                                   command=lambda: self.cambiar_tabla("txt"))
        self.btn_txt.pack(side="left", padx=2)

        self.results_view = ctk.CTkFrame(self.right_column, fg_color="#1a1a1a")
        self.results_view.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.result_text = ctk.CTkTextbox(self.results_view, fg_color="#1a1a1a", text_color="white", font=("Consolas", 11))
        self.result_text.pack(fill="both", expand=True)
        self.result_text.insert("0.0", "Esperando clasificación...")

        self.tabla_actual = "resultados"

    def cambiar_tabla(self, tipo):
        self.tabla_actual = tipo
        self.btn_resultados.configure(fg_color="#2196f3" if tipo == "resultados" else "#444444")
        self.btn_json.configure(fg_color="#2196f3" if tipo == "json" else "#444444")
        self.btn_txt.configure(fg_color="#2196f3" if tipo == "txt" else "#444444")
        self.mostrar_resultados()

    def mostrar_resultados(self):
        self.result_text.delete("0.0", "end")
        if not self.resultados:
            self.result_text.insert("0.0", "Sin resultados aún")
            return

        if self.tabla_actual == "resultados":
            for r in self.resultados:
                nombre = os.path.basename(r["imagen"])
                cat = r["resultado"].get("categoria", "desconocido")
                conf = r["resultado"].get("confianza", 0)
                razones = r["resultado"].get("razones", "")[:500]
                self.result_text.insert("end", f"📷 {nombre}\n   → {cat} ({conf:.1%})\n   {razones}\n\n")
        elif self.tabla_actual == "json":
            self.result_text.insert("0.0", json.dumps(self.resultados, indent=2, ensure_ascii=False))
        else:
            for r in self.resultados:
                nombre = os.path.basename(r["imagen"])
                cat = r["resultado"].get("categoria", "desconocido")
                conf = r["resultado"].get("confianza", 0)
                self.result_text.insert("end", f"{nombre}: {cat} ({conf:.1%})\n")


if __name__ == "__main__":
    app = VisionXApp()
    app.mainloop()
