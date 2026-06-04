// Checklist de verificación ejecutable con mensajes

print("📋 Listando colecciones...");
printjson(db.getCollectionNames());

print("📊 Conteo de documentos en cada colección:");
print("Usuarios: " + db.usuario.countDocuments());
print("Municipios: " + db.municipio.countDocuments());
print("Reportes: " + db.reporte.countDocuments());
print("Evidencias: " + db.evidencia.countDocuments());
print("Agentes municipales: " + db.agente_municipal.countDocuments());

print("🔎 Verificando índices...");
print("Índices en reporte:");
printjson(db.reporte.getIndexes());
print("Índices en municipio:");
printjson(db.municipio.getIndexes());
print("Índices en usuario:");
printjson(db.usuario.getIndexes());
print("Índices en agente_municipal:");
printjson(db.agente_municipal.getIndexes());

print("✅ Validando que todos los usuarios tengan municipio_id...");
print("Usuarios sin municipio_id: " + db.usuario.find({ municipio_id: { $exists: false } }).count());

print("🧪 Prueba de inserción válida...");
const pruebaValida = {
  usuario_id: db.usuario.findOne({ email: "juan.perez@chilecito.com" })._id,
  municipio_id: db.municipio.findOne({ codigo_municipio: "CHL001" })._id,
  patente_vehiculo: "TEST123",
  fechaHora_dispositivo: new Date(),
  fechaHora_server: new Date(),
  ubicacion: { type: "Point", coordinates: [-67.49, -29.16] },
  estado: "Pendiente",
  hash_evidencia: "hash_test_valida",
  descripcion: "Prueba inserción válida"
};
db.reporte.insertOne(pruebaValida);
print("Reporte insertado:");
printjson(db.reporte.find({ hash_evidencia: "hash_test_valida" }).toArray());

print("🌍 Municipios cargados en la base:");
db.municipio.find({}, { nombre: 1, codigo_municipio: 1, _id: 0 }).forEach(m => {
  print(" - " + m.nombre + " (codigo: " + m.codigo_municipio + ")");
});

