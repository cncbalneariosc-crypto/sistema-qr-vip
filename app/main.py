from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import qrcode
import base64
from io import BytesIO
import uuid
from datetime import datetime

# Importaciones de tu base de datos (Asumiendo que así se llaman tus archivos)
from app.database import get_db
from app.models import Entrada 

# 1. INICIALIZAMOS FASTAPI
app = FastAPI(title="Sistema Control VIP Cloud")

# =================================================================
# 🔥 CONFIGURACIÓN BLINDADA PARA RENDER 🔥
# =================================================================
URL_BASE_SISTEMA = "https://sistema-qr-vip-1.onrender.com"
templates = Jinja2Templates(directory="app/templates")
# =================================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Carga la página principal del sistema"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generar", response_class=HTMLResponse)
def generar_qr(request: Request, nombre: str = Form(...), db: Session = Depends(get_db)):
    """Genera el token, lo guarda en Supabase y crea el código QR visual"""
    try:
        # Generar ID único
        token = str(uuid.uuid4())
        
        # Guardar en base de datos
        nueva_entrada = Entrada(
            id=token,
            nombre_ganador=nombre,
            usada=False,
            fecha_creacion=datetime.now()
        )
        db.add(nueva_entrada)
        db.commit()
        
        # LA URL MÁGICA QUE SOLUCIONA EL ERROR
        url_validacion = f"{URL_BASE_SISTEMA}/validar/{token}"
        
        # Generar imagen QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url_validacion)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a Base64 para HTML
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "qr_code": qr_base64,
            "nombre": nombre,
            "mensaje": "✅ Ticket VIP generado con éxito"
        })
        
    except Exception as e:
        print(f"ERROR FATAL EN GENERACIÓN: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor. Revisa los logs de Render.")

@app.get("/validar/{token}", response_class=HTMLResponse)
def validar(request: Request, token: str, db: Session = Depends(get_db)):
    """Escanea el QR y valida si la entrada existe o ya fue usada"""
    entrada = db.query(Entrada).filter(Entrada.id == token).first()
    
    if not entrada:
        return templates.TemplateResponse("validar.html", {
            "request": request, 
            "mensaje": "❌ TICKET FALSO O NO ENCONTRADO", 
            "color": "red"
        })
        
    if entrada.usada:
        return templates.TemplateResponse("validar.html", {
            "request": request, 
            "mensaje": f"⚠️ TICKET YA USADO por {entrada.nombre_ganador}", 
            "color": "orange"
        })
        
    # Si todo está bien, marcar como usada
    entrada.usada = True
    entrada.fecha_uso = datetime.now()
    db.commit()
    
    return templates.TemplateResponse("validar.html", {
        "request": request, 
        "mensaje": f"✅ ACCESO PERMITIDO: {entrada.nombre_ganador}", 
        "color": "green"
    })