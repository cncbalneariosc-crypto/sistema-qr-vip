from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class Entrada(Base):
    __tablename__ = "entrada"
    # Esto asegura que los datos VIP vivan separados de tus Pedidos 2.0
    __table_args__ = {"schema": "sistema_qr"} 

    id = Column(String, primary_key=True, index=True)
    nombre_ganador = Column(String)
    usada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_uso = Column(DateTime(timezone=True), nullable=True)