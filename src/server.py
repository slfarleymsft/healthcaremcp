import os
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from mcp.server.fastmcp import SSETransport
from src.main import mcp

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Healthcare MCP API",
    description="Healthcare MCP server for medical information access",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount MCP SSE endpoint
app.mount("/mcp", mcp.sse_app())

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Redirect root to docs
@app.get("/")
async def redirect_to_docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

# Information about premium version
@app.get("/premium-info")
async def premium_info():
    return {
        "message": "This is the free version of Healthcare MCP Server.",
        "premium_url": "https://healthcaremcp.com", # Replace with your premium service URL
        "features": [
            "Unlimited API calls",
            "Advanced healthcare data tools",
            "Custom integrations",
            "Priority support"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
