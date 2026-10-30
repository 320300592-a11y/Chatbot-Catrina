# main.py
# -*- coding: utf-8 -*-
import difflib
import math
import os
import random
import re
import unicodedata
from collections import Counter
 
from config import (
    ARCHIVO,
    UMBRAL,
    BIENVENIDA,
    SALUDOS,
    RESPUESTAS_SALUDO,
    DESPEDIDAS,
    AGRADECIMIENTOS,
    AYUDA,
    STOPWORDS,
    EXCEPCIONES_RAIZ,
    SINONIMOS,
)

PREGUNTAS_DEFINICION = ("que es ", "que significa", "que son ", "que quiere decir",
                        "definicion", "significado")
PREGUNTAS_LISTA = ("que lleva", "que llevan", "que se pone", "que se ponen",
                   "que se coloca", "que elementos", "elementos", "que tiene ",
                   "que tienen", "que contiene", "que incluye", "que comen",
                   "que se come", "que comida", "que se toma", "que beben")
UMBRAL_FAQ = 0.80
UMBRAL_LISTA = 0.12

INICIO_SEGUIMIENTO = {"y", "pero", "entonces", "tambien", "ademas"}
MARCADORES_SEGUIMIENTO = {"eso", "esa", "ese", "esto", "esta", "este", "estos", "estas",
                          "su", "sus", "ahi", "mismo", "misma"}

