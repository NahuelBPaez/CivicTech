// =====================================================================
// CIVICTECH - SCRIPT DE BASE DE DATOS (Autocontenido para Compass / mongosh)
// - No requiere editar IDs ni usar system.js
// - Ejecutar todo de una sola vez en Playground o mongosh
// =====================================================================



(function cleanup() {
  try {
    const cols = db.getCollectionNames();
    if (cols.length) {
      print("Colecciones detectadas, intentando dropear cada una:");
      cols.forEach(function(c) {
        try {
          print(" - Dropping:", c);
          db.getCollection(c).drop();
        } catch (e) {
          print("   Error al dropear", c, ":", e.message || e);
        }
      });
    } else {
      print("No hay colecciones previas en la base.");
    }
  } catch (e) {
    print("Error en limpieza inicial (continuando):", e.message || e);
  }
})();

print("\n==> Creando colecciones e índices...");

db.createCollection("usuario", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre_apellido", "dni", "email", "contrasena", "municipio_id"],
      properties: {
        nombre_apellido: { bsonType: "string" },
        dni: { bsonType: "string" },
        reputacion: { bsonType: "int" },
        email: { bsonType: "string", pattern: "^.+@.+\\..+$" },
        contrasena: { bsonType: "string" },
        municipio_id: { bsonType: "objectId" }
      }
    }
  }
});
db.usuario.createIndex({ dni: 1 }, { unique: true });
db.usuario.createIndex({ email: 1 }, { unique: true });

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
        ubicacion: { bsonType: "object" }
      }
    }
  }
});
try { db.municipio.createIndex({ ubicacion: "2dsphere" }); } catch(e){ print("Index ubicacion (municipio) skip:", e.message || e); }

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
        ubicacion: { bsonType: "object" },
        estado: { enum: ["Pendiente", "Validada", "Rechazada"] },
        hash_evidencia: { bsonType: "string" },
        descripcion: { bsonType: "string" },
        validador_id: { bsonType: "objectId" }
      }
    }
  }
});
try { db.reporte.createIndex({ ubicacion: "2dsphere" }); } catch(e){ print("Index ubicacion (reporte) skip:", e.message || e); }
db.reporte.createIndex({ patente_vehiculo: 1 });

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
});

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
});
db.agente_municipal.createIndex({ dni: 1 }, { unique: true });
db.agente_municipal.createIndex({ email: 1 }, { unique: true });

print("Colecciones e índices creados.");

print("\n==> Insertando municipios de prueba...");
const famatina = db.municipio.insertOne({
  nombre:"Famatina", provincia:"La Rioja", pais:"Argentina", codigo_municipio:"FAM001",
  contacto:{ email:"transito@famatina.gob.ar", telefono:"+54 3825 111111" }
}).insertedId;
const chilecito = db.municipio.insertOne({
  nombre:"Chilecito", provincia:"La Rioja", pais:"Argentina", codigo_municipio:"CHL001",
  contacto:{ email:"transito@chilecito.gob.ar", telefono:"+54 3825 123456" }
}).insertedId;
const larioja = db.municipio.insertOne({
  nombre:"La Rioja Capital", provincia:"La Rioja", pais:"Argentina", codigo_municipio:"LRJ001",
  contacto:{ email:"transito@larioja.gob.ar", telefono:"+54 3825 222222" }
}).insertedId;
print("Municipios insertados:", famatina, chilecito, larioja);

print("\n==> Insertando usuarios de prueba...");
const usrChl1 = db.usuario.insertOne({ nombre_apellido: "Juan Perez", dni: "30111222", reputacion: 50, email: "juan.perez@chilecito.com", contrasena: "pwd123", municipio_id: chilecito }).insertedId;
const usrChl2 = db.usuario.insertOne({ nombre_apellido: "Maria Gomez", dni: "31111222", reputacion: 45, email: "maria.g@chilecito.com", contrasena: "pwd123", municipio_id: chilecito }).insertedId;
const usrChl3 = db.usuario.insertOne({ nombre_apellido: "Carlos Ruiz", dni: "32111222", reputacion: 60, email: "carlos.r@chilecito.com", contrasena: "pwd123", municipio_id: chilecito }).insertedId;
const usrChl4 = db.usuario.insertOne({ nombre_apellido: "Ana Torres", dni: "33111222", reputacion: 55, email: "ana.t@chilecito.com", contrasena: "pwd123", municipio_id: chilecito }).insertedId;

