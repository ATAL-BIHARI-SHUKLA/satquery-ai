# SatQuery AI Backend

This is the backend foundation for SatQuery AI, built with FastAPI.

## Setup Instructions

1. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   ```

2. **Activate the virtual environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
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
