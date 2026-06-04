# CivicTech

## Plataforma de Tecnología Cívica Colaborativa para Gestión de Reportes Viales

**Universidad Nacional de Chilecito (UNdeC)**  
**Materia:** Base de Datos II – Trabajo Integrador

![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![GeoJSON](https://img.shields.io/badge/GeoJSON-EAA221?style=for-the-badge&logo=geojson&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
---

# Introducción

CivicTech es una propuesta de plataforma colaborativa orientada al ordenamiento vial urbano mediante el uso de tecnologías de bases de datos NoSQL, geolocalización y almacenamiento seguro de evidencia digital.

El objetivo principal del sistema es permitir que los ciudadanos registren reportes de infracciones viales desde una aplicación móvil, mientras que las autoridades municipales pueden validar la información desde un panel administrativo.

El proyecto se centra especialmente en el diseño de una arquitectura de persistencia robusta utilizando MongoDB, priorizando:

* Flexibilidad documental para representar entidades sin necesidad de esquemas rígidos.

* Escalabilidad horizontal mediante replicación y sharding, asegurando crecimiento regional o nacional.

* Procesamiento geoespacial con índices 2dsphere y datos en formato GeoJSON para validar jurisdicciones municipales y generar mapas de calor.

* Trazabilidad de la evidencia mediante almacenamiento seguro en la nube y hash criptográfico.

* Seguridad y control de acceso con autenticación, cifrado y roles para proteger datos ciudadanos.

---

# Problemática

Las ciudades presentan problemas crecientes relacionados con:

* Estacionamiento en doble fila.
* Bloqueo de rampas y sendas peatonales.
* Obstrucción del espacio público.
* Falta de control vial eficiente.

Actualmente, muchos municipios no cuentan con herramientas tecnológicas que permitan:

* Recibir reportes ciudadanos estructurados.
* Validar evidencia digital.
* Gestionar información geográfica.
* Mantener auditoría e integridad de los datos.

---

# Objetivo del Proyecto

Diseñar un sistema de base de datos orientado a la gestión de reportes viales que permita:

* Registrar evidencia digital.
* Asociar coordenadas GPS.
* Garantizar integridad mediante hashing.
* Mantener relaciones logicas
* Optimizar consultas espaciales.

---

# Arquitectura de Persistencia

## MongoDB

El sistema utiliza MongoDB como motor principal debido a:

* **Flexibilidad de documentos:** Los datos se almacenan en formato BSON/JSON, lo que permite representar entidades como Usuario, Reporte, Evidencia y Municipio de manera natural, sin necesidad de un esquema rígido. Esto facilita la evolución del modelo cuando se agregan nuevas colecciones o campos.

* **Escalabilidad horizontal:** MongoDB soporta sharding y replicación nativa, lo que permite distribuir los reportes y evidencias entre múltiples nodos. Esto es clave para un sistema de tecnología cívica que puede crecer a nivel regional o nacional.

* **Índices geoespaciales:** A través de índices 2dsphere, MongoDB permite realizar consultas eficientes sobre coordenadas GPS, como detectar vehículos en rampas o generar mapas de calor de infracciones.

* **Alta disponibilidad:** La replicación automática asegura tolerancia a fallos y continuidad del servicio, garantizando que los reportes ciudadanos estén siempre accesibles.

* **Seguridad y control de acceso  :** MongoDB ofrece autenticación, cifrado en tránsito y en reposo, y control de roles, lo que protege la evidencia digital y los datos personales de los usuarios.

* **Integridad lógica en la aplicación:** Aunque MongoDB no implementa claves foráneas como un motor relacional, la integridad se asegura mediante referencias (ObjectId) y validaciones en la capa DAO. Esto permite mantener consistencia entre Usuario, Reporte y Evidencia, además de registrar las acciones de los agentes municipales sobre la reputación.


---

## Geoespacial en MongoDB
MongoDB permite trabajar con datos geográficos de forma nativa mediante el estándar GeoJSON y los índices 2dsphere.

Se utiliza el tipo:
```Json
{ "type": "Point", "coordinates": [longitud, latitud] }

```
Esto permite:

* Almacenar coordenadas GPS directamente en los documentos.
* Realizar consultas espaciales con operadores como $near, $geoWithin y $geoIntersects.
* Generar mapas de calor y estadísticas de densidad de infracciones.
* Validar jurisdicciones municipales mediante polígonos GeoJSON asociados a cada municipio.

Ejemplo de índice geoespacial:
```Json
db.reporte.createIndex({ ubicacion: "2dsphere" })

```
---

## Object Storage

Las imágenes no se almacenan directamente dentro de MongoDB.

Se utiliza almacenamiento externo tipo:

* Amazon S3
* Google Cloud Storage

En la base de datos únicamente se almacena:

* URL del archivo.
* Hash SHA-256.
* Metadatos asociados.

---


## Requisitos previos

* **Docker Desktop** instalado y en ejecución.
* **Git** instalado (para clonar el repo).
* **MongoDB Compass** o **mongosh** disponibles para ejecutar el script.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/NahuelBPaez/CivicTech.git
cd CivicTech
```
---- 

## 2. Configurar las variables de entorno

Copiá el archivo de ejemplo y completá tus credenciales:

```bash
cp prueba.env .env
nano .env
```

Editá .env con tus valores.

```Bash
# Conexión a MongoDB (contenedor en Docker Desktop)
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB_NAME=civictech
MONGO_USER=admin
MONGO_PASSWORD=adminpass
JUPYTER_PORT=8888
```
**Nota:** estas variables son usadas por los notebooks y la futura DAO para construir la URI de conexión. No subas .env al repo; añadilo a .gitignore.

### Entorno y dependencias  
Crear y activar entorno virtual
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```
#### Windows PowerShell
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Instalar dependencias
```bash
pip install --upgrade pip
pip uninstall -y bson || true
pip install -r requirements.txt
```

requirements.txt sugerido
```bash
pymongo>=4.0
python-dotenv>=1.0
jupyterlab>=4.0
pandas>=2.0
dnspython>=2.0
```

---

### 3. Levantar MongoDB usando Docker Desktop (pasos sencillos)
1. Abrí Docker Desktop y confirmá que está corriendo.

2. Crear el contenedor MongoDB (dos opciones):

### Opción A — Interfaz gráfica (Docker Desktop):

* En Docker Desktop → Images → buscá la imagen mongo:6 (o la versión que prefieras) y hacé Run.

* En la ventana de ejecución:

  * **Container name:** mongo_civictech

  * **Ports:** mapear 27017 → 27017 (Host:Container)

  * **Volumes:** opcionalmente mapear un volumen local para persistencia (ej. ./data/db:/data/db)

  * **Environment (opcional):** MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD si querés autenticación.

* Iniciá el contenedor.


  
### Opción B — Línea de comandos (rápido):
**Sin autenticación (útil para desarrollo local)**  
  
Opción 1 — Mongo 6 (si tu CPU soporta AVX):

```Bash
docker run -d --name mongo_civictech -p 27017:27017 -v "$PWD/data/db:/data/db" mongo:6

```
  
Opción 2 — Mongo 4.4 (para CPUs sin AVX, más compatible):

```Bash
docker run -d --name mongo_civictech -p 27017:27017 -v "$PWD/data/db:/data/db" mongo:4.4

```

  
**Con usuario root (si querés autenticación)**  
Opción 1 — Mongo 6 (si tu CPU soporta AVX):  

```Bash
docker run -d --name mongo_civictech -p 27017:27017 -v "$PWD/data/db:/data/db" -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=adminpass mongo:6

```
Opción 2 — Mongo 4.4 (para CPUs sin AVX, más compatible):  

```Bash
docker run -d --name mongo_civictech -p 27017:27017 -v "$PWD/data/db:/data/db" -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=adminpass mongo:4.4

```



  
3. Verificá en Docker Desktop que el contenedor esté Running y sin errores en los logs.

---

### 4. Conectar MongoDB Compass  

1. Abrí MongoDB Compass.

2. Cadena de conexión:

```Bash
mongodb://admin:adminpass@localhost:27017/?authSource=admin
```
3. Conectate y seleccioná la base civictech (si no existe, el script la creará al insertar).

---

### 5. Ejecutar el script en (MongoDB Compass)
En el repo tenés script_mongo.js. Abrilo y copiá todo su contenido.

En Compass:  
1. Si es la primera vez, creá una nueva base de datos llamada "civictech".  
2. Compass te pedirá también una colección inicial: usá "municipio" (coincide con el script).  
3. Una vez creada, seleccioná la base "civictech" en el panel izquierdo.  
4. Abrí **Open MongoDB Shell** desde Compass (ícono superior derecho).  
5. Pegá el contenido completo de script_mongo.js en la consola del Shell.  
6. Ejecutá los comandos para crear colecciones, índices y datos de prueba.  

### Alternativa por consola(mongosh):  
```Bash
mongosh --username admin --password 'adminpass' --authenticationDatabase admin civictech --file script_mongo.js
```
### Verificación rápida
##### En Compass:  
1. Abrí Open MongoDB Shell desde Compass (ícono superior derecho).
2. Copiá y pegá el contenido de Checklist_script_mongo.js en la consola del Shell.
3. Ejecutá los comandos para confirmar que las colecciones, índices y datos se crearon correctamente.  

#### En mongosh (consola): 
```Bash
mongosh --username admin --password 'adminpass' --authenticationDatabase admin civictech --file Checklist_script_mongo.js
```

Detalles del script:  
* El script es autocontenido: intenta dropear colecciones existentes (si tu usuario tiene permiso readWrite), crea colecciones, índices y datos de prueba, y define una función local para validar que usuario.municipio_id === reporte.municipio_id.  
* Si hay timeout o error por tamaño, ejecutá el script por bloques en este orden: colecciones → municipios → usuarios → función local → reportes → evidencias/agentes.


---




### 4. Acceder a JupyterLab

Abrí el navegador en:

```
http://localhost:8888
```

Los notebooks disponibles son:
- `prueba_dao.ipynb` — pruebas CRUD con la capa DAO en Python
- `consultas_sql.ipynb` — consultas SQL directas con jupysql

---

## Reiniciar la base de datos desde cero

Si necesitás resetear completamente la base de datos (por ejemplo, tras modificar `dbscripts.sql`):

```bash
docker-compose down -v
docker-compose up --build
```

> El flag `-v` elimina el volumen de datos. Sin él, Postgres no vuelve a ejecutar el script de inicialización.

---

## Estructura del proyecto

```
CivicTech/
├── db_models/
│   ├── __init__.py
│   ├── usuario.py
│   ├── reporte.py
│   └── evidencia.py
├── dao.py
├── config_vars.py
├── dbscripts.sql
├── docker-compose.yml
├── Dockerfile
├── libs.txt
├── prueba_dao.ipynb
├── consultas_sql.ipynb
├── prueba.env
└── .gitignore
```

---

# Modelo de Datos en MongoDB

El sistema se compone de cinco colecciones principales:

* Usuario
* Reporte
* Evidencia
* Municipio
* AgenteMunicipal

---

# Relaciones

## Usuario (1:N) Reporte

Un usuario puede generar múltiples reportes.  
Se mantiene mediante la referencia usuario_id en la colección Reporte.


## Reporte (1:N) Evidencia

Un reporte puede contener múltiples evidencias fotográficas.  
Se mantiene mediante la referencia reporte_id en la colección Evidencia.

## Municipio (1:N) Reporte  
Cada reporte pertenece a un municipio específico.  
Se mantiene mediante la referencia municipio_id en la colección Reporte.

## Municipio (1:N) AgenteMunicipal  
Cada agente municipal está asociado a un municipio.  
Se mantiene mediante la referencia municipio_id en la colección AgenteMunicipal.

## AgenteMunicipal (N:M) Usuario  
Los agentes municipales pueden validar reportes y ajustar la reputación de distintos usuarios.  
Se registra en el arreglo acciones dentro de la colección AgenteMunicipal, que guarda usuario_id, reporte_id y el reputacion_delta.

---

# Diccionario de Datos

## Colección: Usuario

```Json
{
  "_id": ObjectId,
  "nombre_apellido": "Juan Pérez",
  "dni": "12345678",
  "reputacion": 95,
  "email": "juan@example.com",
  "contrasena": "hash_bcrypt",
  "municipio_id": ObjectId("ID_CHILECITO")
}
```


### Descripción

| Campo           | Descripción                      |
| --------------- | --------------------------------------------------------|
|``_id``             | Identificador único del documento,indice unico          |
|``nombre_apellido`` | Nombre completo del usuario                             |
|``dni``             | Documento único                                         |
|``reputacion``      | Puntaje de reputación, ajustado por agentes municipales.|
|``email``           | Correo electrónico, indice unico.                       |
|``contrasena``      | Contraseña cifrada(hash)                                |
|``municipio_id``    | Referencia obligatoria al municipio donde el usuario está registrado|  

Regla: cada usuario pertenece a un único municipio.
  
---


## Colección: Reporte

```Json
{
  "_id": ObjectId,
  "usuario_id": ObjectId("ID_USUARIO_CHILECITO"),
  "municipio_id": ObjectId("ID_CHILECITO"),
  "patente_vehiculo": "ABC123",
  "fechaHora_dispositivo": ISODate("2026-06-02T15:00:00Z"),
  "fechaHora_server": ISODate(),
  "ubicacion": { "type": "Point", "coordinates": [-66.85, -29.42] },
  "estado": "Pendiente",
  "hash_evidencia": "sha256...",
  "descripcion": "Vehículo bloqueando rampa",
  "validador_id": ObjectId("ID_AGENTE")
}

```




### Descripción

| Campo | Descripción |
| ---- | --- |
| ``_id`` | Identificador único del reporte. |
| ``usuario_id`` | Referencia al usuario que generó el reporte. |
| ``municipio_id`` | Referencia al municipio donde ocurrió la infracción. |
| ``patente_vehiculo`` | Patente del vehículo reportado. |
| ``fechaHora_dispositivo`` | Fecha y hora registrada por el dispositivo. |
| ``fechaHora_server`` | Fecha y hora registrada por el servidor. |
| ``ubicacion`` | Coordenadas GPS en formato GeoJSON (``Point``). |
| ``estado`` | Estado del reporte: Pendiente, Validada, Rechazada. |
| ``hash_evidencia`` | Hash SHA-256 de la evidencia asociada. |
| ``descripcion`` | Información adicional del reporte. |
| ``validador_id`` | Referencia al agente municipal que validó. |  

Regla de negocio: usuario.municipio_id debe coincidir con reporte.municipio_id. 

---

## Colección: Evidencia

```Json
{
  "_id": ObjectId,
  "reporte_id": ObjectId,
  "url_foto": "http://...",
  "url_archivo_s3": "s3://bucket/file.jpg",
  "hash_seguridad_sha": "sha256..."
}

```

### Descripción

| Campo | Descripción |
| --- | --- |
| ``_id`` | Identificador único de la evidencia. |
| ``reporte_id`` | Referencia al reporte asociado. |
| ``url_foto`` | URL de la imagen. |
| ``url_archivo_s3`` | URL del archivo en almacenamiento externo. |
| ``hash_seguridad_sha`` | Hash de integridad de la evidencia. |

---

### Colección: Municipio
```Json
{
  "_id": ObjectId,
  "nombre": "Chilecito",
  "provincia": "La Rioja",
  "pais": "Argentina",
  "codigo_municipio": "CHL001",
  "contacto": {
    "email": "transito@chilecito.gob.ar",
    "telefono": "+54 3825 123456"
  }
}

```
### Descripción

| Campo | Descripción |
| --- | --- |
| ``_id`` | Identificador único del municipio. |
| ``nombre`` | Nombre de la ciudad o municipio. |
| ``provincia`` | Provincia a la que pertenece. |
| ``pais`` | País. |
| ``codigo_municipio`` | Código único de municipio. |
| ``contacto.email`` | Correo de contacto oficial. |
| ``contacto.telefono`` | Teléfono de contacto oficial. |

---

### Colección: AgenteMunicipal

```Json
{
  "_id": ObjectId,
  "nombre_apellido": "María Gómez",
  "dni": "30111222",
  "email": "mgomez@chilecito.gob.ar",
  "rol": "Inspector",
  "municipio_id": ObjectId,
  "acciones": [
    {
      "reporte_id": ObjectId,
      "usuario_id": ObjectId,
      "fecha_accion": ISODate("2026-06-02T15:00:00Z"),
      "tipo_accion": "AjusteReputacion",
      "reputacion_delta": -10
    }
  ]
}

```

| Campo | Descripción |
| --- | --- |
| ``_id`` | Identificador único del agente municipal. |
| ``nombre_apellido`` | Nombre completo del agente. |
| ``dni`` | Documento único del agente. |
| ``email`` | Correo institucional. |
| ``rol`` | Rol dentro del municipio (ej. Inspector). |
| ``municipio_id`` | Referencia al municipio al que pertenece. |
| ``acciones.reporte_id`` | Reporte sobre el que actuó. |
| ``acciones.usuario_id`` | Usuario cuya reputación fue ajustada. |
| ``acciones.fecha_accion`` | Fecha de la acción realizada. |
| ``acciones.tipo_accion`` | Tipo de acción: Validación, Rechazo, AjusteReputacion. |
| ``acciones.reputacion_delta`` | Variación aplicada a la reputación del usuario. |

---

# Restricciones Implementadas

## Restricciones de Estado
Garantiza que el estado del reporte solo pueda contener valores válidos.  
La validación se implementa de la siguiente manera:   

* **Documentación en el Diccionario de Datos**  
En la colección **Reporte**, el campo estado se define con valores permitidos:

  * Pendiente
  * Validada
  * Rechazada

* **Validación en la base de datos**  
Se puede usar un validador de esquema para garantizar que solo se inserten valores válidos:

```Json
db.createCollection("reporte", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["estado"],
      properties: {
        estado: {
          enum: ["Pendiente", "Validada", "Rechazada"]
        }
      }
    }
  }
})

```


---

## Restricciones Únicas  
En MongoDB se implementan mediante índices únicos para evitar duplicación de usuarios:

```Json
db.usuario.createIndex({ dni: 1 }, { unique: true })
db.usuario.createIndex({ email: 1 }, { unique: true })
```

---

## Referencias (Claves Foráneas)

La integridad se asegura mediante referencias ObjectId y validaciones en la aplicación:

* Usuario → Reporte: usuario_id en la colección Reporte.
* Reporte → Evidencia: reporte_id en la colección Evidencia.
* Municipio → Reporte / AgenteMunicipal: municipio_id en las colecciones correspondientes.

---

# Índices

## Índices Geoespaciales
En MongoDB se implementa 2dsphere:
```Json
db.reporte.createIndex({ ubicacion: "2dsphere" })
```
Permite consultas con $near, $geoWithin y $geoIntersects sobre coordenadas GPS en formato GeoJSON.


---

## Índice por Patente

Optimiza búsquedas de vehículos reportados:
```Json
db.reporte.createIndex({ patente_vehiculo: 1 })

```

---

# Capa DAO (Data Access Object)

El proyecto implementa una capa DAO en Python utilizando `psycopg2`.

## Clases principales

* `ConexionDB`
* `UsuarioDAO`
* `ReporteDAO`
* `EvidenciaDAO`

Esta arquitectura permite:

* Separar lógica de negocio y acceso a datos.
* Facilitar mantenimiento.
* Centralizar operaciones CRUD.

---

# Tecnologías Utilizadas

| Tecnología   | Uso                        |
| ------------ | -------------------------- |
| PostgreSQL   | Base de datos relacional   |
| PostGIS      | Procesamiento geoespacial  |
| Python       | Lógica backend             |
| psycopg2     | Conexión PostgreSQL        |
| AWS S3 / GCP | Almacenamiento de archivos |

---

# Conclusión

CivicTech propone una solución tecnológica enfocada en la gestión de reportes viales mediante una arquitectura de datos robusta y escalable.

La utilización de PostgreSQL junto con PostGIS permite garantizar:

* Integridad referencial.
* Procesamiento geográfico eficiente.
* Seguridad de la información.
* Trazabilidad de la evidencia digital.

El proyecto demuestra la aplicación práctica de conceptos fundamentales de Bases de Datos como:

* Modelado relacional.
* Restricciones.
* Integridad.
* Índices.
* Persistencia geoespacial.
* Arquitectura DAO.

---
## Notas Técnicas y Consideraciones

- **Uso de BSON en Python**  
  MongoDB ya incluye su propia implementación de `bson` dentro de `pymongo`.  
  ✔️ Evitá instalar el paquete externo `bson` para prevenir conflictos.  
  ✔️ Si aparece un error de importación, eliminá el paquete externo y asegurate de usar solo el que viene con `pymongo`.

- **Fechas y zona horaria en Python 3.12+**  
  La función `datetime.utcnow()` está deprecada.  
  ✔️ Usar en su lugar:
  ```python
  from datetime import datetime, timezone
  datetime.now(timezone.utc)

----

# Autores

Trabajo Integrador – Base de Datos II
Universidad Nacional de Chilecito (UNdeC)

* Nombre y Apellido
* Nombre y Apellido

Año: 2026
