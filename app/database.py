import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("dominio")

db = os.getenv("DATABASE_URL")

if not db:
    raise ("No existe la base de datos")

# verificamos si se va a usar la base de datos local o la de Docker
if db.startswith("sqlite"):
    logger.info("Usando una base de datos SQLite local")
    engine = create_engine(
        db,
        connect_args={"check_same_thread": False}
    )
else:
    logger.info(f"Usando una base de datos PostgreSQL: {db}")
    engine = create_engine(
        db,
        pool_pre_ping=True
    )

# Creamos la conexion
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)