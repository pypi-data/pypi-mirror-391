from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Rodin Gen-2 MCP Server",
    description="MCP Server for Rodin Gen-2 API integration",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
RODIN_API_BASE_URL = os.getenv("RODIN_API_BASE_URL", "https://api.rodin.gen2")
RODIN_API_KEY = os.getenv("RODIN_API_KEY")

if not RODIN_API_KEY:
    raise ValueError("RODIN_API_KEY environment variable is not set")

# Models
class RodinRequest(BaseModel):
    prompt: str
    parameters: Optional[Dict[str, Any]] = None

class RodinResponse(BaseModel):
    result: Dict[str, Any]
    status: str = "success"

# Client for making requests to Rodin API
class RodinClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None):
        async with httpx.AsyncClient() as client:
            payload = {"prompt": prompt}
            if parameters:
                payload.update(parameters)
                
            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
                headers=self.headers,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Rodin API error: {response.text}"
                )
                
            return response.json()

# Initialize Rodin client
rodin_client = RodinClient(RODIN_API_BASE_URL, RODIN_API_KEY)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Rodin Gen-2 MCP Server is running"}

@app.post("/generate", response_model=RodinResponse)
async def generate_text(request: RodinRequest):
    """
    Generate text using Rodin Gen-2 API
    """
    try:
        result = await rodin_client.generate(
            prompt=request.prompt,
            parameters=request.parameters
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
