from __future__ import annotations
from app.db.session import engine, Base
from app.db import models  # noqa: F401  (importa modelos para que Base los registre)
from app.db.session import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import Session



def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    # Seed mínimo (DEV) si está vacío
    db: Session = SessionLocal()
    try:
        exists = db.execute(select(models.Domain).limit(1)).scalar_one_or_none()
        if not exists:
            db.add_all([
                models.Domain(id="dom_101", user_id="user_1", domain_name="acme.com", status="active", tags=["marca"]),
                models.Domain(id="dom_205", user_id="user_1", domain_name="acme.es", status="active", tags=["marca","es"]),
                models.Domain(id="dom_777", user_id="user_1", domain_name="acme-dev.net", status="inactive", tags=["dev"]),
            ])
            db.commit()
    finally:
        db.close()