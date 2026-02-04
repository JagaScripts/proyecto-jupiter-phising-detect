def test_01_crea_dominio_1():
    """Crea dominio 1: con score de reputación en VT."""
    print("\n" + "*"*30, "CREA DOMINIO 1", "*"*30)
    dominio = {"nombre": "beritapb.com"}
    response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
    print("\nCódigo Respuesta Crea Dominio 1:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code in [200, 201]

def test_02_crea_dominio_2_con_etiquetas():
    """Crea dominio 2: con score en VT y etiquetas."""
    print("*"*30, "CREA DOMINIO 2", "*"*30)
    dominio = {"nombre": "baliancer.com", "etiquetas": ["malware", "c2"]}
    response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
    print("\nCódigo Respuesta Crea Dominio 2:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code in [200, 201]

def test_03_crea_dominio_3_sin_score():
    """Crea dominio 3: sin score de reputación en VT."""
    print("*"*30, "CREA DOMINIO 3", "*"*30)
    dominio = {"nombre": "leon.com"}
    response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
    print("\nCódigo Respuesta Crea Dominio 3:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code in [200, 201]

def test_04_crea_dominio_existente_falla():
    """Intenta crear un dominio que ya existe (espera 400)."""
    print("*"*30, "CREA DOMINIO EXISTENTE", "*"*30)
    dominio = {"nombre": "leon.com"}
    response = requests.post(f"{BASE_URL_API}/dominio/", json=dominio)
    print("\nCódigo Respuesta Crea Dominio Existente:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 400

# --- PRUEBAS DE LECTURA (GET) ---

def test_05_obtiene_un_dominio():
    """Obtiene un dominio específico (baliancer.com)."""
    print("*"*30, "OBTIENE UN DOMINIO", "*"*30)
    dominio = "baliancer.com"
    response = requests.get(f"{BASE_URL_API}/dominio/{dominio}")
    print("\nCódigo Respuesta Obtiene Dominio:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_06_lista_todos_los_dominios():
    """Lista todos los dominios."""
    print("*"*30, "OBTIENE TODOS LOS DOMINIOS", "*"*30)
    response = requests.get(f"{BASE_URL_API}/dominios")
    print("\nCódigo Respuesta Lista Todos los Dominios:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

# --- PRUEBAS DE ACTUALIZACIÓN (PATCH) ---

def test_07_actualiza_dominio_1_etiquetas():
    """Actualiza dominio 1 con estado y etiquetas."""
    print("*"*30, "ACTUALIZA DOMINIO 1", "*"*30)
    dominio = "baliancer.com"
    datos = {"estado_dominio": "Malicioso", "etiquetas": ["phishing"]}
    response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
    print("\nRespuesta Actualiza Dominio 1:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_08_actualiza_dominio_2_fuentes():
    """Actualiza dominio 2 con fuentes de reputación."""
    print("*"*30, "ACTUALIZA DOMINIO 2", "*"*30)
    dominio = "beritapb.com"
    datos = {"estado_dominio": "Malicioso", "fuentes_reputacion": [{"manual": 80}]}
    response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
    print("\nRespuesta Actualiza Dominio 2:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_09_actualiza_dominio_inexistente_falla():
    """Intenta actualizar un dominio que no existe (espera que no sea 200)."""
    print("*"*30, "ACTUALIZA DOMINIO QUE NO EXISTE", "*"*30)
    dominio = "gato1.com"
    datos = {"estado_dominio": "Malicioso"}
    response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
    print("\nRespuesta Actualiza Dominio que no existe:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code != 200

def test_10_actualiza_estado_dominio_erroneo_falla():
    """Intenta actualizar con estado de dominio incorrecto (espera que no sea 200)."""
    print("*"*30, "ACTUALIZA CON ESTADO DOMINIO ERRONEO", "*"*30)
    dominio = "baliancer.com"
    datos = {"estado_dominio": "Penoso"}
    response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
    print("\nRespuesta Actualiza con estado dominio erroneo:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code != 200

def test_11_actualiza_formato_reputacion_erroneo_falla():
    """Intenta actualizar con formato de reputación incorrecto (espera que no sea 200)."""
    print("*"*30, "ACTUALIZA CON FORMATO DE REPUTACION ERRONEO", "*"*30)
    dominio = "baliancer.com"
    datos = {"fuentes_reputacion": [{"manual": "80"}]} # Valor de score como string
    response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
    print("\nRespuesta Actualiza con formato de reputacion erroneo:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code != 200

def test_12_actualiza_formato_etiquetas_erroneo_falla():
    """Intenta actualizar con formato de etiquetas incorrecto (espera que no sea 200)."""
    print("*"*30, "ACTUALIZA CON FORMATO DE ETIQUETAS ERRONEO", "*"*30)
    dominio = "baliancer.com"
    datos = {"etiquetas": "Suplantacion"} # Valor de etiquetas como string, no lista
    response = requests.patch(f"{BASE_URL_API}/dominio/{dominio}", json=datos)
    print("\nRespuesta Actualiza con formato de etiquetas erroneo:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code != 200

# --- PRUEBAS DE LISTADO POR FILTRO (GET) ---

def test_13_lista_dominios_por_estado_desconocido():
    """Lista dominios por estado 'Desconocido'."""
    print("*"*30, "LISTA DOMINIOS POR ESTADO DESCONOCIDO", "*"*30)
    estado_dominio = "Desconocido"
    response = requests.get(f"{BASE_URL_API}/dominios/estado/{estado_dominio}")
    print("\nRespuesta Lista Dominios/Estado:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_14_lista_dominios_por_estado_malicioso():
    """Lista dominios por estado 'Malicioso'."""
    print("*"*30, "LISTA DOMINIOS POR ESTADO MALICIOSO", "*"*30)
    estado_dominio = "Malicioso"
    response = requests.get(f"{BASE_URL_API}/dominios/estado/{estado_dominio}")
    print("\nRespuesta Lista Dominios/Estado:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_15_lista_dominios_por_score_menor_40():
    """Lista dominios por score menor de 40."""
    print("*"*30, "LISTA DOMINIOS POR SCORE MENOR DE 40", "*"*30)
    score = 40
    response = requests.get(f"{BASE_URL_API}/dominios/reputacion/{score}")
    print("\nRespuesta Lista Dominios/Score:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_16_lista_dominios_con_servidor_correo():
    """Lista dominios que DISPONEN de servidor de correo (MX=True)."""
    print("*"*30, "LISTA DOMINIOS QUE DISPONEN DE SERVIDOR DE CORREO", "*"*30)
    mx = True
    response = requests.get(f"{BASE_URL_API}/dominios/mx/{mx}")
    print("\nRespuesta Lista Dominios con MX:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_17_lista_dominios_sin_servidor_correo():
    """Lista dominios que NO DISPONEN de servidor de correo (MX=False)."""
    print("*"*30, "LISTA DOMINIOS QUE NO DISPONEN DE SERVIDOR DE CORREO", "*"*30)
    mx = False
    response = requests.get(f"{BASE_URL_API}/dominios/mx/{mx}")
    print("\nRespuesta Lista Dominios sin MX:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

# --- PRUEBAS DE ELIMINACIÓN (DELETE) ---

def test_18_elimina_un_dominio():
    """Elimina un dominio existente (leon.com)."""
    print("*"*30, "ELIMINA UN DOMINIO", "*"*30)
    dominio = "leon.com"
    response = requests.delete(f"{BASE_URL_API}/dominio/{dominio}")
    print("\nRespuesta Elimina Dominio:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code == 200

def test_19_elimina_dominio_que_no_existe_falla():
    """Intenta eliminar un dominio que no existe (espera que no sea 200)."""
    print("*"*30, "ELIMINA UN DOMINIO QUE NO EXISTE", "*"*30)
    dominio = "gato1.com"
    response = requests.delete(f"{BASE_URL_API}/dominio/{dominio}")
    print("\nRespuesta Elimina Dominio que no existe:", response.status_code)
    print("Contenido Respuesta:", response.json(), "\n")
    assert response.status_code != 200

# --- FIN DE PRUEBAS ---

def test_20_final_message():
    """Imprime mensaje de éxito si todos los tests pasan."""
    print("*"*30, "PASADAS TODAS LAS PRUEBAS CON EXITO", "*"*30, "\n\n")