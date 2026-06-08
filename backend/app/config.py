import os
from dotenv import load_dotenv

# Load env variables from .env file if it exists
load_dotenv()

class Settings:
    PROJECT_NAME: str = "TaskFlow API"
    VERSION: str = "1.0.0"
    
    # Path to Firebase Service Account JSON file
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "firebase-credentials.json"
        )
    )
    
    # CORS Origins allowed
    ALLOWED_ORIGINS: list = [
        "http://localhost:4200",  # Angular default port
        "http://127.0.0.1:4200",
    ] + [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]

settings = Settings()
