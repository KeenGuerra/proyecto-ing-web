import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Render sets PORT; disable reload in production by default or check environments
    environment = os.getenv("ENVIRONMENT", "development")
    reload = environment == "development"
    
    print(f"Iniciando el servidor FastAPI de TaskFlow en el puerto {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=reload)
