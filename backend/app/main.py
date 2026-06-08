from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import settings
from .routers import tasks
from .database import is_mock

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST de TaskFlow para gestionar tareas conectada a Firebase Firestore."
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(tasks.router, prefix="/api")

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_status": "Mock DB" if is_mock else "Firebase Firestore"
    }

# Serve frontend static files if built
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "frontend",
    "dist",
    "frontend",
    "browser"
)

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

    # Catch-all handler for SPA routing: redirect 404 to index.html unless it's an API route
    @app.exception_handler(404)
    async def custom_404_handler(request, exc):
        if not request.url.path.startswith("/api"):
            index_path = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        return FileResponse(os.path.join(frontend_dist, "index.html")) # default fallback

