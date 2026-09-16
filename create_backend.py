import os

backend_dir = r"c:\Users\batal\OneDrive\Desktop\satquery-ai\backend"
dirs = [
    "app",
    "app/api",
    "app/api/routes",
    "app/core",
    "app/schemas",
    "app/utils"
]

for d in dirs:
    os.makedirs(os.path.join(backend_dir, d), exist_ok=True)

files_content = {
    "app/__init__.py": "",
    "app/api/__init__.py": "",
    "app/api/routes/__init__.py": "",
    "app/core/__init__.py": "",
    "app/schemas/__init__.py": "",
    "app/utils/__init__.py": "",
    
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health

app = FastAPI(
    title="SatQuery AI API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
""",
    
    "app/api/routes/health.py": """from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", service="satquery-ai")
""",
    
    "app/core/config.py": """import os

class Settings:
    PROJECT_NAME: str = "SatQuery AI API"
    # Future settings (like API keys) can be added here
    # Example: SOME_API_KEY = os.getenv("SOME_API_KEY", "default")
    
settings = Settings()
""",
    
    "app/schemas/health.py": """from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    service: str
""",
    
    "requirements.txt": """fastapi
uvicorn[standard]
pydantic
python-multipart
""",
    
    ".env": """# SatQuery AI API Environment Variables
""",
    
    ".gitignore": """__pycache__/
*.py[cod]
.venv/
venv/
.env
.pytest_cache/
.idea/
.vscode/
""",
    
    "README.md": """# SatQuery AI Backend

This is the backend foundation for SatQuery AI, built with FastAPI.

## Setup Instructions

1. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   ```

2. **Activate the virtual environment:**
   ```powershell
   .venv\\Scripts\\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the FastAPI server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

## Development and Testing

- **Health Endpoint:** `GET http://127.0.0.1:8000/api/health` 
  - Expected Response: `{"status": "ok", "service": "satquery-ai"}`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`
"""
}

for path, content in files_content.items():
    file_path = os.path.join(backend_dir, path)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Backend scaffolding completed.")
