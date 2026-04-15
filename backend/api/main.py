import os
# Set thread count FIRST to prevent KMeans memory leak warnings
os.environ["OMP_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import uuid
from typing import Optional
from backend.pipeline.manager import PipelineManager

app = FastAPI(title="Quant Research & Risk Engine API")

# Configure CORS for Streamlit Cloud <-> Vercel communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In strict prod, replace with ["https://your-streamlit-app.streamlit.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = PipelineManager()

# Temporary storage for uploads and results
# Vercel only allows writing to /tmp
UPLOAD_DIR = "/tmp/uploads" if os.getenv("VERCEL") else "temp_uploads"
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception:
    pass

# Simple in-memory cache for results (in production, use Redis/DB)
results_cache = {}

class AnalysisRequest(BaseModel):
    ticker: str
    start_date: str = "2022-01-01"
    end_date: str = "2024-01-01"
    simulations: Optional[int] = 10000

class AnalysisResponse(BaseModel):
    job_id: str
    status: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "Quant Engine API is running"}

@app.get("/health")
def health_check():
    """Endpoint for monitoring tools to verify the service is alive."""
    return {"status": "healthy", "timestamp": str(uuid.uuid4())}

@app.post("/analyze")
async def run_analysis(request: AnalysisRequest):
    """
    Triggers the full quant pipeline for a ticker.
    """
    try:
        # In a real async prod environment, this would be a background task
        # or sent to a Celery worker. For this local CPU-friendly version, 
        # we run it synchronously but keep it behind the API.
        result = pipeline.run_analysis(
            ticker=request.request_ticker if hasattr(request, 'request_ticker') else request.ticker,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        job_id = str(uuid.uuid4())
        results_cache[job_id] = result
        
        # The manager already runs clean_json on the result
        return {"job_id": job_id, "status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """
    Uploads a custom dataset for analysis.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"file_id": file_id, "file_path": file_path, "message": "File uploaded successfully"}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    """
    Fetches the result of a previously run analysis.
    """
    if job_id not in results_cache:
        raise HTTPException(status_code=404, detail="Job result not found.")
    
    return results_cache[job_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
