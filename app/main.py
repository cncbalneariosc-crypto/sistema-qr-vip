from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import qrcode
import base64
from io import BytesIO
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Entrada 

app = FastAPI(title="Innova Dynamics - QR VIP")

# Configuración de rutas
URL_BASE_SISTEMA = "https://sistema-qr-vip-1.onrender.com"
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generar", response_class=HTMLResponse)
def generar_qr(request: Request, nombre: str = Form(...), db: Session = Depends(get_db)):
    try:
        token = str(uuid.uuid4())
        nueva_entrada = Entrada(id=token, nombre_ganador=nombre, usada=False, fecha_creacion=datetime.now())
        db.add(nueva_entrada)
        db.commit()
        
        url_validacion = f"{URL_BASE_SISTEMA}/validar/{token}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url_validacion)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "qr_code": qr_base64,
            "nombre": nombre,
            "exito": True
        })
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error en el servidor")

@app.get("/validar/{token}", response_class=HTMLResponse)
def validar(request: Request, token: str, db: Session = Depends(get_db)):
    entrada = db.query(Entrada).filter(Entrada.id == token).first()
    if not entrada:
        res = {"msg": "❌ TICKET NO ENCONTRADO", "color": "#ff4d4d"}
    elif entrada.usada:
        res = {"msg": f"⚠️ YA USADO POR: {entrada.nombre_ganador}", "color": "#ffa500"}
    else:
        entrada.usada = True
        entrada.fecha_uso = datetime.now()
        db.commit()
        res = {"msg": f"✅ ACCESO CONCEDIDO: {entrada.nombre_ganador}", "color": "#2ecc71"}
    
    return templates.TemplateResponse("resultado.html", {"request": request, **res})