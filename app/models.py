from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class Entrada(Base):
    __tablename__ = "entrada"
    
    id = Column(String, primary_key=True, index=True)
    nombre_ganador = Column(String)
    cedula = Column(String)  # NUEVO: Guardará la cédula
    folio = Column(String)   # NUEVO: Guardará el folio autogenerado
    usada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_uso = Column(DateTime(timezone=True), nullable=True)