const usrLr1 = db.usuario.insertOne({ nombre_apellido: "Luis Diaz", dni: "34111222", reputacion: 50, email: "luis.d@larioja.com", contrasena: "pwd123", municipio_id: larioja }).insertedId;
const usrLr2 = db.usuario.insertOne({ nombre_apellido: "Marta Silva", dni: "35111222", reputacion: 40, email: "marta.s@larioja.com", contrasena: "pwd123", municipio_id: larioja }).insertedId;
const usrLr3 = db.usuario.insertOne({ nombre_apellido: "Pablo Lopez", dni: "36111222", reputacion: 70, email: "pablo.l@larioja.com", contrasena: "pwd123", municipio_id: larioja }).insertedId;
const usrLr4 = db.usuario.insertOne({ nombre_apellido: "Rosa Luna", dni: "37111222", reputacion: 65, email: "rosa.l@larioja.com", contrasena: "pwd123", municipio_id: larioja }).insertedId;

const usrFam1 = db.usuario.insertOne({ nombre_apellido: "Jorge Vera", dni: "38111222", reputacion: 50, email: "jorge.v@famatina.com", contrasena: "pwd123", municipio_id: famatina }).insertedId;
const usrFam2 = db.usuario.insertOne({ nombre_apellido: "Elena Paz", dni: "39111222", reputacion: 50, email: "elena.p@famatina.com", contrasena: "pwd123", municipio_id: famatina }).insertedId;
const usrFam3 = db.usuario.insertOne({ nombre_apellido: "Raul Sosa", dni: "40111223", reputacion: 55, email: "raul.s@famatina.com", contrasena: "pwd123", municipio_id: famatina }).insertedId;
const usrFam4 = db.usuario.insertOne({ nombre_apellido: "Carmen Rios", dni: "41111223", reputacion: 60, email: "carmen.r@famatina.com", contrasena: "pwd123", municipio_id: famatina }).insertedId;

print("Usuarios insertados.");

print("\n==> Definiendo función local insertReporteConValidacion...");
const insertReporteConValidacion = function(reporteDoc) {
  if (!reporteDoc.usuario_id || !reporteDoc.municipio_id) {
    throw new Error("Faltan usuario_id o municipio_id en el documento de reporte");
  }
  const usuario = db.usuario.findOne({ _id: reporteDoc.usuario_id });
  if (!usuario) {
    throw new Error("Usuario no encontrado");
  }
  if (!usuario.municipio_id) {
    throw new Error("El usuario no tiene municipio_id asignado");
  }
  if (!usuario.municipio_id.equals(reporteDoc.municipio_id)) {
    throw new Error("Regla de negocio: usuario.municipio_id debe coincidir con reporte.municipio_id");
  }
  const res = db.reporte.insertOne(reporteDoc);
  return res.insertedId;
};
print("Función local definida.");

print("\n==> Insertando reportes de prueba (usando validación)...");
const r_chl1 = insertReporteConValidacion({
  usuario_id: usrChl1,
  municipio_id: chilecito,
  patente_vehiculo: "AB123CD",
  fechaHora_dispositivo: new Date(),
  fechaHora_server: new Date(),
  ubicacion: { type: "Point", coordinates: [-67.49, -29.16] },
  estado: "Pendiente",
  hash_evidencia: "hash_chilecito_001",
  descripcion: "Estacionado en rampa"
});
const r_lr1 = insertReporteConValidacion({
  usuario_id: usrLr1,
  municipio_id: larioja,
  patente_vehiculo: "EF456GH",
  fechaHora_dispositivo: new Date(),
  fechaHora_server: new Date(),
  ubicacion: { type: "Point", coordinates: [-66.85, -29.41] },
  estado: "Pendiente",
  hash_evidencia: "hash_larioja_001",
  descripcion: "Doble fila"
});
const r_fam1 = insertReporteConValidacion({
  usuario_id: usrFam1,
  municipio_id: famatina,
  patente_vehiculo: "IJ789KL",
  fechaHora_dispositivo: new Date(),
  fechaHora_server: new Date(),
  ubicacion: { type: "Point", coordinates: [-67.52, -28.92] },
  estado: "Pendiente",
  hash_evidencia: "hash_famatina_001",
  descripcion: "Bloqueando garaje"
});

