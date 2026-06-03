
## Checklist de verificación (ejecutar después)
- Comprobar colecciones:
  - `db.getCollectionNames()` debe listar: `usuario, municipio, reporte, evidencia, agente_municipal`.
- Comprobar índices:
  - `db.reporte.getIndexes()` debe mostrar `ubicacion: 2dsphere` y `patente_vehiculo`
  - `db.municipio.getIndexes()` debe mostrar `ubicacion: 2dsphere` (si se creó)
  - `db.usuario.getIndexes()` y `db.agente_municipal.getIndexes()` deben mostrar índices únicos en `dni` y `email`.
- Comprobar usuarios con municipio_id:
  - `db.usuario.find({ municipio_id: { $exists: false } }).count()` debe devolver `0`.
- Probar inserción válida (debe insertarse):
  - Usar el Playground o mongosh para ejecutar el bloque de prueba incluido en el script o:
    ```js
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
    db.reporte.find({ hash_evidencia: "hash_test_valida" }).pretty();
    ```
- Probar inserción inválida (debe bloquearse si se usa la función local del script):
  - Ejecutar el bloque de prueba incluido en el script que intenta insertar un reporte con `municipio_id` distinto al del usuario.

## Notas sobre permisos y backups
- Si no tenés permisos `dropDatabase`, el script no intentará crear usuarios ni cambiar roles; solo dropeará colecciones (operación permitida con `readWrite`).
- Hacé export de colecciones si necesitás backup antes de ejecutar.

## Problemas comunes y soluciones rápidas
- `db.system.js.save is not a function`: el script no usa `system.js` para funcionar; la validación se hace con una función local.
- Errores por índices únicos: si aparecen duplicados, dropeá las colecciones y ejecutá de nuevo.
- Timeouts en Compass: ejecutar el script por bloques (colecciones, municipios, usuarios, reportes, evidencias/agentes).

## Comandos útiles de verificación
- Listar colecciones: `db.getCollectionNames()`
- Ver índices: `db.reporte.getIndexes()`
- Conteos: `db.usuario.countDocuments()` etc.
- Reportes por municipio:
```js
db.reporte.aggregate([
  { $lookup: { from: "municipio", localField: "municipio_id", foreignField: "_id", as: "mun" } },
  { $unwind: "$mun" },
  { $group: { _id: "$mun.codigo_municipio", total: { $sum: 1 } } },
  { $sort: { total: -1 } }
]).pretty();
