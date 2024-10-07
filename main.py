import os  # Import os to access environment variables
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware to handle cross-origin requests
from routes import router
import uvicorn

# Create a Limiter instance to apply rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI instance
app = FastAPI()

# CORS middleware to allow cross-origin requests for GET access to anyone
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow public access to GET requests for everyone
    allow_credentials=True,
    allow_methods=["GET"],  # Restrict public access to GET requests only
    allow_headers=["*"],  # Allow all headers for requests
)

# Add SlowAPI middleware for rate limiting functionality
app.add_middleware(SlowAPIMiddleware)

# Set the Limiter instance in the app's state for global access
app.state.limiter = limiter

# Include routes from routes.py
app.include_router(router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
