import logging
import asyncio
import sys
sys.path.append('/app/shared')

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
import httpx
from shared.schemas import CrearDominio, ActualizaDominio, DominioSalida

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    description="API Gateway para orquestar microservicios"
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs de los microservicios
DNS_SERVICE = "http://dns-service:8001"
REPUTATION_SERVICE = "http://reputation-service:8002"
DOMAIN_CRUD_SERVICE = "http://domain-crud:8003"

http_client = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()


@app.get("/")
def bienvenida():
    return {"message": "Bienvenido a la API de Dominios - Gateway"}


@app.get("/health")
async def health():
    """Health check del gateway y servicios"""
    services_status = {}
    
    try:
        resp = await http_client.get(f"{DNS_SERVICE}/health")
        services_status["dns"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        services_status["dns"] = "unreachable"
    
    try:
        resp = await http_client.get(f"{REPUTATION_SERVICE}/health")
        services_status["reputation"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        services_status["reputation"] = "unreachable"
    
    try:
        resp = await http_client.get(f"{DOMAIN_CRUD_SERVICE}/health")
        services_status["domain-crud"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        services_status["domain-crud"] = "unreachable"
    
    return {"status": "healthy", "services": services_status}


@app.post("/dominio", response_model=DominioSalida)
async def create_domain(datos: CrearDominio):
    """Crear dominio con datos completos de servicios externos"""
    logger.info(f"Creando dominio: {datos.nombre}")
    
    try:
        # 1. Consultar servicios externos en paralelo
        dns_task = http_client.get(f"{DNS_SERVICE}/dns/{datos.nombre}")
        rep_task = http_client.get(f"{REPUTATION_SERVICE}/reputation/{datos.nombre}")
        
        dns_resp, rep_resp = await asyncio.gather(dns_task, rep_task)
        
        if dns_resp.status_code != 200 or rep_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error consultando servicios externos")
        
        dns_data = dns_resp.json()
        rep_data = rep_resp.json()
        
        # 2. Crear dominio en CRUD
        crud_resp = await http_client.post(
            f"{DOMAIN_CRUD_SERVICE}/dominios",
            json=datos.model_dump()
        )
        
        if crud_resp.status_code == 400:
            raise HTTPException(status_code=400, detail=f"El dominio {datos.nombre} ya existe")
        elif crud_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error creando dominio")
        
        # 3. Completar datos del dominio
        complete_resp = await http_client.patch(
            f"{DOMAIN_CRUD_SERVICE}/dominios/{datos.nombre}/complete",
            params={
                "ip": dns_data.get("ip", ""),
                "tiene_mx": dns_data.get("tiene_mx", False),
                "fuentes_rep": rep_data.get("fuentes", [])
            }
        )
        
        if complete_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error completando datos del dominio")
        
        return complete_resp.json()
        
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.get("/dominios", response_model=list[DominioSalida])
async def list_domains():
    """Listar todos los dominios"""
    try:
        resp = await http_client.get(f"{DOMAIN_CRUD_SERVICE}/dominios")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error obteniendo dominios")
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.get("/dominio/{nombre_dominio}", response_model=DominioSalida)
async def get_domain(nombre_dominio: str):
    """Obtener un dominio específico"""
    try:
        resp = await http_client.get(f"{DOMAIN_CRUD_SERVICE}/dominios/{nombre_dominio}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
        elif resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error obteniendo dominio")
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.patch("/dominio/{nombre_dominio}", response_model=DominioSalida)
async def update_domain(nombre_dominio: str, datos: ActualizaDominio):
    """Actualizar dominio con nuevas consultas externas"""
    logger.info(f"Actualizando dominio: {nombre_dominio}")
    
    try:
        # 1. Consultar servicios externos en paralelo
        dns_task = http_client.get(f"{DNS_SERVICE}/dns/{nombre_dominio}")
        rep_task = http_client.get(f"{REPUTATION_SERVICE}/reputation/{nombre_dominio}")
        
        dns_resp, rep_resp = await asyncio.gather(dns_task, rep_task)
        
        if dns_resp.status_code != 200 or rep_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error consultando servicios externos")
        
        dns_data = dns_resp.json()
        rep_data = rep_resp.json()
        
        # 2. Fusionar fuentes de reputación
        fuentes_actualizadas = datos.fuentes_reputacion or []
        fuentes_actualizadas.extend(rep_data.get("fuentes", []))
        
        # 3. Actualizar en CRUD
        crud_resp = await http_client.patch(
            f"{DOMAIN_CRUD_SERVICE}/dominios/{nombre_dominio}",
            json=datos.model_dump()
        )
        
        if crud_resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no existe")
        elif crud_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error actualizando dominio")
        
        # 4. Completar datos actualizados
        complete_resp = await http_client.patch(
            f"{DOMAIN_CRUD_SERVICE}/dominios/{nombre_dominio}/complete",
            params={
                "ip": dns_data.get("ip", ""),
                "tiene_mx": dns_data.get("tiene_mx", False),
                "fuentes_rep": fuentes_actualizadas
            }
        )
        
        if complete_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error completando actualización")
        
        return complete_resp.json()
        
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.delete("/dominio/{nombre_dominio}")
async def delete_domain(nombre_dominio: str):
    """Eliminar dominio"""
    try:
        resp = await http_client.delete(f"{DOMAIN_CRUD_SERVICE}/dominios/{nombre_dominio}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Dominio '{nombre_dominio}' no encontrado")
        elif resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error eliminando dominio")
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.get("/dominios/estado/{estado}", response_model=list[DominioSalida])
async def get_domain_state(estado: str):
    """Filtrar dominios por estado"""
    try:
        resp = await http_client.get(f"{DOMAIN_CRUD_SERVICE}/dominios/filtro/estado/{estado}")
        if resp.status_code == 422:
            raise HTTPException(status_code=422, detail=resp.json()["detail"])
        elif resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error filtrando dominios")
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.get("/dominios/reputacion/{score}", response_model=list[DominioSalida])
async def get_domain_score(score: int):
    """Filtrar dominios por score"""
    try:
        resp = await http_client.get(f"{DOMAIN_CRUD_SERVICE}/dominios/filtro/reputacion/{score}")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error filtrando dominios")
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


@app.get("/dominios/mx/{tiene_mx}", response_model=list[DominioSalida])
async def get_domain_mx(tiene_mx: bool):
    """Filtrar dominios por disponibilidad MX"""
    try:
        resp = await http_client.get(f"{DOMAIN_CRUD_SERVICE}/dominios/filtro/mx/{tiene_mx}")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error filtrando dominios")
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Error HTTP: {e}")
        raise HTTPException(status_code=500, detail="Error comunicándose con microservicios")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
