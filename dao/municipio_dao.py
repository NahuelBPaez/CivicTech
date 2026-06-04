# dao/municipio_dao.py
from bson import ObjectId

class MunicipioDAO:
    def __init__(self, db):
        self.collection = db["municipio"]

    def listar(self, limit=10):
        return list(self.collection.find().limit(limit))

    def insertar(self, municipio_doc):
        res = self.collection.insert_one(municipio_doc)
        return res.inserted_id

    def actualizar(self, municipio_id, nuevos_campos):
        oid = ObjectId(municipio_id)
        res = self.collection.update_one({"_id": oid}, {"$set": nuevos_campos})
        return res.modified_count

    def borrar(self, municipio_id):
        oid = ObjectId(municipio_id)
        res = self.collection.delete_one({"_id": oid})
        return res.deleted_count

