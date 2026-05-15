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

El sistema opera bajo un modelo **B2G (Business to Government)**, conectando la participación ciudadana directamente con los paneles de control de las autoridades de tránsito.

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
