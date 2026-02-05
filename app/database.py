from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_database_url

# Nombre de la base de datos
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Creamos la conexion
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)