# config.py — configuración compartida terminal + interfaz

MODELO_VISION = "qwen3.5:2b"                         # Cambia aquí el modelo 
OLLAMA_URL    = "http://10.46.191.232:11434/api/generate"

# Parámetros de consistencia (garantizan el mismo resultado siempre)
CONFIG_CONSISTENTE = {
    "temperature": 0.0,    # Cero aleatoriedad
    "seed": 42,            # Semilla fija para reproducibilidad
    "num_predict": 150,
    "top_k": 1,
    "top_p": 0.9,
    "think": False,
    "repeat_penalty": 1.0,
    "stream": False
}

TIMEOUT          = 120     # 2 minutos por imagen
MAX_REINTENTOS   = 3
CARPETA_IMAGENES = "img"
CARPETA_RESULTADOS = "resultados"

CATEGORIAS_POR_DEFECTO = [
    "gato", "perro", "pajaro", "auto",
    "comida", "persona", "flor", "arbol",
    "casa", "desconocido"
]