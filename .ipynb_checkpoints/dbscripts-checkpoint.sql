-- =====================================================================
-- EXOMSYSTEM - SCRIPT DE BASE DE DATOS
-- MOTOR: PostgreSQL v15+ con Extensión Espacial PostGIS
-- =====================================================================

-- Habilitar la extensión geoespacial PostGIS para el atributo 'ubicacion'
CREATE EXTENSION IF NOT EXISTS postgis;

-- ---------------------------------------------------------------------
-- 1. Tabla: Usuario
-- ---------------------------------------------------------------------
CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre_apellido VARCHAR(255) NOT NULL,
    dni_cuil VARCHAR(20) UNIQUE NOT NULL,
    reputacion INT DEFAULT 100,
    email VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL -- Se utiliza 'contrasena' sin 'ñ' para evitar conflictos de encoding
);

-- ---------------------------------------------------------------------
-- 2. Tabla: Reporte
-- ---------------------------------------------------------------------
CREATE TABLE Reporte (
    id_reporte SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    patente_vehiculo VARCHAR(15) NOT NULL,
    fechaHora_dispositivo TIMESTAMP NOT NULL,
    fechaHora_server TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ubicacion GEOMETRY(Point, 4326) NOT NULL, -- Tipo de dato nativo de PostGIS (SRID 4326 = WGS84 / GPS)
    estado VARCHAR(20) DEFAULT 'Pendiente',
    hash_evidencia VARCHAR(64), -- Hash SHA-256 preliminar del reporte
    descripcion TEXT,
    
    -- Relaciones y Restricciones
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE RESTRICT,
    CONSTRAINT chk_estado_reporte CHECK (estado IN ('Pendiente', 'Validada', 'Rechazada'))
);

-- ---------------------------------------------------------------------
-- 3. Tabla: Evidencia
-- ---------------------------------------------------------------------
CREATE TABLE Evidencia (
    id_evidencia SERIAL PRIMARY KEY,
    id_infraccion INT NOT NULL, -- Mapea el link lógico. Se conecta con id_reporte de la tabla Reporte.
    url_foto TEXT,
    url_archivo_s3 TEXT,
    hash_seguridad_sha VARCHAR(64), -- Almacena el checksum de inalterabilidad legal
    
    -- Relaciones y Restricciones
    FOREIGN KEY (id_infraccion) REFERENCES Reporte(id_reporte) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- 4. Índices de Optimización de Rendimiento
-- ---------------------------------------------------------------------
-- Índice espacial GIST para acelerar consultas geográficas (mapas de calor, jurisdicciones)
CREATE INDEX idx_reporte_ubicacion ON Reporte USING GIST (ubicacion);

-- Índice tradicional para búsquedas rápidas por patente de vehículos
CREATE INDEX idx_reporte_patente ON Reporte (patente_vehiculo);


-- =====================================================================
-- EXOMSYSTEM - SCRIPT DE CARGA DE DATOS DE PRUEBA (CHILECITO, LA RIOJA)
-- =====================================================================

TRUNCATE TABLE Evidencia, Reporte, Usuario RESTART IDENTITY CASCADE;

-- ---------------------------------------------------------------------
-- 1. Carga de Usuarios (Denunciantes locales)
-- ---------------------------------------------------------------------
INSERT INTO Usuario (nombre_apellido, dni_cuil, reputacion, email, contrasena) VALUES
('Mariano Ormeño', '20-36123456-9', 100, 'mariano.ormeno@email.com', '$2a$12$K3vYV2vG8L8...hash_simulado'),
('Lucía Fanchil', '27-40987654-2', 98, 'lucia.f@email.com', '$2a$12$J9xWw3vH9M9...hash_simulado'),
('Carlos Castro', '20-28112233-3', 50, 'carlos.c@email.com', '$2a$12$L1zZz4vJ1N1...hash_simulado');

-- ---------------------------------------------------------------------
-- 2. Carga de Reportes (Infracciones con GPS real en Chilecito)
-- ---------------------------------------------------------------------

INSERT INTO Reporte (id_usuario, patente_vehiculo, fechaHora_dispositivo, ubicacion, estado, hash_evidencia, descripcion) VALUES
(
    1, 
    'AF123AA', 
    CURRENT_TIMESTAMP - INTERVAL '45 minutes', 
    ST_GeomFromText('POINT(-67.4965 -29.1611)', 4326), -- Ubicación: Alrededores de Plaza Caudillos Federales (Centro)
    'Pendiente', 
    '8f43428f53c153249d9c67ef1142bc3c4b14d23d8cbb819c9e0111aa757c91a3',
    'Vehículo estacionado obstruyendo la rampa de accesibilidad en la esquina de la plaza principal.'
),
(
    2, 
    'AE987BB', 
    CURRENT_TIMESTAMP - INTERVAL '2 hours', 
    ST_GeomFromText('POINT(-67.4892 -29.1664)', 4326), -- Ubicación: Cerca del campus de la UNDe (Universidad Nacional de Chilecito)
    'Validada', 
    'a591e1143c1a2d8e4115161c29e1f516a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7',
    'Auto en doble fila frente al ingreso escolar, interrumpiendo el tránsito de colectivos.'
),
(
    3, 
    'POV654', 
    CURRENT_TIMESTAMP - INTERVAL '6 hours', 
    ST_GeomFromText('POINT(-67.4915 -29.1548)', 4326), -- Ubicación: Proximidades de la Terminal de Ómnibus de Chilecito
    'Rechazada', 
    'b682f2254d2b3e9f5226272d30f2a627b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8',
    'Estacionado en lugar no permitido.'
);

-- ---------------------------------------------------------------------
-- 3. Carga de Evidencias (Vínculos a fotos en S3 de los reportes)
-- ---------------------------------------------------------------------
INSERT INTO Evidencia (id_infraccion, url_foto, url_archivo_s3, hash_seguridad_sha) VALUES
(
    1, 
    'https://exomsystem.com/evidencia/tmp_chilecito_001.jpg', 
    'https://s3.amazonaws.com/bucket-exomsystem/evidencias/2026/05/chilecito_001.jpg', 
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
),
(
    1, -- Segunda foto de respaldo para el reporte del centro
    'https://exomsystem.com/evidencia/tmp_chilecito_001_alt.jpg', 
    'https://s3.amazonaws.com/bucket-exomsystem/evidencias/2026/05/chilecito_001_alt.jpg', 
    '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
),
(
    2, 
    'https://exomsystem.com/evidencia/tmp_chilecito_002.jpg', 
    'https://s3.amazonaws.com/bucket-exomsystem/evidencias/2026/05/chilecito_002.jpg', 
    '751e22244d2b3e9f5226272d30f2a627b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8'
),
(
    3, 
    'https://exomsystem.com/evidencia/tmp_chilecito_003.jpg', 
    'https://s3.amazonaws.com/bucket-exomsystem/evidencias/2026/05/chilecito_003.jpg', 
    '112e22244d2b3e9f5226272d30f2a627b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e9'
);
 COMMIT;
