# TaskFlow: Angular + FastAPI + Firebase Firestore

¡Bienvenido a **TaskFlow**, un gestor de tareas colaborativo y Kanban interactivo premium con frontend en Angular, backend en FastAPI y base de datos Firebase Firestore.

El proyecto está diseñado para funcionar **fuera de la caja** (out-of-the-box): si no configuras tus credenciales de Firebase, el servidor usará automáticamente una **Base de Datos Simulada en Memoria (Mock DB)** pre-cargada con tareas de demostración, permitiendo que explores el sistema inmediatamente.

---

## Estructura del Proyecto

- `backend/`: API construida con FastAPI y Firebase Admin SDK.
- `frontend/`: Aplicación de una sola página (SPA) construida con Angular.

---

## Configuración y Ejecución del Backend

### Requisitos Previos
- Python 3.10 o superior

### Pasos de Inicio
1. Dirígete a la carpeta del backend:
   ```bash
   cd backend
   ```
2. El entorno virtual ya ha sido creado en `backend/venv` y las dependencias han sido instaladas. Puedes activarlo con:
   - **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   - **Linux/macOS:** `source venv/bin/activate`
3. Ejecuta el servidor:
   ```bash
   python run.py
   ```
   *El servidor se levantará en [http://localhost:8000](http://localhost:8000).*
   *Puedes consultar la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs).*

### Conectar a Firebase Firestore Real
1. Ve a la consola de Firebase -> Configuración del proyecto -> Cuentas de servicio.
2. Genera una nueva clave privada en formato JSON.
3. Descarga el archivo, renombralo a `firebase-credentials.json` y colócalo en la raíz del proyecto (`d:/PROYECTOINGWEB/firebase-credentials.json`).
4. Reinicia el servidor backend. Detectará automáticamente el archivo y se conectará a tu Firestore real.

---

## Configuración y Ejecución del Frontend

### Requisitos Previos
- Node.js (v18+)
- npm (v9+)

### Pasos de Inicio
1. Dirígete a la carpeta del frontend:
   ```bash
   cd frontend
   ```
2. Ejecuta el servidor de desarrollo:
   ```bash
   npm start
   ```
3. Abre tu navegador en [http://localhost:4200](http://localhost:4200).

---

## Tecnologías Utilizadas

- **Frontend**: Angular 17+ / Angular CLI con Vanilla CSS premium y animaciones.
- **Backend**: FastAPI, Pydantic v2 y Uvicorn.
- **Base de datos**: Google Cloud Firestore (Firebase Admin SDK) con fallback in-memory.
