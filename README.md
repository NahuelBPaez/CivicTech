# CivicTech
## Plataforma Tecnología Cívica Colaborativa  
Universidad Nacional de Chilecito (UNdeC) – Base de Datos II – Trabajo Integrador

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostGIS-155E95?style=for-the-badge&logo=postgresql&logoColor=white)
![Cloud Storage](https://img.shields.io/badge/Cloud_Storage-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Status](https://img.shields.io/badge/Status-En_Desarrollo-green)

## ¿Cuál es el problema?
Las ciudades enfrentan un colapso en la movilidad urbana debido a infracciones de tránsito frecuentes y difíciles de controlar. El estacionamiento en doble fila, el bloqueo de rampas y sendas peatonales generan riesgos para peatones, afectan la accesibilidad de personas con movilidad reducida y aumentan la frustración ciudadana por la falta de control estatal efectivo. Los municipios carecen de herramientas ágiles y confiables para recibir, organizar y validar reportes ciudadanos de manera estructurada.

## ¿Qué es CivicTech?
CivicTech (tecnología cívica) es el uso de soluciones digitales para fortalecer la participación ciudadana, mejorar la transparencia y facilitar la colaboración entre sociedad y gobierno. Se trata de aplicaciones y plataformas que convierten a los ciudadanos en actores activos de la gestión pública, permitiéndoles reportar problemas, aportar datos y colaborar en la construcción de ciudades más ordenadas y accesibles.
En este contexto, una app CivicTech transforma el teléfono móvil en una herramienta de control social: el ciudadano captura evidencia (fotografía, ubicación GPS, estampa de tiempo) y la plataforma la estructura con mecanismos de seguridad como hashing y metadatos, garantizando la integridad de la información.

---

##  Características Principales

### Para el Ciudadano (App Móvil)
* **Captura Estructurada:** Registro automático de la fecha, hora (servidor/dispositivo) y coordenadas exactas (GPS).
* **Anonimización:** Sistema diseñado para proteger la identidad del denunciante, procesando únicamente los datos del vehículo infractor en la vía pública.
* **Integridad Legal:** Generación de un Hash SHA-256 en el momento de la captura para garantizar la inalterabilidad de la evidencia frente a futuras auditorías.

### Para el Estado (Dashboard Gubernamental)
* **Validación Espacial:** Cruce automático de las coordenadas de la infracción con las zonas jurisdiccionales del municipio.
* **Flujo de Aprobación:** Panel exclusivo para agentes de tránsito matriculados, quienes validan la prueba documental y proceden a la sanción.
* **Trazabilidad Absoluta:** Base de datos relacional estricta para garantizar que no existan inconsistencias legales ante impugnaciones.

---

##  Arquitectura Técnica

Para garantizar el cumplimiento de normativas legales y la solidez de las auditorías, ExomSystem utiliza una arquitectura de persistencia 100% relacional:

1. **Base de Datos Principal:** `PostgreSQL`
   * Maneja toda la lógica del negocio: Usuarios, Vehículos, Tipos de Infracción y el registro transaccional de las denuncias.
   * Garantiza propiedades ACID, asegurando integridad referencial estricta.

2. **Motor Geoespacial:** `PostGIS` (Extensión de PostgreSQL)
   * Permite almacenar las ubicaciones en formato `Geometry/Point`.
   * Facilita consultas espaciales complejas (ej. *¿Está esta coordenada dentro de un polígono de zona de exclusión?*).

3. **Almacenamiento Multimedia:** `Object Storage (AWS S3 / GCP)`
   * Las fotografías y evidencias pesadas se almacenan en la nube.
   * La base de datos PostgreSQL almacena únicamente la URL segura del archivo y su hash criptográfico.

---

##  Esquema de Datos Relacional (MER Básico)

El modelo de datos está diseñado para evitar datos huérfanos y asegurar la trazabilidad:

* **`Usuarios`**: Registra al ciudadano denunciante (ID, DNI Validado, Reputación).
* **`Tipos_Infraccion`**: Tabla maestra con la normativa legal (Artículos, Montos de referencia).
* **`Infracciones`**: Tabla central que vincula al Usuario, el Tipo de Falta, la Patente y la Ubicación (PostGIS).
* **`Evidencias`**: Entidad asociada a la infracción que guarda la URL de S3 y el Hash SHA-256 de las fotografías.

---

##  Instalación y Ejecución Local

### Prerrequisitos
* [Docker](https://www.docker.com/) y Docker Compose (Recomendado para levantar la base de datos fácilmente).
* PostgreSQL 15+ (si se instala de forma nativa).
* PostGIS habilitado en la instancia de base de datos.

### Pasos de Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/ExomSystem.git](https://github.com/tu-usuario/ExomSystem.git)
   cd ExomSystem


# CivicTech

## Plataforma de Tecnología Cívica Colaborativa para Gestión de Reportes Viales

**Universidad Nacional de Chilecito (UNdeC)**
**Materia:** Base de Datos II – Trabajo Integrador

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
    dni_cuil VARCHAR(20) UNIQUE NOT NULL,
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
| dni_cuil        | Documento único             |
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
