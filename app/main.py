import uuid
import qrcode
import io
import base64
from datetime import datetime

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models

# Iniciar esquemas y tablas en Supabase automáticamente
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Control VIP Cloud")
templates = Jinja2Templates(directory="app/templates")

# --- CAMBIAR ESTO AL SUBIR A RENDER ---
URL_BASE_SISTEMA = "http://localhost:9999" 
# ---------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel VIP</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #121212; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e1e1e; padding: 40px; border-radius: 15px; border: 1px solid #333; text-align: center; width: 300px; }
            input { width: 90%; padding: 12px; margin: 20px 0; border-radius: 8px; border: 1px solid #444; background: #2d2d2d; color: white; }
            button { background: #00c853; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎫 Nueva Entrada</h2>
            <form action="/generar" method="post">
                <input type="text" name="nombre" placeholder="Nombre del Ganador" required>
                <button type="submit">Generar QR VIP</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/generar", response_class=HTMLResponse)
def generar_qr(request: Request, nombre: str = Form(...), db: Session = Depends(get_db)):
    token = str(uuid.uuid4())
    nueva_entrada = models.Entrada(id=token, nombre_ganador=nombre)
    db.add(nueva_entrada)
    db.commit()
    
    url_validacion = f"{URL_BASE_SISTEMA}/validar/{token}"
    
    # Generar QR en memoria (Base64)
    img = qrcode.make(url_validacion)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_str = base64.b64encode(buf.getvalue()).decode()
    
    return templates.TemplateResponse("ticket.html", {
        "request": request, "nombre": nombre, "imagen_qr": f"data:image/png;base64,{img_str}"
    })

@app.get("/validar/{token}", response_class=HTMLResponse)
def validar(request: Request, token: str, db: Session = Depends(get_db)):
    entrada = db.query(models.Entrada).filter(models.Entrada.id == token).first()
    
    if not entrada:
        return templates.TemplateResponse("resultado.html", {"request": request, "status": "¡ERROR!", "msg": "QR NO VÁLIDO", "nombre": "DESCONOCIDO", "color": "#c0392b"})
    
    if entrada.usada:
        return templates.TemplateResponse("resultado.html", {"request": request, "status": "DENEGADO", "msg": "ESTA ENTRADA YA FUE USADA", "nombre": entrada.nombre_ganador, "color": "#f39c12"})
    
    entrada.usada = True
    entrada.fecha_uso = datetime.now()
    db.commit()
    
    return templates.TemplateResponse("resultado.html", {"request": request, "status": "¡ÉXITO!", "msg": "ACCESO PERMITIDO", "nombre": entrada.nombre_ganador, "color": "#27ae60"})