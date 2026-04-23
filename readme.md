# 🖼️ VisionXComputadora — Clasificador de Imágenes Local con Ollama

> Herramienta educativa para clasificar imágenes usando modelos de visión por computador de forma **100% local, gratuita y privada** — sin API keys, sin enviar datos a internet.

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Comparativa de Modelos](#comparativa-de-modelos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Evolución del Proyecto](#evolución-del-proyecto)
- [Tecnologías](#tecnologías)

---

## 📌 Descripción

**VisionXComputadora** es un proyecto educativo que demuestra cómo pasar de una solución de clasificación de imágenes basada en la API de OpenAI (de pago, con dependencia de internet) a una solución completamente local usando [Ollama](https://ollama.com) y modelos de visión abiertos como `llava` o `moondream`.

El proyecto incluye todas las versiones intermedias del código, desde el código heredado hasta la interfaz final configurable mediante `config.py`.

---

## ✨ Características

- ✅ **Gratuito** — sin coste por uso ni tarjeta de crédito
- ✅ **Privado** — las imágenes nunca salen de tu máquina
- ✅ **Sin internet** — funciona completamente offline una vez instalado
- ✅ **Multi-modelo** — compatible con `llava`, `moondream`, `llava:13b`, `bakllava`, `llava-phi3`
- ✅ **Configurable** — cambia de modelo con una sola variable en `config.py`
- ✅ **Robusto** — reintentos automáticos, timeouts, redimensionado de imágenes y manejo de errores

---

## 📊 Comparativa de Modelos

| Modelo | Velocidad | Precisión | RAM Mínima | Mejor Para |
|---|---|---|---|---|
| `qwen3.5:2b` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 5 GB | ✅ **Recomendado** — balance calidad/velocidad |
| `moondream` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 4 GB | CPU lento o RAM limitada |
| `llava:13b` | ⭐⭐ | ⭐⭐⭐⭐⭐ | 16 GB | Máxima precisión |
| `bakllava` | ⭐⭐⭐ | ⭐⭐⭐⭐ | 8 GB | Texto pequeño y detección de objetos |
| `llava-phi3` | ⭐⭐⭐⭐ | ⭐⭐⭐ | 6 GB | CPU moderno con RAM moderada |

---

## 🗂️ Estructura del Proyecto

```
VisionXComputadora/
│
│
├── Codigo_Heredado/
│       └── clasificacionImagenes.py  # 🔴 Código original con OpenAI (solo referencia)
│
├── img/                        # Imágenes de entrada para clasificar
├── ui/                  # 🖥️ Interfaz gráfica del clasificador
├── resultados/                 # ⚠️ Generado en local — excluido por .gitignore
│
├── main.py                    # ✅ Primera versión funcional con Ollama
├── main_v2.py                    # Version con interfaz mejorada

├── config.py                   # ⚙️ Configuración compartida interfaz
├── .gitignore
└── readme.md
```



---

## 🚀 Instalación

### 1. Instalar Ollama

```bash
# Windows / macOS: descargar el instalador desde https://ollama.com/download

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Verificar instalación:
ollama --version
```

### 2. Descargar un modelo de visión

```bash
# Recomendado (balance calidad/velocidad):
ollama pull qwen3.5:2b

# Para PCs con poca RAM (4 GB):
ollama pull moondream

# Máxima precisión (requiere 16 GB+):
ollama pull gemma4:e2b
```

### 3. Instalar dependencias Python

```bash
pip install requests customtkinter threading PIL
```


---

## ▶️ Uso

### Configuración (`config.py`)

El archivo `config.py` es compartido entre el clasificador de terminal y la interfaz gráfica, garantizando resultados **idénticos** en ambos entornos:

```python
# config.py — configuración compartida terminal + interfaz

MODELO_VISION = "qwen3.5:2b"     # Cambia aquí el modelo

# OLLAMA_URL Se configura desde la interfaz
OLLAMA_URL    = "http://localhost:11434/api/generate" # Codigo heredado

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
```

### Ejecutar el clasificador

```bash
python main.py

python main_v2.py  # Diseño visual mejorado
```

---

## 🔄 Evolución del Proyecto

| Versión | Archivo | Descripción |
|---|---|---|
| v0 (heredado) | `Codigo_Heredado/clasificacionImagenes.py` | Código original con OpenAI — solo referencia |
| v0 (heredado) | `Codigo_Heredado/clasificacionImagenes_ollama.py` | Código original con ollama — solo referencia |
| v1 | `main.py` | Primera versión funcional con Ollama. Verificación de conexión, clasificación JSON, interfaz grafica basica |
| v2 | `main_v2.py` | Diseño visual mejorado  |
| Config | `config.py` | Configuración centralizada compartida: temperatura, semilla, timeout, prompt unificado |
| Status | `core/status.py` | Verifica la conexion con ollama, actualiza el estado de conexion |
| Ollama | `core/ollama.py` | Nucleo de la clasificacion de imagenes,  |



---

## 🛠️ Tecnologías

- **Python 3.10+**
- **[Ollama](https://ollama.com)** — servidor local de modelos LLM/visión
- **`requests`** — cliente HTTP para comunicarse con Ollama
- **Modelos:** - [Modelos compatibles con vision](https://ollama.com/search?c=vision)

---

## 📄 Licencia

Proyecto educativo de uso libre. Consulta el archivo `LICENSE`.