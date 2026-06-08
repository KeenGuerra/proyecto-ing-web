import os
import logging
import uuid
from datetime import datetime
from .config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# Mock Firestore Implementation for out-of-the-box operation
class MockDocumentReference:
    def __init__(self, doc_id, collection_ref):
        self.id = doc_id
        self._collection = collection_ref
    
    def get(self):
        class MockDocumentSnapshot:
            def __init__(self, doc_id, data):
                self.id = doc_id
                self.exists = data is not None
                self._data = data
            def to_dict(self):
                return self._data
        
        data = self._collection._data.get(self.id)
        return MockDocumentSnapshot(self.id, data)
        
    def set(self, data):
        self._collection._data[self.id] = data
        
    def update(self, data):
        if self.id in self._collection._data:
            # Handle deep or shallow merge
            self._collection._data[self.id].update(data)
            
    def delete(self):
        if self.id in self._collection._data:
            del self._collection._data[self.id]

class MockCollectionReference:
    def __init__(self):
        self._data = {}
        
    def document(self, doc_id):
        return MockDocumentReference(doc_id, self)
        
    def stream(self):
        class MockDocumentSnapshot:
            def __init__(self, doc_id, data):
                self.id = doc_id
                self._data = data
            def to_dict(self):
                return self._data
                
        # Return sorted by creation date if available
        items = list(self._data.items())
        # Try sorting by date to maintain order
        try:
            items.sort(key=lambda x: x[1].get("created_at", ""))
        except Exception:
            pass
        return [MockDocumentSnapshot(k, v) for k, v in items]
        
    def add(self, data):
        doc_id = str(uuid.uuid4())
        self._data[doc_id] = data
        return None, MockDocumentReference(doc_id, self)

class MockFirestoreClient:
    def __init__(self):
        self._collections = {}
        
    def collection(self, name):
        if name not in self._collections:
            self._collections[name] = MockCollectionReference()
        return self._collections[name]

# Global database client variable
db = None
is_mock = False

# Try to initialize Firebase
credentials_path = settings.FIREBASE_CREDENTIALS_PATH
firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if firebase_creds_json:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import json
        
        # Parse credential details directly from environment variable
        creds_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(creds_dict)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
        db = firestore.client()
        logger.info("Successfully connected to real Firebase Firestore using environment JSON!")
    except Exception as e:
        logger.error(f"Error initializing Firebase from environment JSON: {e}. Falling back to file checks.")
        is_mock = True

if db is None:
    if os.path.exists(credentials_path):
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                
            db = firestore.client()
            is_mock = False
            logger.info("Successfully connected to real Firebase Firestore using certificate file!")
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK from file: {e}. Falling back to Mock DB.")
            is_mock = True
    else:
        if not firebase_creds_json:
            logger.warning(
                f"Firebase credentials not found in environment JSON or file at '{credentials_path}'. "
                "Falling back to in-memory Mock Firestore. "
                "To connect your database, please configure the FIREBASE_CREDENTIALS_JSON environment variable "
                "or place your service account json file at the root."
            )
        is_mock = True

if is_mock or db is None:
    db = MockFirestoreClient()
    
    # Seed Mock DB with some premium demo tasks so it looks stunning out of the box!
    tasks_col = db.collection("tasks")
    
    demo_tasks = [
        {
            "title": "Diseñar interfaz de usuario principal",
            "description": "Crear el prototipo del Dashboard en Figma usando una paleta moderna, componentes reutilizables y tipografía Inter.",
            "status": "completed",
            "priority": "high",
            "category": "Diseño",
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        },
        {
            "title": "Integrar API de Firebase en FastAPI",
            "description": "Establecer conexión con Firestore, preparar controladores CRUD y añadir sistema de fallback local en caso de ausencia de credenciales.",
            "status": "in_progress",
            "priority": "medium",
            "category": "Backend",
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        },
        {
            "title": "Implementar Drag & Drop en Tablero Kanban",
            "description": "Utilizar interacciones fluidas de CSS y Angular Signals para permitir arrastrar y soltar tareas entre columnas del tablero.",
            "status": "todo",
            "priority": "high",
            "category": "Frontend",
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        },
        {
            "title": "Configurar despliegue continuo",
            "description": "Configurar GitHub Actions para ejecutar pruebas unitarias y desplegar automáticamente la API en Cloud Run y el frontend en Firebase Hosting.",
            "status": "todo",
            "priority": "low",
            "category": "DevOps",
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for task in demo_tasks:
        tasks_col.add(task)
        
    logger.info("Mock Firestore database initialized and seeded with 4 tasks.")
