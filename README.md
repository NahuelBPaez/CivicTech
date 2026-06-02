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

CivicTech es una propuesta de plataforma colaborativa orientada al ordenamiento vial urbano mediante el uso de tecnologías de bases de datos, geolocalización y almacenamiento seguro de evidencia digital.

El objetivo principal del sistema es permitir que los ciudadanos registren reportes de infracciones viales desde una aplicación móvil, mientras que las autoridades municipales pueden validar la información desde un panel administrativo.

El proyecto se centra especialmente en el diseño de una arquitectura de persistencia robusta utilizando PostgreSQL y PostGIS, priorizando:

* Integridad referencial.
* Trazabilidad de la evidencia.
* Consistencia transaccional.
* Procesamiento geoespacial.

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
* Mantener relaciones consistentes entre entidades.
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

- [Docker](https://www.docker.com/get-started) y Docker Compose instalados
- [Git](https://git-scm.com/) instalado

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/NahuelBPaez/CivicTech.git
cd CivicTech
```

### 2. Configurar las variables de entorno

Copiá el archivo de ejemplo y completá tus credenciales:

```bash
cp prueba.env .env
```

Editá `.env` con tus valores:

```env
DB_HOST=db
DB_PORT=5432
DB_NAME=civictech_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_secreta
```


### 3. Levantar los contenedores

```bash
docker-compose up --build
```

Esto levanta dos servicios:
- **`db`** — PostgreSQL 16 con PostGIS. Ejecuta `dbscripts.sql` automáticamente y carga los datos de prueba.
- **`jupyter`** — JupyterLab disponible en [http://localhost:8888](http://localhost:8888)

> La primera vez puede tardar unos minutos mientras se descarga la imagen de PostGIS.

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

---

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
  "contrasena": "hash_bcrypt"
}
```

### Descripción

| Campo           | Descripción                      |
| --------------- | --------------------------------------------------------|
|``_id``             | Identificador único del documento                       |
|``nombre_apellido`` | Nombre completo del usuario                             |
|``dni``             | Documento único                                         |
|``reputacion``      | Puntaje de reputación, ajustado por agentes municipales.|
|``email``           | Correo electrónico                                      |
|``contrasena``      | Contraseña cifrada(hash)                                |

---


## Colección: Reporte

```Json
{
  "_id": ObjectId,
  "usuario_id": ObjectId,
  "municipio_id": ObjectId,
  "patente_vehiculo": "ABC123",
  "fechaHora_dispositivo": ISODate("2026-06-02T15:00:00Z"),
  "fechaHora_server": ISODate(),
  "ubicacion": { "type": "Point", "coordinates": [-66.85, -29.42] },
  "estado": "Pendiente",
  "hash_evidencia": "sha256...",
  "descripcion": "Vehículo bloqueando rampa",
  "validador_id": ObjectId
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

## Restricción CHECK

```sql
CONSTRAINT chk_estado_reporte
CHECK (estado IN ('Pendiente', 'Validada', 'Rechazada'))
```

Garantiza que el estado del reporte solo pueda contener valores válidos.

---

## Restricciones UNIQUE

Aplicadas sobre:

* `dni_cuil`
* `email`

Evitan duplicación de usuarios.

---

## Claves Foráneas

Permiten mantener integridad referencial entre:

* Usuario → Reporte
* Reporte → Evidencia

---

# Índices

## Índice Espacial GIST

```sql
CREATE INDEX idx_reporte_ubicacion
ON Reporte USING GIST (ubicacion);
```

Optimiza consultas geográficas realizadas con PostGIS.

---

## Índice por Patente

```sql
CREATE INDEX idx_reporte_patente
ON Reporte (patente_vehiculo);
```

Optimiza búsquedas de vehículos.

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

# Autores

Trabajo Integrador – Base de Datos II
Universidad Nacional de Chilecito (UNdeC)

* Nombre y Apellido
* Nombre y Apellido

Año: 2026
