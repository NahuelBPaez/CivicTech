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
// Usamos insertOne para capturar los IDs en variables y luego agruparlos
const usrChl1 = db.usuario.insertOne({ nombre_apellido: "Juan Perez", dni: "30111222", reputacion: 50, email: "juan.perez@chilecito.com", contrasena: "pwd123" }).insertedId;
const usrChl2 = db.usuario.insertOne({ nombre_apellido: "Maria Gomez", dni: "31111222", reputacion: 45, email: "maria.g@chilecito.com", contrasena: "pwd123" }).insertedId;
const usrChl3 = db.usuario.insertOne({ nombre_apellido: "Carlos Ruiz", dni: "32111222", reputacion: 60, email: "carlos.r@chilecito.com", contrasena: "pwd123" }).insertedId;
const usrChl4 = db.usuario.insertOne({ nombre_apellido: "Ana Torres", dni: "33111222", reputacion: 55, email: "ana.t@chilecito.com", contrasena: "pwd123" }).insertedId;
const usuariosChilecito = [usrChl1, usrChl2, usrChl3, usrChl4];

const usrLr1 = db.usuario.insertOne({ nombre_apellido: "Luis Diaz", dni: "34111222", reputacion: 50, email: "luis.d@larioja.com", contrasena: "pwd123" }).insertedId;
const usrLr2 = db.usuario.insertOne({ nombre_apellido: "Marta Silva", dni: "35111222", reputacion: 40, email: "marta.s@larioja.com", contrasena: "pwd123" }).insertedId;
const usrLr3 = db.usuario.insertOne({ nombre_apellido: "Pablo Lopez", dni: "36111222", reputacion: 70, email: "pablo.l@larioja.com", contrasena: "pwd123" }).insertedId;
const usrLr4 = db.usuario.insertOne({ nombre_apellido: "Rosa Luna", dni: "37111222", reputacion: 65, email: "rosa.l@larioja.com", contrasena: "pwd123" }).insertedId;
const usuariosLaRioja = [usrLr1, usrLr2, usrLr3, usrLr4];

const usrFam1 = db.usuario.insertOne({ nombre_apellido: "Jorge Vera", dni: "38111222", reputacion: 50, email: "jorge.v@famatina.com", contrasena: "pwd123" }).insertedId;
const usrFam2 = db.usuario.insertOne({ nombre_apellido: "Elena Paz", dni: "39111222", reputacion: 50, email: "elena.p@famatina.com", contrasena: "pwd123" }).insertedId;
const usrFam3 = db.usuario.insertOne({ nombre_apellido: "Raul Sosa", dni: "40111223", reputacion: 55, email: "raul.s@famatina.com", contrasena: "pwd123" }).insertedId;
const usrFam4 = db.usuario.insertOne({ nombre_apellido: "Carmen Rios", dni: "41111223", reputacion: 60, email: "carmen.r@famatina.com", contrasena: "pwd123" }).insertedId;
const usuariosFamatina = [usrFam1, usrFam2, usrFam3, usrFam4];

// Reportes: Chilecito (5), La Rioja Capital (3), Famatina (4)

// 1. Insertamos un reporte por ciudad guardando el ID para la colección de Evidencias
const r_chl1 = db.reporte.insertOne({ usuario_id: usrChl1, municipio_id: chilecito, patente_vehiculo: "AB123CD", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.49, -29.16] }, estado: "Pendiente", hash_evidencia: "hash_chilecito_001", descripcion: "Estacionado en rampa" }).insertedId;

const r_lr1 = db.reporte.insertOne({ usuario_id: usrLr1, municipio_id: larioja, patente_vehiculo: "EF456GH", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-66.85, -29.41] }, estado: "Pendiente", hash_evidencia: "hash_larioja_001", descripcion: "Doble fila" }).insertedId;

const r_fam1 = db.reporte.insertOne({ usuario_id: usrFam1, municipio_id: famatina, patente_vehiculo: "IJ789KL", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.52, -28.92] }, estado: "Pendiente", hash_evidencia: "hash_famatina_001", descripcion: "Bloqueando garaje" }).insertedId;

// 2. Insertamos el resto de los reportes solicitados con insertMany
db.reporte.insertMany([
  // Chilecito (faltan 4 para llegar a 5)
  { usuario_id: usrChl2, municipio_id: chilecito, patente_vehiculo: "AA000BB", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.491, -29.161] }, estado: "Validada", hash_evidencia: "hash_chl_002", descripcion: "Mal estacionado" },
  { usuario_id: usrChl3, municipio_id: chilecito, patente_vehiculo: "CC111DD", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.492, -29.162] }, estado: "Rechazada", hash_evidencia: "hash_chl_003", descripcion: "Senda peatonal" },
  { usuario_id: usrChl4, municipio_id: chilecito, patente_vehiculo: "EE222FF", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.493, -29.163] }, estado: "Pendiente", hash_evidencia: "hash_chl_004", descripcion: "Línea amarilla" },
  { usuario_id: usrChl1, municipio_id: chilecito, patente_vehiculo: "GG333HH", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.494, -29.164] }, estado: "Pendiente", hash_evidencia: "hash_chl_005", descripcion: "Parada de colectivo" },

  // La Rioja Capital (faltan 2 para llegar a 3)
  { usuario_id: usrLr2, municipio_id: larioja, patente_vehiculo: "II444JJ", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-66.851, -29.411] }, estado: "Validada", hash_evidencia: "hash_lr_002", descripcion: "Doble fila en colegio" },
  { usuario_id: usrLr3, municipio_id: larioja, patente_vehiculo: "KK555LL", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-66.852, -29.412] }, estado: "Pendiente", hash_evidencia: "hash_lr_003", descripcion: "Ocupando lugar de discapacitados" },

  // Famatina (faltan 3 para llegar a 4)
  { usuario_id: usrFam2, municipio_id: famatina, patente_vehiculo: "MM666NN", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.521, -28.921] }, estado: "Pendiente", hash_evidencia: "hash_fam_002", descripcion: "Carga y descarga en horario no permitido" },
  { usuario_id: usrFam3, municipio_id: famatina, patente_vehiculo: "OO777PP", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.522, -28.922] }, estado: "Rechazada", hash_evidencia: "hash_fam_003", descripcion: "Vehículo abandonado" },
  { usuario_id: usrFam4, municipio_id: famatina, patente_vehiculo: "QQ888RR", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.523, -28.923] }, estado: "Validada", hash_evidencia: "hash_fam_004", descripcion: "Estacionado en contramano" }
]);



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
