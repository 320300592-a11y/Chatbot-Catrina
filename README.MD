# Catrina Bot 💀🌼 - Chatbot de Día de Muertos

**Catrina Bot** es una aplicación interactiva desarrollada en Python con interfaz gráfica en Tkinter. Está diseñada para responder dudas y consultas sobre las tradiciones, elementos y fechas del Día de Muertos en México mediante un motor de Procesamiento de Lenguaje Natural (NLP) totalmente local basado en TF-IDF y similitud coseno.

---

## 👥 Integrantes del Proyecto
* **Juárez Martínez Gabriel Alejandro**
* **Sánchez Pérez Jessica Maylin**

---

## ⚙️ ¿Cómo funciona?

El sistema opera 100% de manera local y no requiere conexión a internet ni consumo de APIs externas:

1. **Base de Conocimiento (`dia_de_muertos.txt`):** Contiene la información temática estructurada (definición, orígenes, elementos de la ofrenda, ofrenda para mascotas, fechas clave y preguntas frecuentes).
2. **Preprocesamiento Lingüístico (`main.py`):** Realiza normalización de texto (remoción de acentos y caracteres especiales), lematización básica/raíces de palabras, eliminación de palabras vacías (*stopwords*) y expansión por sinónimos comunes.
3. **Motor de Recuperación (TF-IDF + Coseno):** Calcula la frecuencia de término y frecuencia inversa de documento para vectorizar tanto la base de datos como la consulta del usuario, recuperando la respuesta más precisa mediante similitud coseno.
4. **Memoria de Conversación y Seguimiento:** Detecta si una pregunta da continuidad a la anterior (ej. *"¿y eso qué significa?"*, *"explícame"*), manteniendo el contexto temático activo.
5. **Interfaz Gráfica Asíncrona (`interfaz.py`):** Implementada en Tkinter con temática alusiva al Día de Muertos. Utiliza hilos (`threading`) para procesar las respuestas en segundo plano, evitando que la ventana se congele o bloquee.

---

## 📋 Requisitos del Sistema

* **Python 3.10 o superior** instalado en el equipo.
* Librerías: El proyecto utiliza exclusivamente la biblioteca estándar de Python (`tkinter`, `threading`, `math`, `re`, `unicodedata`, `collections`, `difflib`), por lo que **no requiere instalaciones adicionales vía `pip`**.

---

## 🚀 Instrucciones de Ejecución

Para iniciar el chatbot con su interfaz gráfica:

1. **Clonar o descargar** este repositorio en tu computadora:
   ```bash
   git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)