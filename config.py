
import os
 
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(CARPETA, "dia_de_muertos.txt")
UMBRAL = 0.22
 
BIENVENIDA = (
    "¡Hola! 🌼 Soy Catrina Bot.\n\n"
    "Para darte la respuesta exacta de mis textos, por favor incluye el tema o elemento directo:\n"
    "• Menciona el nombre clave: 'pan de muerto', 'cempasúchil', 'Catrina', 'mascotas', 'niveles del altar'.\n"
    "• Haz preguntas directas: '¿Qué significa el pan de muerto?' o '¿Cuándo llegan los perros?'.\n"
    "• Para profundizar en el tema anterior, puedes decir: '¿y eso qué significa?' o 'explícame'.\n\n"
    "Escribe 'ayuda' para ver la lista de temas que conozco."
)
SALUDOS = {"hola", "buenas", "hey", "buenos dias", "buenas tardes", "buenas noches"}
RESPUESTAS_SALUDO = [
    "¡Hola! Pregúntame lo que quieras sobre el Día de Muertos.",
    "¡Hola! 🌼 ¿Qué te gustaría saber del Día de Muertos o las ofrendas?",
    "¡Bienvenido! Puedo contarte sobre la ofrenda para mascotas, la Catrina, las fechas y más.",
]
DESPEDIDAS = {"adios", "salir", "bye", "chao", "hasta luego"}
AGRADECIMIENTOS = {"gracias", "muchas gracias", "ok gracias"}
AYUDA = {"ayuda", "que puedes hacer", "que sabes", "temas", "de que puedes hablar",
         "que puedo preguntar"}
 
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "de", "del", "y", "o", "en", "a",
    "que", "es", "se", "por", "con", "para", "al", "lo", "su", "sus", "como",
    "mas", "pero", "me", "mi", "te", "tu", "son", "cual", "cuales",
    "hay", "ser", "esta", "este", "eso", "esa", "les", "le"
}
 
EXCEPCIONES_RAIZ = {
    "pais", "dios", "mes", "tres", "dos", "compas", "interes", "despues", "ademas"
}
 
SINONIMOS = {
    "flor": ["cempasuchil"],
    "vela": ["veladora"],
    "altar": ["ofrenda"],
    "ofrenda": ["altar"],
    "comida": ["platillo", "croqueta", "alimento"],
    "comen": ["comida", "platillo"],
    "comer": ["comida", "platillo"],
    "come": ["comida", "platillo"],
    "beber": ["bebida", "agua"],
    "toman": ["bebida", "agua"],
    "dulce": ["calavera", "azucar"],
    "fiesta": ["celebracion", "tradicion", "festejo"],
    "festeja": ["celebra", "celebracion", "fecha"],
    "festejan": ["celebra", "celebracion"],
    "festejar": ["celebra", "celebracion"],
    "festejo": ["celebracion", "tradicion"],
    "lugar": ["donde", "mexico", "pais"],
    "origen": ["prehispanico"],
    "halloween": ["celta", "diferencia", "diferencias"],
    "diferencia": ["distinto", "halloween", "celta", "comparar"],
    "diferencias": ["distinto", "halloween", "celta", "comparar"],
    "distinto": ["diferencia", "halloween"],
    "vs": ["diferencia", "halloween"],
    "unesco": ["patrimonio", "internacional"],
    "foto": ["fotografia", "retrato"],
    "calavera": ["craneo"],
    "perro": ["mascota", "animal"],
    "gato": ["mascota", "perro", "animal"],
    "pone": ["coloca", "lleva"],
    "pongo": ["coloca", "lleva"],
    "ponen": ["coloca", "lleva"],
    "poner": ["coloca", "lleva"],
    "mascota": ["perro", "gato", "animal"],
    "vienen": ["llegan", "llegada", "visita", "regresan"],
    "viene": ["llega", "llegada", "visita", "regresa"],
    "llegan": ["vienen", "llegada", "visita"],
    "llega": ["viene", "llegada", "visita"],
    "tumba": ["panteon"],
    "cementerio": ["panteon"],
    "nino": ["angelito"],
}