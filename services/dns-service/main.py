import dns.resolver
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="DNS Service", version="1.0.0")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DNSResponse(BaseModel):
    ip: str | None
    tiene_mx: bool


@app.get("/health")
def health():
    return {"status": "healthy", "service": "dns-service"}


@app.get("/dns/{dominio}", response_model=DNSResponse)
def obtener_datos_dns(dominio: str):
    """Obtiene IP y registros MX de un dominio"""
    try:
        # Obtener IP
        ip = None
        try:
            respuesta_a = dns.resolver.resolve(dominio, "A", lifetime=3.0, raise_on_no_answer=False)
            if respuesta_a.rrset is not None:
                for r in respuesta_a:
                    ip = r.address
                    break
        except Exception as e:
            logger.warning(f"Error obteniendo IP para {dominio}: {e}")

        # Verificar MX
        tiene_mx = False
        try:
            respuesta_mx = dns.resolver.resolve(dominio, "MX", lifetime=3.0, raise_on_no_answer=False)
            if respuesta_mx.rrset is not None:
                tiene_mx = True
        except Exception as e:
            logger.warning(f"Error obteniendo MX para {dominio}: {e}")

        return DNSResponse(ip=ip, tiene_mx=tiene_mx)
    except Exception as e:
        logger.error(f"Error procesando DNS para {dominio}: {e}")
        raise HTTPException(status_code=500, detail=f"Error en consulta DNS: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
