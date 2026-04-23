import os
import base64
import json
import requests
from config.config import MODELO_VISION, OLLAMA_URL, CONFIG_CONSISTENTE, TIMEOUT, MAX_REINTENTOS

def clasificar_imagen(ruta_imagen: str, categorias: list) -> dict:
    """
    Clasifica una imagen en una de las categorías proporcionadas usando Ollama
    """
    with open(ruta_imagen, "rb") as f:
        imagen_base64 = base64.b64encode(f.read()).decode("utf-8")

    system_prompt = f"""Clasifica la imagen en UNA de estas categorías: {', '.join(categorias)}.
Responde ÚNICAMENTE en formato JSON con:
- categoria: la categoría seleccionada
- confianza: número del 0 al 1
- razones: breve explicación de por qué elegiste esa categoría

Si no estás seguro o la imagen no coincide con ninguna categoría,
responde con categoria: "desconocido"."""

    payload = {
        "model": MODELO_VISION,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "¿Qué hay en esta imagen?", "images": [imagen_base64]}
        ],
        **CONFIG_CONSISTENTE
    }

    for intento in range(MAX_REINTENTOS):
        try:
            response = requests.post(OLLAMA_URL.replace("/api/generate", "/api/chat"), 
                            json=payload, timeout=TIMEOUT)
            if response.status_code == 200:
                contenido = response.json()["message"]["content"]
                try:
                    return json.loads(contenido)
                except:
                    return {
                        "categoria": "desconocido",
                        "confianza": 0,
                        "razones": contenido[:200]
                    }
        except Exception as e:
            if intento == MAX_REINTENTOS - 1:
                return {"categoria": "error", "confianza": 0, "razones": str(e)}

    return {"categoria": "error", "confianza": 0, "razones": "Sin conexión"}

def clasificar_imagenes_lote(rutas_imagenes: list, categorias: list) -> list:
    """Clasifica múltiples imágenes"""
    resultados = []
    for ruta in rutas_imagenes:
        resultado = clasificar_imagen(ruta, categorias)
        resultados.append({"imagen": ruta, "resultado": resultado})

    conteo = {}
    for r in resultados:
        cat = r["resultado"].get("categoria", "desconocido")
        conteo[cat] = conteo.get(cat, 0) + 1

    return {"resultados": resultados, "estadisticas": conteo, "total": len(resultados)} # type: ignore

def verificar_conexion_ollama() -> bool:
    """Verifica si Ollama está disponible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False
    


resultado = clasificar_imagen("img/foto9.jpg", ["gato", "perro", "pajaro", "desconocido"])
print(json.dumps(resultado, indent=2, ensure_ascii=False))