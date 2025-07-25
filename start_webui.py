import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Config
os.environ.setdefault("OLLAMA_API_BASE", "http://localhost:11434")
PORT = int(os.getenv("WEBUI_PORT", "3001"))

# --- Cargar la app de la API original ---
api_app = None
for candidate in ("open_webui.main", "open_webui.app", "open_webui.server"):
    try:
        mod = __import__(candidate, fromlist=["app"])
        api_app = getattr(mod, "app", None)
        if api_app:
            break
    except Exception:
        continue
if not api_app:
    raise ImportError("No se encontró 'app' dentro de open_webui")

# --- Localizar carpeta frontend ---
static_dir = Path(__file__).parent / "open-webui" / "build"
index_file = static_dir / "index.html"
if not index_file.exists():
    raise FileNotFoundError(f"No se encontró {index_file}")

app = FastAPI()

# Montamos la API en /api
app.mount("/api", api_app)
# Montamos /socket.io (websocket/socketio) apuntando también a la API
app.mount("/socket.io", api_app)

# Servimos el frontend completo en la raíz
app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

# Cualquier otra ruta -> index.html (para SPA)
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str, request: Request):
    return FileResponse(index_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="debug")
