from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Título de la tarea")
    description: Optional[str] = Field(None, max_length=500, description="Descripción detallada de la tarea")
    status: TaskStatus = Field(TaskStatus.TODO, description="Estado de la tarea (todo, in_progress, completed)")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Prioridad de la tarea (low, medium, high)")
    category: Optional[str] = Field("General", description="Categoría o tag de la tarea")
    due_date: Optional[str] = Field(None, description="Fecha de vencimiento (YYYY-MM-DD)")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = None
    due_date: Optional[str] = None

class Task(TaskBase):
    id: str = Field(..., description="ID único de la tarea (generado por Firestore o uuid)")
    created_at: str = Field(..., description="Fecha de creación en formato ISO")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "e23fa282-3d84-482a-bc9f-1d8995a9a4b3",
                "title": "Diseñar Dashboard",
                "description": "Completar la interfaz del dashboard usando CSS Grid y Variables CSS",
                "status": "in_progress",
                "priority": "high",
                "category": "Diseño",
                "due_date": "2026-06-15",
                "created_at": "2026-06-08T12:00:00.000000"
            }
        }
        use_enum_values = True
