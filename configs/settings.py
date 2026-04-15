import os

# Threading Control (Fix for KMeans memory leak warning)
os.environ["OMP_NUM_THREADS"] = "1"

# API Settings
API_TITLE = "Quant Research & Risk Engine"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "temp_uploads")

# Default Parameters
DEFAULT_SIMULATIONS = int(os.getenv("DEFAULT_SIMULATIONS", 10000))
DEFAULT_HORIZON = 252 # trading days
NU_FALLBACK = 5.0
NU_BOUNDS = (2.0, 30.0)

# Environment Type
IS_PROD = os.getenv("VERCEL", False) # Vercel sets this automatically
