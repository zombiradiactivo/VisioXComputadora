import threading
import requests


def verificar_ollama(app, ip):
    app.status_label.configure(text="● Verificando...", text_color="#ff9800")
    print(ip)
    threading.Thread(target=lambda a=app, i=ip: _verificar_ollama_thread(a, i), daemon=True).start()

def _verificar_ollama_thread(app, ip):
    ollama_url = f"http://{ip}:11434/api/tags"
    try:
        response = requests.get(ollama_url, timeout=5)
        app.ollama_conectado = response.status_code == 200
    except:
        app.ollama_conectado = False
    app.after(0, lambda a=app: _actualizar_estado_conexion(a))

def _actualizar_estado_conexion(app):
    if app.ollama_conectado:
        app.status_label.configure(text="● Ollama conectado", text_color="#4caf50")
    else:
        app.status_label.configure(text="● Sin conexión", text_color="#f44336")
