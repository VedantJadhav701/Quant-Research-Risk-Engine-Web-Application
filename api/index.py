# Vercel Serverless Function Bridge
import os
import sys

# Add the project root to sys.path so the app can find the backend package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.main import app

# Vercel needs the app object to be accessible at the module level
# When using Fast API, it looks for an object named 'app'
