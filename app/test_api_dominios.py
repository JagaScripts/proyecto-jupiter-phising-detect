import requests

BASE_URL_API = "http://127.0.0.1:8080"

# CREA DOMINIO 1
# Este dominio tiene score de reputacion en VT
print("\n" + "*"*30, "CREA DOMINIO 1", "*"*30)
dominio = {
    "nombre": "beritapb.com"
}
response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
# Imprimimos el código de respuesta. Este formato se va a aplicar a todas las peticiones 
print("\nCódigo Respuesta Crea Dominio 1:", response.status_code)
# Mosramos el contenido de la respuesta. Este formato se va a aplicar a todas las peticiones
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200 o 201.
# El codigo 201 indica que se ha creado algo nuevo
# Este formato se va a aplicar a todas las peticiones de tipo POST 
assert response.status_code in [200, 201]

# CREA DOMINIO 2
# Este dominio tiene score de reputacion en VT y creamos las etiquetas
print("*"*30, "CREA DOMINIO 2", "*"*30)
dominio = {
    "nombre": "baliancer.com",
    "etiquetas": ["malware", "c2"]
}
response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
print("\nCódigo Respuesta Crea Dominio 2:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
assert response.status_code in [200, 201]

# CREA DOMINIO 3
# Este dominio tiene score de reputacion en VT y creamos las etiquetas
print("*"*30, "CREA DOMINIO 3", "*"*30)
dominio = {
    "nombre": "gato.com",
    "etiquetas": ["phishing"]
}
response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
print("\nCódigo Respuesta Crea Dominio 3:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
assert response.status_code in [200, 201]

# CREA DOMINIO 4
# Este dominio no tiene score de reputacion en VT y creamos las etiquetas
print("*"*30, "CREA DOMINIO 4", "*"*30)
dominio = {
    "nombre": "leon.com"
}
response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
print("\nCódigo Respuesta Crea Dominio 4:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
assert response.status_code in [200, 201]

# CREA DOMINIO QUE YA EXISTE
# Este dominio no tiene score de reputacion en VT y creamos las etiquetas
print("*"*30, "CREA DOMINIO EXISTENTE", "*"*30)
dominio = {
    "nombre": "leon.com"
}
response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
print("\nCódigo Respuesta Crea Dominio Existente:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
assert response.status_code == 400

# OBTIENE UN DOMINIO
print("*"*30, "OBTIENE UN DOMINIO", "*"*30)
dominio = "baliancer.com"
response = requests.get(f"{BASE_URL_API}/dominio/{dominio}")
print("\nCódigo Respuesta Obtiente Dominio:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# LISTA TODOS LOS DOMINIOS
print("*"*30, "OBTIENE TODOS LOS DOMINIOS", "*"*30)
response = requests.get(f"{BASE_URL_API}/dominios")
print("\nCódigo Respuesta Lista Todos los Dominos:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# ACTUALIZA DOMINIO 1
print("*"*30, "ACTUALIZA DOMINIO 1", "*"*30)
dominio = "baliancer.com"
datos = {
    "estado_dominio": "Malicioso",
    "etiquetas": ["phishing"]
}
response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
print("\nRespuesta Actualiza Dominio 1:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# ACTUALIZA DOMINIO 2
print("*"*30, "ACTUALIZA DOMINIO 2", "*"*30)
dominio = "gato.com"
datos = {
    "estado_dominio": "Malicioso",
    "fuentes_reputacion": [{"manual": 80}]
}
response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
print("\nRespuesta Actualiza Dominio 2:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# ACTUALIZA DOMINIO QUE NO EXISTE
print("*"*30, "ACTUALIZA DOMINIO QUE NO EXISTE", "*"*30)
dominio = "gato1.com"
datos = {
    "estado_dominio": "Malicioso",
    "fuentes_reputacion": [{"manual": 80}]
}
response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
print("\nRespuesta Actualiza Dominio que no existe:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no distinto de 200. Esto 
# implicaría que ha actualizado el dominio
assert response.status_code != 200

# ACTUALIZA CON ESTADO DOMINIO ERRONEO
print("*"*30, "ACTUALIZA CON ESTADO DOMINIO ERRONEO", "*"*30)
dominio = "gato.com"
datos = {
    "estado_dominio": "Penoso",
    "fuentes_reputacion": [{"manual": 80}]
}
response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
print("\nRespuesta Actualiza con estado dominio erroneo:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no distinto de 200. Esto 
# implicaría que ha actualizado el dominio
assert response.status_code != 200

# ACTUALIZA CON FORMATO DE REPUTACION ERRONEO
print("*"*30, "ACTUALIZA CON FORMATO DE REPUTACION ERRONEO", "*"*30)
dominio = "gato.com"
datos = {
    "fuentes_reputacion": [{"manual": "80"}]
}
response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
print("\nRespuesta Actualiza con formato de reputacion erroneo:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no distinto de 200. Esto 
# implicaría que ha actualizado el dominio
assert response.status_code != 200

# ACTUALIZA CON FORMATO DE ETIQUETAS ERRONEO
print("*"*30, "ACTUALIZA CON FORMATO DE ETIQUETAS ERRONEO", "*"*30)
dominio = "gato.com"
datos = {
    "etiquetas": "Suplantacion"
}
response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
print("\nRespuesta Actualiza con formato de etiquetas erroneo:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no distinto de 200. Esto 
# implicaría que ha actualizado el dominio
assert response.status_code != 200

# ELIMINA UN DOMINIO
print("*"*30, "ELIMINA UN DOMINIO", "*"*30)
dominio = {
    "nombre": "leon.com"
}
response = requests.delete(f"{BASE_URL_API}/dominio/{dominio['nombre']}")
print("\nRespuesta Elimina Dominio:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# ELIMINA UN DOMINIO QUE NO EXISTE
print("*"*30, "ELIMINA UN DOMINIO QUE NO EXISTE", "*"*30)
dominio = {
    "nombre": "gato1.com"
}
response = requests.delete(f"{BASE_URL_API}/dominio/{dominio['nombre']}")
print("\nRespuesta Elimina Dominio que no existe:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code != 200

# LISTA DOMINIOS POR ESTADO DESCONOCIDO
print("*"*30, "LISTA DOMINIOS POR ESTADO DESCONOCIDO", "*"*30)
estado_dominio = "Desconocido"
response = requests.get(f"{BASE_URL_API}/dominios/estado/{estado_dominio}")
print("\nRespuesta Lista Dominios/Estado:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# LISTA DOMINIOS POR ESTADO MALICIOSO
print("*"*30, "LISTA DOMINIOS POR ESTADO MALICIOSO", "*"*30)
estado_dominio = "Malicioso"
response = requests.get(f"{BASE_URL_API}/dominios/estado/{estado_dominio}")
print("\nRespuesta Lista Dominios/Estado:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# LISTA DOMINIOS POR SCORE MENOR DE 40
print("*"*30, "LISTA DOMINIOS POR SCORE MENOR DE 40", "*"*30)
score = 40
response = requests.get(f"{BASE_URL_API}/dominios/reputacion/{score}")
print("\nRespuesta Lista Diminios/Score:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# LISTA DOMINIOS POR SCORE MENOR DE 60
print("*"*30, "LISTA DOMINIOS POR SCORE MENOR DE 60", "*"*30)
score = 60
response = requests.get(f"{BASE_URL_API}/dominios/reputacion/{score}")
print("\nRespuesta Lista Diminios/Score:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# LISTA DOMINIOS QUE DISPONEN DE SERVIDOR DE CORREO
print("*"*30, "LISTA DOMINIOS QUE DISPONEN DE SERVIDOR DE CORREO", "*"*30)
mx = True
response = requests.get(f"{BASE_URL_API}/dominios/mx/{mx}")
print("\nRespuesta Lista Diminios con MX:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

# LISTA DOMINIOS QUE NO DISPONEN DE SERVIDOR DE CORREO
print("*"*30, "LISTA DOMINIOS QUE NO DISPONEN DE SERVIDOR DE CORREO", "*"*30)
mx = False
response = requests.get(f"{BASE_URL_API}/dominios/mx/{mx}")
print("\nRespuesta Lista Diminios sin MX:", response.status_code)
print("Contenido Respuesta:", response.json(), "\n\n")
# Lanzamos excepción si el codigo no es 200.
assert response.status_code == 200

print("*"*30, "PASADAS TODAS LAS PRUEBAS CON EXITO", "*"*30, "\n\n")