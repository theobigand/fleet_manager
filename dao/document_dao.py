from typing import Optional, List
from dao.base_dao import BaseDAO
from models import Document

class DocumentDAO(BaseDAO):
    
    def find_all(self, vehicle_immat: Optional[str] = None, type_document: Optional[str] = None) -> List[Document]:
        query="""
            SELECT d.*, v.immatriculation, v.marque, v.modele
            FROM documents d
            JOIN vehicules v ON d.vehicule_id = v.id
            WHERE 1=1
        """
        params=[]
        if vehicle_immat:
            query+=" AND v.immatriculation = ?"
            params.append(vehicle_immat)
        if type_document:
            query+=" AND d.type_document = ?"
            params.append(type_document)
        query+=" ORDER BY d.date_echeance"
        rows=self._fetch_all(query, tuple(params))
        return [Document.from_dict(row) for row in rows]
    
    def find_by_id(self, doc_id: int) -> Optional[Document]:
        row=self._fetch_one("SELECT * FROM documents WHERE id = ?", (doc_id,))
        return Document.from_dict(row)
    
    def create(self, doc: Document) -> Optional[int]:
        data=doc.to_dict()
        data.pop('id', None)
        for key in ['immatriculation', 'marque', 'modele']:
            data.pop(key, None)
        return self._insert('documents', data)
    
    def update(self, doc_id: int, **fields) -> None:
        self._update('documents', doc_id, fields)
    
    def delete(self, doc_id: int) -> None:
        self._delete('documents', doc_id)