insertReporteConValidacion({ usuario_id: usrChl2, municipio_id: chilecito, patente_vehiculo: "AA000BB", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.491, -29.161] }, estado: "Validada", hash_evidencia: "hash_chl_002", descripcion: "Mal estacionado" });
insertReporteConValidacion({ usuario_id: usrChl3, municipio_id: chilecito, patente_vehiculo: "CC111DD", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.492, -29.162] }, estado: "Rechazada", hash_evidencia: "hash_chl_003", descripcion: "Senda peatonal" });
insertReporteConValidacion({ usuario_id: usrChl4, municipio_id: chilecito, patente_vehiculo: "EE222FF", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.493, -29.163] }, estado: "Pendiente", hash_evidencia: "hash_chl_004", descripcion: "Línea amarilla" });
insertReporteConValidacion({ usuario_id: usrChl1, municipio_id: chilecito, patente_vehiculo: "GG333HH", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.494, -29.164] }, estado: "Pendiente", hash_evidencia: "hash_chl_005", descripcion: "Parada de colectivo" });

insertReporteConValidacion({ usuario_id: usrLr2, municipio_id: larioja, patente_vehiculo: "II444JJ", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-66.851, -29.411] }, estado: "Validada", hash_evidencia: "hash_lr_002", descripcion: "Doble fila en colegio" });
insertReporteConValidacion({ usuario_id: usrLr3, municipio_id: larioja, patente_vehiculo: "KK555LL", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-66.852, -29.412] }, estado: "Pendiente", hash_evidencia: "hash_lr_003", descripcion: "Ocupando lugar de discapacitados" });

insertReporteConValidacion({ usuario_id: usrFam2, municipio_id: famatina, patente_vehiculo: "MM666NN", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.521, -28.921] }, estado: "Pendiente", hash_evidencia: "hash_fam_002", descripcion: "Carga y descarga en horario no permitido" });
insertReporteConValidacion({ usuario_id: usrFam3, municipio_id: famatina, patente_vehiculo: "OO777PP", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.522, -28.922] }, estado: "Rechazada", hash_evidencia: "hash_fam_003", descripcion: "Vehículo abandonado" });
insertReporteConValidacion({ usuario_id: usrFam4, municipio_id: famatina, patente_vehiculo: "QQ888RR", fechaHora_dispositivo: new Date(), fechaHora_server: new Date(), ubicacion: { type: "Point", coordinates: [-67.523, -28.923] }, estado: "Validada", hash_evidencia: "hash_fam_004", descripcion: "Estacionado en contramano" });

print("Reportes insertados correctamente.");

print("\n==> Insertando evidencias y agentes...");
db.evidencia.insertMany([
  { reporte_id:r_chl1, url_foto:"https://upload.wikimedia.org/wikipedia/commons/3/3f/Car_in_parking.jpg", url_archivo_s3:"https://s3.amazonaws.com/bucket/evidencia/chilecito_001.jpg", hash_seguridad_sha:"sha256..." },
  { reporte_id:r_lr1, url_foto:"https://upload.wikimedia.org/wikipedia/commons/5/5e/Car_double_parking.jpg", url_archivo_s3:"https://s3.amazonaws.com/bucket/evidencia/larioja_001.jpg", hash_seguridad_sha:"sha256..." },
  { reporte_id:r_fam1, url_foto:"https://upload.wikimedia.org/wikipedia/commons/6/6a/Car_blocking_access.jpg", url_archivo_s3:"https://s3.amazonaws.com/bucket/evidencia/famatina_001.jpg", hash_seguridad_sha:"sha256..." }
]);

db.agente_municipal.insertMany([
  { nombre_apellido:"Inspector Chilecito", dni:"40111222", email:"inspector.chl@chilecito.gob.ar", rol:"Inspector", municipio_id:chilecito, acciones:[] },
  { nombre_apellido:"Inspector La Rioja", dni:"41111222", email:"inspector.lr@larioja.gob.ar", rol:"Inspector", municipio_id:larioja, acciones:[] },
  { nombre_apellido:"Inspector Famatina", dni:"42111222", email:"inspector.fam@famatina.gob.ar", rol:"Inspector", municipio_id:famatina, acciones:[] }
]);

print("Evidencias y agentes insertados. Script finalizado con éxito.");
