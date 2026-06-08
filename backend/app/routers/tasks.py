from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from ..database import db
from ..models.task import Task, TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

# Helper function to convert Firestore doc snapshot to Task model dict
def doc_to_task_dict(doc_id: str, doc_data: dict) -> dict:
    return {
        "id": doc_id,
        "title": doc_data.get("title", ""),
        "description": doc_data.get("description"),
        "status": doc_data.get("status", "todo"),
        "priority": doc_data.get("priority", "medium"),
        "category": doc_data.get("category", "General"),
        "due_date": doc_data.get("due_date"),
        "created_at": doc_data.get("created_at", datetime.utcnow().isoformat())
    }

@router.get("", response_model=List[Task])
async def get_tasks():
    """
    Obtener todas las tareas de la base de datos Firestore (o Mock DB).
    """
    try:
        tasks_ref = db.collection("tasks")
        docs = tasks_ref.stream()
        
        tasks_list = []
        for doc in docs:
            tasks_list.append(doc_to_task_dict(doc.id, doc.to_dict()))
            
        return tasks_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las tareas: {str(e)}"
        )

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    Obtener una tarea específica por su ID.
    """
    try:
        doc_ref = db.collection("tasks").document(task_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID '{task_id}' no encontrada."
            )
            
        return doc_to_task_dict(doc.id, doc.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la tarea: {str(e)}"
        )

@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate):
    """
    Crear una nueva tarea y guardarla en Firestore (o Mock DB).
    """
    try:
        # Prepare task data dict
        task_data = task_in.model_dump()
        task_data["created_at"] = datetime.utcnow().isoformat()
        
        # Generate a unique ID (if using mock, add method returns it. In real firestore, add() creates it)
        # To maintain uniform code for mock & real, we can generate ID ourselves or use firestore's creation.
        # Generating ID ourselves is highly reliable and uniform.
        task_id = str(uuid.uuid4())
        
        doc_ref = db.collection("tasks").document(task_id)
        doc_ref.set(task_data)
        
        return doc_to_task_dict(task_id, task_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tarea: {str(e)}"
        )

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_in: TaskUpdate):
    """
    Actualizar campos de una tarea existente.
    """
    try:
        doc_ref = db.collection("tasks").document(task_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID '{task_id}' no encontrada."
            )
            
        # Get only set values
        update_data = task_in.model_dump(exclude_unset=True)
        if not update_data:
            # Nothing to update, return current
            return doc_to_task_dict(doc.id, doc.to_dict())
            
        doc_ref.update(update_data)
        
        # Get updated data
        updated_doc = doc_ref.get()
        return doc_to_task_dict(updated_doc.id, updated_doc.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la tarea: {str(e)}"
        )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """
    Eliminar una tarea de la base de datos.
    """
    try:
        doc_ref = db.collection("tasks").document(task_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID '{task_id}' no encontrada."
            )
            
        doc_ref.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la tarea: {str(e)}"
        )
