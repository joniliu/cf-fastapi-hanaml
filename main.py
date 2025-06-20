#! /usr/bin/env python
import os
import logging
import sys
import uvicorn
from fastapi import FastAPI
from api.route import api_router

# Initialize FastAPI app
app = FastAPI()
# Include API router
app.include_router(api_router, prefix="/api")

# Configure logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
