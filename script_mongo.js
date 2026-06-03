// =====================================================================
// CIVICTECH - SCRIPT DE BASE DE DATOS
// MOTOR: MongoDB v6+ con Índices Geoespaciales 2dsphere
// =====================================================================

// ---------------------------------------------------------------------
// 1. Colección: Usuario
// ---------------------------------------------------------------------
db.createCollection("usuario", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_apellido", "dni", "email", "contrasena"],
      properties: {
        nombre_apellido: { bsonType: "string" },
        dni: { bsonType: "string" },
        reputacion: { bsonType: "int" },
        email: { bsonType: "string", pattern: "^.+@.+\\..+$" },
        contrasena: { bsonType: "string" }
      }
    }
  }
})
db.usuario.createIndex({ dni: 1 }, { unique: true })
db.usuario.createIndex({ email: 1 }, { unique: true })

// ---------------------------------------------------------------------
// 2. Colección: Municipio
// ---------------------------------------------------------------------
db.createCollection("municipio", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "provincia", "pais", "codigo_municipio"],
      properties: {
        nombre: { bsonType: "string" },
        provincia: { bsonType: "string" },
        pais: { bsonType: "string" },
        codigo_municipio: { bsonType: "string" },
        contacto: {
          bsonType: "object",
          properties: {
            email: { bsonType: "string" },
            telefono: { bsonType: "string" }
          }
        },
        ubicacion: { bsonType: "object" } // Polygon GeoJSON
      }
    }
  }
})
db.municipio.createIndex({ ubicacion: "2dsphere" })

// ---------------------------------------------------------------------
// 3. Colección: Reporte
// ---------------------------------------------------------------------
db.createCollection("reporte", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["usuario_id", "municipio_id", "estado", "ubicacion"],
      properties: {
        usuario_id: { bsonType: "objectId" },
        municipio_id: { bsonType: "objectId" },
        patente_vehiculo: { bsonType: "string" },
        fechaHora_dispositivo: { bsonType: "date" },
        fechaHora_server: { bsonType: "date" },
        ubicacion: { bsonType: "object" }, // Point GeoJSON
        estado: { enum: ["Pendiente", "Validada", "Rechazada"] },
        hash_evidencia: { bsonType: "string" },
        descripcion: { bsonType: "string" },
        validador_id: { bsonType: "objectId" }
      }
    }
  }
})
db.reporte.createIndex({ ubicacion: "2dsphere" })
db.reporte.createIndex({ patente_vehiculo: 1 })

// ---------------------------------------------------------------------
// 4. Colección: Evidencia
// ---------------------------------------------------------------------
db.createCollection("evidencia", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["reporte_id", "url_foto", "hash_seguridad_sha"],
      properties: {
        reporte_id: { bsonType: "objectId" },
        url_foto: { bsonType: "string" },
        url_archivo_s3: { bsonType: "string" },
        hash_seguridad_sha: { bsonType: "string" }
      }
    }
  }
})

// ---------------------------------------------------------------------
// 5. Colección: AgenteMunicipal
// ---------------------------------------------------------------------
db.createCollection("agente_municipal", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_apellido", "dni", "email", "rol", "municipio_id"],
      properties: {
        nombre_apellido: { bsonType: "string" },
        dni: { bsonType: "string" },
        email: { bsonType: "string" },
        rol: { bsonType: "string" },
        municipio_id: { bsonType: "objectId" },
        acciones: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              reporte_id: { bsonType: "objectId" },
              usuario_id: { bsonType: "objectId" },
              fecha_accion: { bsonType: "date" },
              tipo_accion: { enum: ["Validacion", "Rechazo", "AjusteReputacion"] },
              reputacion_delta: { bsonType: "int" }
            }
          }
        }
      }
    }
  }
})
db.agente_municipal.createIndex({ dni: 1 }, { unique: true })
db.agente_municipal.createIndex({ email: 1 }, { unique: true })

// =====================================================================
// DATOS DE PRUEBA
// =====================================================================

// Municipios
const famatina = db.municipio.insertOne({ nombre:"Famatina", provincia:"La Rioja", pais:"Argentina", codigo_municipio:"FAM001", contacto:{ email:"transito@famatina.gob.ar", telefono:"+54 3825 111111" } }).insertedId
const chilecito = db.municipio.insertOne({ nombre:"Chilecito", provincia:"La Rioja", pais:"Argentina", codigo_municipio:"CHL001", contacto:{ email:"transito@chilecito.gob.ar", telefono:"+54 3825 123456" } }).insertedId
const larioja = db.municipio.insertOne({ nombre:"La Rioja Capital", provincia:"La Rioja", pais:"Argentina", codigo_municipio:"LRJ001", contacto:{ email:"transito@larioja.gob.ar", telefono:"+54 3825 222222" } }).insertedId

// Usuarios por ciudad (4 cada uno)
const usuariosChilecito = [...]; // (igual que definimos antes)
const usuariosLaRioja = [...];
const usuariosFamatina = [...];

// Reportes: Chilecito (5), La Rioja Capital (3), Famatina (4)
db.reporte.insertMany([...]); // (igual que definimos antes)

// Evidencias (ejemplo con URLs reales de imágenes públicas)
db.evidencia.insertMany([
  { reporte_id:r_chl1, url_foto:"https://upload.wikimedia.org/wikipedia/commons/3/3f/Car_in_parking.jpg", url_archivo_s3:"https://s3.amazonaws.com/bucket/evidencia/chilecito_001.jpg", hash_seguridad_sha:"sha256..." },
  { reporte_id:r_lr1, url_foto:"https://upload.wikimedia.org/wikipedia/commons/5/5e/Car_double_parking.jpg", url_archivo_s3:"https://s3.amazonaws.com/bucket/evidencia/larioja_001.jpg", hash_seguridad_sha:"sha256..." },
  { reporte_id:r_fam1, url_foto:"https://upload.wikimedia.org/wikipedia/commons/6/6a/Car_blocking_access.jpg", url_archivo_s3:"https://s3.amazonaws.com/bucket/evidencia/famatina_001.jpg", hash_seguridad_sha:"sha256..." }
])

// Agentes Municipales (1 por ciudad)
db.agente_municipal.insertMany([
  { nombre_apellido:"Inspector Chilecito", dni:"40111222", email:"inspector.chl@chilecito.gob.ar", rol:"Inspector", municipio_id:chilecito, acciones:[] },
  { nombre_apellido:"Inspector La Rioja", dni:"41111222", email:"inspector.lr@larioja.gob.ar", rol:"Inspector", municipio_id:larioja, acciones:[] },
  { nombre_apellido:"Inspector Famatina", dni:"42111222", email:"inspector.fam@famatina.gob.ar", rol:"Inspector", municipio_id:famatina, acciones:[] }
])
