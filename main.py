from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from routes import router
import uvicorn

# Create a Limiter instance to apply rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI instance
app = FastAPI()

# Add SlowAPI middleware for rate limiting functionality
app.add_middleware(SlowAPIMiddleware)

# Set the Limiter instance in the app's state for global access
app.state.limiter = limiter

# Include routes from routes.py
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