FRASES_GENERICAS = {
    "que es", "que son", "explicame", "cuentame", "cuentame mas", "dime mas",
    "de que trata", "no entendi", "mas informacion", "como es", "que significa",
    "mas detalles", "hablame de eso", "explicacion"
}
 
 
def normalizar(texto):
    """Minúsculas y sin acentos."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")
 
 
def raiz(palabra):
    """Quita plurales de forma segura sin romper palabras invariables."""
    if palabra in EXCEPCIONES_RAIZ:
        return palabra
    if len(palabra) > 4 and palabra.endswith("es"):
        return palabra[:-2]
    if len(palabra) > 3 and palabra.endswith("s") and not palabra.endswith("is"):
        return palabra[:-1]
    return palabra
 
 
def tokenizar(texto):
    palabras = re.findall(r"[a-zñ0-9]+", normalizar(texto))
    return [raiz(p) for p in palabras if p not in STOPWORDS]
 
 
def corregir(tokens, vocabulario):
    """Corrige errores ortográficos manteniendo cutoff estricto."""
    corregidos = []
    for t in tokens:
        if (t in vocabulario or t in SINONIMOS or len(t) < 5
                or any(v.startswith(t) for v in vocabulario)):
            corregidos.append(t)
            continue
        candidatas = [v for v in vocabulario if v[0] == t[0] and abs(len(v) - len(t)) <= 1]
        parecidas = difflib.get_close_matches(t, candidatas, n=1, cutoff=0.90)
        corregidos.append(parecidas[0] if parecidas else t)
    return corregidos
 
 
def expandir(tokens):
    """Agrega sinónimos a los tokens de la pregunta."""
    extra = []
    for t in tokens:
        for s in SINONIMOS.get(t, []):
            extra.extend(raiz(w) for w in s.split())
    return tokens + extra
 
 
def limpiar_linea(linea):
    return linea.strip().lstrip("•-*· \t").strip()
 
 
def resumir(texto, palabras=6):
    corto = " ".join(texto.split()[:palabras])
    return corto + ("..." if len(texto.split()) > palabras else "")
 
 
def cargar_fragmentos(ruta):
    if not os.path.exists(ruta):
        print(f"Advertencia: No se encontró el archivo {ruta}")
        return [], []
 
    with open(ruta, encoding="utf-8") as f:
        crudas = f.read().splitlines()
    lineas = [(limpiar_linea(l), l[:1] in (" ", "\t")) for l in crudas if l.strip()]
 
    fragmentos, temas = [], []
    titulo, etiquetas, pregunta = "", [], None
 
    def cerrar_seccion():
        if titulo and len(etiquetas) >= 6:
            resumen = f"{titulo}: " + ", ".join(etiquetas) + "."
            fragmentos.append((f"{titulo} elementos lista resumen", resumen, titulo, True, False))
 
    for linea, con_sangria in lineas:
        m = re.match(r"^\d+\.\s*(.+)", linea)
        if m:
            cerrar_seccion()
            titulo, etiquetas, pregunta = m.group(1), [], None
            if "faq" not in normalizar(titulo) and "preguntas frecuentes" not in normalizar(titulo):
                temas.append(titulo.strip("¿?"))
            continue
 
        if normalizar(linea).startswith("esta seccion"):
            continue
 
        if linea.startswith("¿"):
            pregunta = linea
            continue
 
        if normalizar(linea).startswith("respuesta del chatbot"):
            partes = linea.split(":", 1)
            respuesta = partes[1].strip() if len(partes) > 1 else linea
            texto_busqueda = f"{pregunta or ''} {respuesta}"
            fragmentos.append((texto_busqueda, respuesta,
                               (pregunta or respuesta).strip("¿?"), False, pregunta is not None))
            pregunta = None
            continue
 
        etiqueta = ""
        if ":" in linea and len(linea.split(" practical", 1)[0]) < 40 and len(linea.split(":", 1)[0]) < 40:
            etiqueta = linea.split(":", 1)[0].strip()
            if not con_sangria:
                etiquetas.append(etiqueta)
 
        texto_busqueda = f"{etiqueta} {etiqueta} {linea} {titulo}"
        fragmentos.append((texto_busqueda, linea, etiqueta or resumir(linea), False, False))
 
    cerrar_seccion()
    return fragmentos, temas
 
 
def calcular_idf(docs_tokens):
    n = len(docs_tokens)
    if n == 0:
        return {}
    df = Counter()
    for tokens in docs_tokens:
        df.update(set(tokens))
    return {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
 
 
def vector_tfidf(tokens, idf):
    tf = Counter(tokens)
    return {t: tf[t] * idf[t] for t in tf if t in idf}
 
 
def coseno(a, b):
    comunes = set(a) & set(b)
    if not comunes:
        return 0.0
    num = sum(a[t] * b[t] for t in comunes)
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0
 
 
class Chatbot:
    def __init__(self, ruta=ARCHIVO):
        self.fragmentos, self.temas = cargar_fragmentos(ruta)
        docs_tokens = [tokenizar(f[0]) for f in self.fragmentos]
        self.idf = calcular_idf(docs_tokens)
        self.vocabulario = list(self.idf)
        self.vectores = [vector_tfidf(t, self.idf) for t in docs_tokens]
        self.faq = [(i, vector_tfidf(tokenizar(f[2]), self.idf))
                    for i, f in enumerate(self.fragmentos) if f[4]]
        self.tema_actual = ""
 
    def reiniciar(self):
        self.tema_actual = ""
 
    @staticmethod
    def _limpiar(pregunta):
        return normalizar(pregunta).strip("¡!¿?., ")
 
    def es_despedida(self, pregunta):
        return self._limpiar(pregunta) in DESPEDIDAS
 
    @staticmethod
    def _es_seguimiento(limpia):
        if limpia in FRASES_GENERICAS:
            return True
        palabras = limpia.split()
        return bool(palabras) and (
            palabras[0] in INICIO_SEGUIMIENTO
            or any(p in MARCADORES_SEGUIMIENTO for p in palabras)
        )
 
    def _buscar_mejor_coincidencia(self, texto, limpia=""):
        tokens = corregir(tokenizar(texto), self.vocabulario)
        es_definicion = limpia.startswith(PREGUNTAS_DEFINICION)
 
        vec_simple = vector_tfidf(tokens, self.idf)
        if vec_simple and self.faq:
            sim, i_faq = max((coseno(vec_simple, v), i) for i, v in self.faq)
            if sim >= UMBRAL_FAQ:
                return self.fragmentos[i_faq], 1.0, [], UMBRAL
 
        if es_definicion and len([t for t in tokens if t in self.idf]) == 1:
            tokens = tokens + ["significa"]
        vec_q = vector_tfidf(expandir(tokens), self.idf)
        if not vec_q:
            return None, 0.0, [], UMBRAL
 
        puntajes = [coseno(vec_q, v) for v in self.vectores]
        umbral = UMBRAL
 
        if limpia.startswith(PREGUNTAS_LISTA):
            solo_resumenes = [p if f[3] else 0 for f, p in zip(self.fragmentos, puntajes)]
            if max(solo_resumenes) >= UMBRAL_LISTA:
                puntajes = solo_resumenes
                umbral = UMBRAL_LISTA
        elif es_definicion:
            puntajes = [0 if f[3] else p for f, p in zip(self.fragmentos, puntajes)]
 
        orden = sorted(range(len(puntajes)), key=puntajes.__getitem__, reverse=True)
        mejor = orden[0]
        cercanos = [self.fragmentos[i][2] for i in orden[:2] if puntajes[i] > 0.12]
        return self.fragmentos[mejor], puntajes[mejor], cercanos, umbral
 
    def responder(self, pregunta):
        limpia = self._limpiar(pregunta)
        if not limpia:
            return "Escribe tu pregunta 🙂"
        if limpia in SALUDOS:
            return random.choice(RESPUESTAS_SALUDO)
        if limpia in AGRADECIMIENTOS:
            return "¡De nada! 🌼 ¿Tienes alguna otra duda sobre el tema?"
        if limpia in DESPEDIDAS:
            return "¡Hasta luego! 🌼"
        if limpia in AYUDA:
            lista = "\n".join(f"- {t}" for t in self.temas)
            return ("Puedo responder sobre estos temas:\n\n" + lista)
 
        if not self.vectores:
            return "No hay información cargada en el archivo de texto."

        tokens_utiles = corregir(tokenizar(pregunta), self.vocabulario)

        if (not tokens_utiles or limpia in FRASES_GENERICAS) and not self.tema_actual:
            return ("¿De qué elemento o tema en específico te gustaría saber? "
                    "Por ejemplo: la Catrina, la ofrenda, el cempasúchil, las mascotas o escribe 'ayuda'.")
 
        # 1. Coincidencia directa
        mejor_frag, puntaje, cercanos, umbral = self._buscar_mejor_coincidencia(pregunta, limpia)
 
        # 2. Seguimiento de conversación
        if ((not mejor_frag or puntaje < umbral) and self.tema_actual
                and self._es_seguimiento(limpia)):
            pregunta_con_contexto = f"{pregunta} {self.tema_actual}"
            frag_ctx, puntaje_ctx, cercanos_ctx, umbral_ctx = \
                self._buscar_mejor_coincidencia(pregunta_con_contexto, limpia)
 
            if frag_ctx and puntaje_ctx >= umbral_ctx:
                mejor_frag, puntaje, cercanos, umbral = frag_ctx, puntaje_ctx, cercanos_ctx, umbral_ctx
 
        # 3. Retornar coincidencia local
        if mejor_frag and puntaje >= umbral:
            self.tema_actual = mejor_frag[2]
            return mejor_frag[1]
 
        # 4. Respuesta cuando no se encuentra en las notas
        texto = "No encontré esa información en mis notas del Día de Muertos."
        if cercanos:
            texto += f"\n\n¿Quizá te refieres a alguno de estos temas?: {' / '.join(cercanos)}"
        else:
            texto += (
                "\n\n💡 Tip para preguntar mejor:\n"
                "- Menciona el elemento específico (ejemplo: 'cempasúchil', 'veladoras', 'Catrina', 'mascotas').\n"
                "- Evita frases como 'cuéntame de eso' si no hemos hablado antes de un tema.\n"
                "- Escribe 'ayuda' para ver todos los temas disponibles."
            )
        return texto
 
 
def main():
    bot = Chatbot()
    print(BIENVENIDA)
    while True:
        try:
            pregunta = input("\nTú: ").strip()
            if not pregunta:
                continue
            print("Bot:", bot.responder(pregunta))
            if bot.es_despedida(pregunta):
                break
        except (KeyboardInterrupt, EOFError):
            print("\n¡Hasta luego! 🌼")
            break
 
 
if __name__ == "__main__":
    main()