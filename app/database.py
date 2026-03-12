from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CONEXIÓN DIRECTA (Puerto 5432) - Más estable para pruebas locales
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:26228299j.a@db.lnobkltufmayfxvmloxj.supabase.co:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()