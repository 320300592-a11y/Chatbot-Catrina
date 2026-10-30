import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from main import Chatbot
from config import BIENVENIDA

# ───────────────────────── Paleta ─────────────────────────
BG_VENTANA = "#1E1226"
BG_HEADER = "#32163B"
BG_CHAT = "#150C1D"
BG_CAJA = "#2B1836"
BORDE = "#4A2859"
NARANJA = "#FB8500"
AMARILLO = "#FFB703"
LILA = "#E0AAFF"
MORADO = "#9D4EDD"
TEXTO = "#F4EEF7"
APAGADO = "#8F7BA3"

BURBUJA_BOT_BG = "#2D1B3D"
BURBUJA_BOT_BORDE = "#5A2D75"
BURBUJA_USER_BG = "#FB8500"
BURBUJA_USER_FG = "#1A0B00"

FUENTE = "Segoe UI"
FUENTE_EMOJI = "Segoe UI Emoji"

PLACEHOLDER = "Ej: ¿Qué lleva la ofrenda de perros? o ¿Qué es el Mictlán?..."

# (texto del botón, pregunta que se envía)
EJEMPLOS = [
    ("🌼 La Catrina", "¿Qué es la Catrina?"),
    ("🕯 La ofrenda", "¿Qué lleva la ofrenda?"),
    ("📅 Fechas", "¿Cuándo se celebra?"),
    ("🐶 Mascotas", "¿Qué le pongo a mi perro en la ofrenda?"),
    ("🍞 Comida", "¿Qué comen en Día de Muertos?"),
    ("🎃 Halloween", "¿Cuáles son las diferencias entre Halloween y Día de Muertos?"),
]


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Catrina Bot 💀🌼")
        self.root.geometry("680x780")
        self.root.minsize(520, 620)
        self.root.configure(bg=BG_VENTANA)

        self.bot = Chatbot()

        self.burbujas = []          # etiquetas de burbujas (para ajustar el ancho)
        self.esperando = False      # True mientras el bot "escribe"
        self.fila_escribiendo = None
        self._anim_id = None
        self._puntos = 0
        self._token = 0             # invalida respuestas pendientes al limpiar
        self._placeholder_activo = False

        self._configurar_estilos()
        self._crear_interfaz()
        self._mostrar_mensaje_bot(BIENVENIDA)

    # ───────────────────────── Estilos ─────────────────────────
    def _configurar_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure(
            "Muerto.Vertical.TScrollbar",
            background=BORDE,
            troughcolor=BG_CHAT,
            bordercolor=BG_CHAT,
            lightcolor=BORDE,
            darkcolor=BORDE,
            arrowcolor=BG_CHAT,
            relief="flat",
            width=10,
        )
        estilo.map(
            "Muerto.Vertical.TScrollbar",
            background=[("active", MORADO), ("pressed", NARANJA)],
        )

    # ───────────────────────── Interfaz ─────────────────────────
    def _crear_interfaz(self):
        self._crear_cabecera()
        self._crear_ejemplos()
        self._crear_area_chat()
        self._crear_entrada()

    def _crear_cabecera(self):
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill=tk.X)

        contenido = tk.Frame(header, bg=BG_HEADER, padx=16, pady=12)
        contenido.pack(fill=tk.X)

        avatar = tk.Label(
            contenido, text="💀", font=(FUENTE_EMOJI, 24),
            bg=BORDE, fg=TEXTO, width=2, pady=2,
        )
        avatar.pack(side=tk.LEFT, padx=(0, 12))

        textos = tk.Frame(contenido, bg=BG_HEADER)
        textos.pack(side=tk.LEFT)

        tk.Label(
            textos, text="Catrina Bot", font=(FUENTE, 16, "bold"),
            fg=AMARILLO, bg=BG_HEADER, anchor="w",
        ).pack(anchor="w")

        tk.Label(
            textos, text="● En línea  ·  Tradiciones de Día de Muertos",
            font=(FUENTE, 9), fg="#7BE495", bg=BG_HEADER, anchor="w",
        ).pack(anchor="w")

        tk.Label(
            contenido, text="🌼", font=(FUENTE_EMOJI, 20),
            bg=BG_HEADER,
        ).pack(side=tk.RIGHT)

        # Línea decorativa color cempasúchil
        tk.Frame(header, bg=NARANJA, height=3).pack(fill=tk.X)

    def _crear_ejemplos(self):
        marco = tk.Frame(self.root, bg=BG_VENTANA, padx=14, pady=10)
        marco.pack(fill=tk.X)

        tk.Label(
            marco, text="💡 Prueba con una de estas preguntas:",
            font=(FUENTE, 9), fg=LILA, bg=BG_VENTANA, anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        for i, (texto_boton, pregunta) in enumerate(EJEMPLOS):
            btn = tk.Button(
                marco,
                text=texto_boton,
                font=(FUENTE, 9, "bold"),
                bg=BG_CAJA,
                fg=AMARILLO,
                activebackground=NARANJA,
                activeforeground="#1A0B00",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=7,
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=BORDE,
                command=lambda p=pregunta: self.enviar_mensaje(p),
            )
            btn.grid(row=1 + i // 3, column=i % 3, sticky="ew", padx=3, pady=3)
            self._hover(btn, BG_CAJA, "#4A2859")

        for col in range(3):
            marco.columnconfigure(col, weight=1)

    def _crear_area_chat(self):
        contenedor = tk.Frame(self.root, bg=BG_CHAT)
        contenedor.pack(fill=tk.BOTH, expand=True, padx=14, pady=(2, 0))

        self.canvas = tk.Canvas(contenedor, bg=BG_CHAT, highlightthickness=0, bd=0)
        scroll = ttk.Scrollbar(
            contenedor, orient="vertical", command=self.canvas.yview,
            style="Muerto.Vertical.TScrollbar",
        )
        self.canvas.configure(yscrollcommand=scroll.set)

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_inner = tk.Frame(self.canvas, bg=BG_CHAT)
        self.ventana_chat = self.canvas.create_window(
            (0, 0), window=self.chat_inner, anchor="nw"
        )

        self.chat_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind("<Configure>", self._al_redimensionar)

        # Rueda del ratón (Windows/macOS y Linux)
        self.root.bind_all("<MouseWheel>", self._rueda)
        self.root.bind_all("<Button-4>", lambda e: self._rueda(e, -1))
        self.root.bind_all("<Button-5>", lambda e: self._rueda(e, 1))

    def _crear_entrada(self):
        barra = tk.Frame(self.root, bg=BG_VENTANA, padx=14, pady=12)
        barra.pack(fill=tk.X)

        caja = tk.Frame(
            barra, bg=BG_CAJA, highlightthickness=1,
            highlightbackground=BORDE, highlightcolor=AMARILLO,
        )
        caja.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.caja_entrada = caja

        self.entry_mensaje = tk.Entry(
            caja,
            font=(FUENTE, 11),
            bg=BG_CAJA,
            fg=TEXTO,
            insertbackground=AMARILLO,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
        )
        self.entry_mensaje.pack(fill=tk.X, expand=True, ipady=9, padx=12)
        self.entry_mensaje.bind("<Return>", lambda e: self.enviar_mensaje())
        self.entry_mensaje.bind("<FocusIn>", self._quitar_placeholder)
        self.entry_mensaje.bind("<FocusOut>", self._poner_placeholder)
        self._poner_placeholder()

        btn_limpiar = tk.Button(
            barra, text="🗑", font=(FUENTE_EMOJI, 12),
            bg=BORDE, fg=TEXTO, activebackground="#6B3A7D",
            activeforeground="#FFFFFF", relief=tk.FLAT, bd=0,
            padx=12, pady=6, cursor="hand2", command=self.limpiar_chat,
        )
        btn_limpiar.pack(side=tk.RIGHT, padx=(8, 0), fill=tk.Y)
        self._hover(btn_limpiar, BORDE, "#6B3A7D")

        btn_enviar = tk.Button(
            barra, text="Enviar ➤", font=(FUENTE, 10, "bold"),
            bg=NARANJA, fg="#FFFFFF", activebackground=AMARILLO,
            activeforeground="#000000", relief=tk.FLAT, bd=0,
            padx=18, pady=6, cursor="hand2", command=self.enviar_mensaje,
        )
        btn_enviar.pack(side=tk.RIGHT, padx=(8, 0), fill=tk.Y)
        self._hover(btn_enviar, NARANJA, AMARILLO, fg_hover="#000000", fg_normal="#FFFFFF")

        self.root.after(100, self.canvas.focus_set)

    # ───────────────────────── Utilidades ─────────────────────────
    @staticmethod
    def _hover(widget, color_normal, color_hover, fg_normal=None, fg_hover=None):
        def entrar(_):
            widget.config(bg=color_hover)
            if fg_hover:
                widget.config(fg=fg_hover)

        def salir(_):
            widget.config(bg=color_normal)
            if fg_normal:
                widget.config(fg=fg_normal)

        widget.bind("<Enter>", entrar)
        widget.bind("<Leave>", salir)

    def _poner_placeholder(self, _=None):
        if not self.entry_mensaje.get():
            self.entry_mensaje.insert(0, PLACEHOLDER)
            self.entry_mensaje.config(fg=APAGADO)
            self._placeholder_activo = True

    def _quitar_placeholder(self, _=None):
        if self._placeholder_activo:
            self.entry_mensaje.delete(0, tk.END)
            self.entry_mensaje.config(fg=TEXTO)
            self._placeholder_activo = False

    def _texto_escrito(self):
        return "" if self._placeholder_activo else self.entry_mensaje.get().strip()

    def _wrap_actual(self):
        ancho = self.canvas.winfo_width()
        if ancho <= 1:
            ancho = 560
        return max(220, int(ancho * 0.66))

    def _al_redimensionar(self, evento):
        self.canvas.itemconfig(self.ventana_chat, width=evento.width)
        wrap = max(220, int(evento.width * 0.66))
        for burbuja in self.burbujas:
            try:
                burbuja.config(wraplength=wrap)
            except tk.TclError:
                pass

    def _rueda(self, evento, direccion=None):
        if self.canvas.yview() == (0.0, 1.0):
            return
        if direccion is None:
            direccion = -1 * (evento.delta // 120) if abs(evento.delta) >= 120 else -evento.delta
        self.canvas.yview_scroll(int(direccion), "units")

    def _scroll_abajo(self):
        self.root.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    # ───────────────────────── Mensajes ─────────────────────────
    def _agregar_mensaje(self, texto, de_usuario):
        hora = datetime.now().strftime("%H:%M")

        fila = tk.Frame(self.chat_inner, bg=BG_CHAT)
        fila.pack(fill=tk.X, padx=10, pady=(8, 2))

        if de_usuario:
            columna = tk.Frame(fila, bg=BG_CHAT)
            columna.pack(side=tk.RIGHT)

            burbuja = tk.Label(
                columna, text=texto, font=(FUENTE, 10),
                bg=BURBUJA_USER_BG, fg=BURBUJA_USER_FG,
                justify=tk.LEFT, anchor="w", padx=14, pady=9,
                wraplength=self._wrap_actual(),
            )
            burbuja.pack(anchor="e")

            tk.Label(
                columna, text=f"Tú · {hora}", font=(FUENTE, 8),
                fg=APAGADO, bg=BG_CHAT,
            ).pack(anchor="e", pady=(2, 0))
        else:
            tk.Label(
                fila, text="💀", font=(FUENTE_EMOJI, 14),
                bg=BORDE, fg=TEXTO, width=2,
            ).pack(side=tk.LEFT, anchor="n", padx=(0, 8))

            columna = tk.Frame(fila, bg=BG_CHAT)
            columna.pack(side=tk.LEFT)

            burbuja = tk.Label(
                columna, text=texto, font=(FUENTE, 10),
                bg=BURBUJA_BOT_BG, fg=TEXTO,
                justify=tk.LEFT, anchor="w", padx=14, pady=9,
                highlightthickness=1, highlightbackground=BURBUJA_BOT_BORDE,
                wraplength=self._wrap_actual(),
            )
            burbuja.pack(anchor="w")

            tk.Label(
                columna, text=f"Catrina Bot · {hora}", font=(FUENTE, 8),
                fg=APAGADO, bg=BG_CHAT,
            ).pack(anchor="w", pady=(2, 0))

        self.burbujas.append(burbuja)
        self._scroll_abajo()

    def _mostrar_mensaje_usuario(self, mensaje):
        self._agregar_mensaje(mensaje, de_usuario=True)

    def _mostrar_mensaje_bot(self, mensaje):
        self._agregar_mensaje(mensaje, de_usuario=False)

    # ───────────────────────── Indicador "escribiendo" ─────────────────────────
    def _mostrar_escribiendo(self):
        fila = tk.Frame(self.chat_inner, bg=BG_CHAT)
        fila.pack(fill=tk.X, padx=10, pady=(8, 2))
        self.fila_escribiendo = fila

        tk.Label(
            fila, text="💀", font=(FUENTE_EMOJI, 14),
            bg=BORDE, fg=TEXTO, width=2,
        ).pack(side=tk.LEFT, anchor="n", padx=(0, 8))

        self.lbl_escribiendo = tk.Label(
            fila, text="●  ○  ○", font=(FUENTE, 10, "bold"),
            bg=BURBUJA_BOT_BG, fg=MORADO, padx=14, pady=9,
            highlightthickness=1, highlightbackground=BURBUJA_BOT_BORDE,
        )
        self.lbl_escribiendo.pack(side=tk.LEFT)

        self._puntos = 0
        self._animar_escribiendo()
        self._scroll_abajo()

    def _animar_escribiendo(self):
        if self.fila_escribiendo is None:
            return
        frames = ["●  ○  ○", "○  ●  ○", "○  ○  ●"]
        self.lbl_escribiendo.config(text=frames[self._puntos % 3])
        self._puntos += 1
        self._anim_id = self.root.after(250, self._animar_escribiendo)

    def _quitar_escribiendo(self):
        if self._anim_id is not None:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None
        if self.fila_escribiendo is not None:
            self.fila_escribiendo.destroy()
            self.fila_escribiendo = None

    # ───────────────────────── Acciones con Hilos ─────────────────────────
    def enviar_mensaje(self, pregunta=None):
        """Envía el mensaje en un hilo secundario para no congelar la ventana."""
        if self.esperando:
            return

        if pregunta is None:
            pregunta = self._texto_escrito()
            self.entry_mensaje.delete(0, tk.END)
            self._placeholder_activo = False
        if not pregunta:
            return

        self.esperando = True
        self._mostrar_mensaje_usuario(pregunta)
        self._mostrar_escribiendo()

        token = self._token
        despedida = self.bot.es_despedida(pregunta)

        def procesar_respuesta():
            # Se calcula en segundo plano; si entra la IA por respaldo, la GUI no se congela
            respuesta = self.bot.responder(pregunta)
            # Entregamos el resultado al hilo principal de Tkinter
            self.root.after(0, lambda: self._entregar_respuesta(respuesta, despedida, token))

        threading.Thread(target=procesar_respuesta, daemon=True).start()

    def _entregar_respuesta(self, respuesta, despedida, token):
        if token != self._token:
            return  # el chat se limpió mientras tanto
        self._quitar_escribiendo()
        self._mostrar_mensaje_bot(respuesta)
        self.esperando = False

        if despedida:
            self.root.after(1500, self.root.destroy)

    def limpiar_chat(self):
        """Borra el chat y el contexto del bot."""
        self._token += 1
        self._quitar_escribiendo()
        self.esperando = False
        self.bot.reiniciar()

        for hijo in self.chat_inner.winfo_children():
            hijo.destroy()
        self.burbujas.clear()

        self._mostrar_mensaje_bot(BIENVENIDA)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()