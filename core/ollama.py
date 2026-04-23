from config.config import MODELO_VISION, CONFIG_CONSISTENTE
import threading
import requests
import json
import base64
import os
import time
import ast

 

def clasificar_imagenes(app, ip):
    if not app.imagenes_seleccionadas:
        app.result_text.delete("0.0", "end")
        app.result_text.insert("0.0", "Selecciona imágenes primero")
        return
    if not app.ollama_conectado:
        app.result_text.delete("0.0", "end")
        app.result_text.insert("0.0", "Conecta con Ollama primero")
        return
    app.result_text.delete("0.0", "end")
    app.result_text.insert("0.0", "Clasificando...\n")
    app.classify_button.configure(state="disabled")
    threading.Thread(target=lambda a=app, i=ip: _clasificar_thread(a, i), daemon=True).start()

def _clasificar_thread(app, ip):
    ollama_url = f"http://{ip}:11434/api/chat"
    app.resultados = []
    total = len(app.imagenes_seleccionadas)
    
    for idx, ruta in enumerate(app.imagenes_seleccionadas):
        inicio = time.time()
        try:
            with open(ruta, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            system_prompt = f"""Clasifica la imagen en UNA de estas categorías: {', '.join(app.categorias)}.
                            Responde ÚNICAMENTE en formato JSON SOLO con:
                            - categoria: la categoría seleccionada
                            - confianza: número del 0 al 1
                            - razones: breve explicación
                            Si no coincide, responde con categoria: "desconocido"."""
            payload = {
                "model": MODELO_VISION,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "¿Qué hay en esta imagen?", "images": [img_b64]}
                ],
                **CONFIG_CONSISTENTE
            }
            response = requests.post(ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                contenido = response.json()["message"]["content"]
                try:
                    resultado = json.loads(contenido)
                except:
                    try:
                        limpio = contenido.strip()
                        if limpio.startswith("```"):
                            lines = limpio.split("\n")
                            lines = lines[1:-1] if lines[0].startswith("```") and lines[-1].startswith("```") else lines
                            limpio = "\n".join(lines)
                        resultado = json.loads(limpio)
                    except:
                        resultado = {"categoria": "desconocido", "confianza": 0, "razones": contenido}
                
                if isinstance(resultado.get("razones"), str):
                    texto = resultado["razones"]
                    es_json = texto.strip().startswith("{") and '"categoria"' in texto
                    es_py = texto.strip().startswith("{") and "'categoria'" in texto
                    if es_json or es_py:
                        try:
                            if es_py:
                                sub = ast.literal_eval(texto)
                            else:
                                sub = json.loads(texto)
                            resultado["categoria"] = sub.get("categoria", resultado.get("categoria", "desconocido"))
                            resultado["confianza"] = sub.get("confianza", resultado.get("confianza", 0))
                            resultado["razones"] = sub.get("razones", texto)
                        except:
                            pass
            else:
                resultado = {"categoria": "error", "confianza": 0, "razones": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            resultado = {"categoria": "error", "confianza": 0, "razones": str(e)}
        
        duracion = time.time() - inicio
        app.resultados.append({"imagen": ruta, "resultado": resultado, "tiempo": duracion})
        app.after(0, lambda a=app, t=total, i=idx+1: _actualizar_progreso(a, t, i))
    
    app.after(0, lambda a=app: _finalizar_clasificacion(a))

def _actualizar_progreso(app, total, actual):
    app.result_text.delete("0.0", "end")
    app.result_text.insert("0.0", f"Procesando {actual}/{total}...\n\n")
    for r in app.resultados:
        nombre = os.path.basename(r["imagen"])
        cat = r["resultado"].get("categoria", "desconocido")
        conf = r["resultado"].get("confianza", 0)
        razones = r["resultado"].get("razones", "")[:500]
        tiempo = r.get("tiempo", 0)
        app.result_text.insert("end", f"📷 {nombre} ({tiempo:.1f}s)\n   → {cat} ({conf:.1%})\n   {razones}\n\n")

def _finalizar_clasificacion(app):
    app.classify_button.configure(state="normal")
    app.mostrar_resultados()