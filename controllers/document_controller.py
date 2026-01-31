from typing import Optional, List, Dict, Any
from models import Document
from dao import DocumentDAO, UserDAO
from controllers.result import Result


class DocumentController:
    
    def __init__(self) -> None:
        self.dao = DocumentDAO()
        self.log_dao = UserDAO()
    
    def get_all(self, vehicle_immat: Optional[str] = None,
                type_document: Optional[str] = None) -> List[Document]:
        return self.dao.find_all(vehicle_immat, type_document)
    
    def get_by_id(self, doc_id: int) -> Optional[Document]:
        return self.dao.find_by_id(doc_id)
    
    def create(self, data: Dict[str, Any], user_id: int) -> Result:
        vehicule_id = data.get('vehicule_id')
        type_doc = data.get('type_document')
        
        if not vehicule_id:
            return Result.error("Véhicule obligatoire")
        if not type_doc:
            return Result.error("Type de document obligatoire")
        
        doc = Document(
            vehicule_id=vehicule_id,
            type_document=type_doc,
            date_emission=data.get('date_emission') or None,
            date_echeance=data.get('date_echeance') or None,
            chemin_fichier=data.get('chemin_fichier'),
            description=data.get('description')
        )
        
        doc_id = self.dao.create(doc)
        if doc_id:
            self.log_dao.add_log(user_id, 'CREATION_DOCUMENT', f"{type_doc}")
            return Result.ok(doc_id, "Document créé")
        return Result.error("Erreur lors de la création")
    
    def update(self, doc_id: int, data: Dict[str, Any], user_id: int) -> Result:
        doc = self.dao.find_by_id(doc_id)
        if not doc:
            return Result.error("Document non trouvé")
        
        fields = {
            'vehicule_id': data.get('vehicule_id', doc.vehicule_id),
            'type_document': data.get('type_document', doc.type_document),
            'date_emission': data.get('date_emission') or None,
            'date_echeance': data.get('date_echeance') or None,
            'chemin_fichier': data.get('chemin_fichier'),
            'description': data.get('description')
        }
        
        self.dao.update(doc_id, **fields)
        self.log_dao.add_log(user_id, 'MODIFICATION_DOCUMENT', f"ID {doc_id}")
        return Result.ok(message="Document modifié")
    
    def delete(self, doc_id: int, user_id: int) -> Result:
        self.dao.delete(doc_id)
        self.log_dao.add_log(user_id, 'SUPPRESSION_DOCUMENT', f"ID {doc_id}")
        return Result.ok(message="Document supprimé")
