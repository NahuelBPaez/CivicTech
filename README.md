# CivicTech

## Plataforma de Tecnología Cívica Colaborativa para Gestión de Reportes Viales

**Universidad Nacional de Chilecito (UNdeC)**
**Materia:** Base de Datos II – Trabajo Integrador

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostGIS-155E95?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

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

## PostgreSQL

El sistema utiliza PostgreSQL como motor principal debido a:

* Soporte de propiedades ACID.
* Integridad referencial mediante claves foráneas.
* Alta confiabilidad transaccional.
* Escalabilidad y seguridad.

---

## PostGIS

La extensión PostGIS permite trabajar con datos geográficos de forma nativa.

Se utiliza el tipo:

```sql
GEOMETRY(Point, 4326)
```

Esto permite:

* Almacenar coordenadas GPS.
* Realizar consultas espaciales.
* Generar mapas de calor.
* Validar jurisdicciones municipales.

---

## Object Storage

Las imágenes no se almacenan directamente dentro de PostgreSQL.

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

# Modelo Relacional

El sistema se compone de tres entidades principales:

* Usuario
* Reporte
* Evidencia

---

# Relaciones

## Usuario (1:N) Reporte

Un usuario puede generar múltiples reportes.

---

## Reporte (1:N) Evidencia

Un reporte puede contener múltiples evidencias fotográficas.

---

# Diccionario de Datos

## Tabla: Usuario

```sql
CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre_apellido VARCHAR(255) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    reputacion INT DEFAULT 100,
    email VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL
);
```

### Descripción

| Campo           | Descripción                 |
| --------------- | --------------------------- |
| id_usuario      | Identificador único         |
| nombre_apellido | Nombre completo del usuario |
| dni             | Documento único             |
| reputacion      | Puntaje de reputación       |
| email           | Correo electrónico          |
| contrasena      | Contraseña cifrada          |

---

## Tabla: Reporte

```sql
CREATE TABLE Reporte (
    id_reporte SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    patente_vehiculo VARCHAR(15) NOT NULL,
    fechaHora_dispositivo TIMESTAMP NOT NULL,
    fechaHora_server TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ubicacion GEOMETRY(Point, 4326) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    hash_evidencia VARCHAR(64),
    descripcion TEXT,

    FOREIGN KEY (id_usuario)
    REFERENCES Usuario(id_usuario)
);
```

### Descripción

| Campo                 | Descripción                    |
| --------------------- | ------------------------------ |
| id_reporte            | Identificador del reporte      |
| id_usuario            | Usuario que realizó el reporte |
| patente_vehiculo      | Patente del vehículo           |
| fechaHora_dispositivo | Fecha y hora del dispositivo   |
| fechaHora_server      | Fecha y hora del servidor      |
| ubicacion             | Coordenadas GPS                |
| estado                | Estado del reporte             |
| hash_evidencia        | Hash SHA-256                   |
| descripcion           | Información adicional          |

---

## Tabla: Evidencia

```sql
CREATE TABLE Evidencia (
    id_evidencia SERIAL PRIMARY KEY,
    id_infraccion INT NOT NULL,
    url_foto TEXT,
    url_archivo_s3 TEXT,
    hash_seguridad_sha VARCHAR(64),

    FOREIGN KEY (id_infraccion)
    REFERENCES Reporte(id_reporte)
);
```

### Descripción

| Campo              | Descripción                  |
| ------------------ | ---------------------------- |
| id_evidencia       | Identificador de evidencia   |
| id_infraccion      | Referencia al reporte        |
| url_foto           | URL de imagen                |
| url_archivo_s3     | URL del almacenamiento cloud |
| hash_seguridad_sha | Hash de integridad           |

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
