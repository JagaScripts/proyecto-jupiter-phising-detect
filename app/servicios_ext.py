import dns.resolver
import requests
import logging
from dotenv import load_dotenv
from config import get_api_timeout, get_vt_api_key, get_urlscan_api_key

logger = logging.getLogger("dominio")
load_dotenv() # Cargamos las variable de entorno

# Estas funciones tiene_mx, obtiene_ip y fuentes_reputacion se van a ejecutar
# en hilos distintos por lo que las respuestas no seguiran el orden declarado

# Funcion para consultar si un dominio dispone de servidor de correo
def tiene_mx(dominio: str) -> bool:
	try:
		logger.debug(f"[+] Se inicia la comprobacion de MX del dominio {dominio}")
		# Se realiza la consulta al servicio externo. Configuramos que no puede exceder de mas de 3 segundos
		# con el parametro raise_on_no_answer=False evitamos que nos lance una excepcion si el servidor no
		# tiene registros de tipo "MX"
		respuesta = dns.resolver.resolve(dominio, "MX", lifetime=3.0, raise_on_no_answer=False)
		if respuesta.rrset is None:
			logger.debug(f"[+] El {dominio} no tiene registros MX (sin respuesta en ANSWER)")
			return False
		logger.debug(f"[+] Finalizada la comprobacion de MX del dominio {dominio}")
		return True
	except Exception as e:
		logger.warning(f"[-] Ha fallado la comprobacion de MX del dominio {dominio}\nError: {e}")
		return False

# Funcion para consultar si un dominio dispone de servidor de correo
# Es igual que la funcion anterior pero consulta registros de tipo "A" que son IPs
def obtiene_ip(dominio: str) -> str:
	try:
		logger.debug(f"[+] Se inicia la comprobacion de IP del dominio {dominio}")
		# Manejamos la excepcion de igual forma
		respuesta = dns.resolver.resolve(dominio, "A", lifetime=3.0, raise_on_no_answer=False)
		if respuesta.rrset is None:
			logger.debug(f"[+] El {dominio} no tiene registros A (sin respuesta en ANSWER)")
			return ""
		for r in respuesta:
			logger.debug(f"[+] Finalizada la comprobacion de IP del dominio {dominio}")
			return r.address
	except Exception as e:
		logger.warning(f"[-] Ha fallado la comprobacion de IP del dominio {dominio}\nError: {e}")
		return ""
	
# Funcion privada que consulta la API de VirusTotal para obtener el score
def _virustotal(dominio: str) -> dict:
	logger.debug(f"[+] Se inicia la comprobacion del score en VirusTotal del dominio {dominio}")
	URL_Dominio = f"https://www.virustotal.com/api/v3/domains/{dominio}"
	api_key = get_vt_api_key() # Obtenemos la API Key que está almacenada en el archivo .env
	score = {"virustotal": 0}
	# Verificamos que tenemos la KEY, sino asignamos el score por defecto que es 0
	if not api_key:
		logger.warning("[-] No hay configurada una API KEY en VirusTotal")
		return score
	# Configuramos las cabeceras como indica la documentación de la API
	headers_vt = {"accept": "application/json", "x-apikey": api_key}
	# Hacemos la petición a la API
	try:
		respuesta = requests.get(URL_Dominio, headers = headers_vt, timeout=get_api_timeout())
		respuesta.raise_for_status()
		datos = respuesta.json()
	except Exception as e:
		logger.warning(f"[-] Error consultando VirusTotal para {dominio}: {e}")
		return score
	# Buscamos el valor "Malicious" que es donde se almacena el score
	if "malicious" in datos.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}):
		score = {"virustotal": datos["data"]["attributes"]["last_analysis_stats"]["malicious"]}
		logger.debug(f"[+] Finalizada la comprobacion del score en VirusTotal del dominio {dominio}")
		return score
	else:
		logger.info(f"[-] Ha fallado la comprobacion del score en VirusTotal del dominio {dominio} porque no tiene el campo 'malicious'")
		return score

# Funcion privada que consulta la API de Urlscan para obtener el score
def _urlscan(dominio: str) -> dict:
	logger.debug(f"[+] Se inicia la comprobacion del score en Urlscan del dominio {dominio}")
	URL_Dominio = f"https://urlscan.io/api/v1/search/?q=page.domain:{dominio}"
	api_key = get_urlscan_api_key() # Obtenemos la API Key que está almacenada en el archivo .env
	headers = {"API-Key":api_key,"Content-Type":"application/json"} # Confuguramos las cabeceras segun domumentacion
	score = {"urlscan": 0}
	# Verificamos que tenemos la KEY, sino asignamos el score por defecto que es 0
	if not api_key:
		logger.warning("[-] No hay configurada una API KEY en Urlscan")
		return score
	try:
		respuesta = requests.get(URL_Dominio, headers=headers, timeout=get_api_timeout()) # hacemos la consulta a la API. Puede devolver muchos resultados
		respuesta.raise_for_status()
		datos = respuesta.json()
	except Exception as e:
		logger.warning(f"[-] Error consultando Urlscan para {dominio}: {e}")
		return score
	resultados = datos.get("results", {})
	# Verificamos si tenemos resultados y si los hay vamos a buscar el ID del resultado mas nuevo que es el primero de la lista
	if resultados: 
		id = resultados[0]["task"]["uuid"]
		URL_ID = f"https://urlscan.io/api/v1/result/{id}"
		# Hacemos una petición con el ID
		try:
			respuesta = requests.get(URL_ID, headers=headers, timeout=get_api_timeout())
			respuesta.raise_for_status()
			datos = respuesta.json()
		except Exception as e:
			logger.warning(f"[-] Error consultando Urlscan result para {dominio}: {e}")
			return score
		# Buscamos el valor "Malicious" que es donde se almacena el score 
		if "malicious" in datos.get("stats", {}):
			score = {"urlscan": datos["stats"]["malicious"]}
			logger.debug(f"[+] Finalizada la comprobacion del score en Urlscan del dominio {dominio}")
			return score
		else:
			logger.info(f"[-] Ha fallado la comprobacion del score en Urlscan del dominio {dominio} porque no tiene el campo 'malicious")
			return score
	else:
		logger.info(f"[-] No hay resultados en Urlscan del dominio {dominio}")
		return score 

# Con esta funcion montamos los resultados obtenidos por cada fuente de reputacion
# Esta es la funcion que se llama desde el archivo main.py
def fuentes_reputacion(dominio: str) -> list:
	fuentes = []
	fuentes.append(_virustotal(dominio))
	fuentes.append(_urlscan(dominio))
	return fuentes
