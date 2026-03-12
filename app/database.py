from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ Pon tu contraseña real en lugar de AQUI_TU_CONTRASEÑA
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.lnobkltufmayfxvmloxj:26228299j.a@aws-1-sa-east-1.pooler.supabase.com:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()