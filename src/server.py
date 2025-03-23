import os
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
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

# Import necessary components for request handling
from fastapi import Body
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Define tool request model
class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

# Mount SSE endpoint (but don't mount it at the same path as other APIs)
app.mount("/mcp/sse", mcp.sse_app())

# Define API endpoints for each tool
@app.post("/api/fda_drug_lookup")
async def api_fda_drug_lookup(drug_name: str, search_type: str = "general"):
    from src.main import fda_drug_lookup
    return await fda_drug_lookup(None, drug_name, search_type)

@app.post("/api/pubmed_search")
async def api_pubmed_search(query: str, max_results: int = 5, date_range: str = ""):
    from src.main import pubmed_search
    return await pubmed_search(None, query, max_results, date_range)

@app.post("/api/health_topics")
async def api_health_topics(topic: str, language: str = "en"):
    from src.main import health_topics
    return await health_topics(None, topic, language)

@app.post("/api/clinical_trials_search")
async def api_clinical_trials(condition: str, status: str = "recruiting", max_results: int = 10):
    from src.main import clinical_trials_search
    return await clinical_trials_search(None, condition, status, max_results)

@app.post("/api/lookup_icd_code")
async def api_lookup_icd_code(code: str = None, description: str = None, max_results: int = 10):
    from src.main import lookup_icd_code
    return await lookup_icd_code(None, code, description, max_results)

@app.get("/api/usage_stats")
async def api_usage_stats():
    from src.main import get_usage_stats
    return await get_usage_stats(None)

# Add the specific call-tool endpoint
@app.post("/mcp/call-tool")
async def call_tool(request: ToolRequest = Body(...)):
    from src.main import fda_drug_lookup, pubmed_search, health_topics, clinical_trials_search, lookup_icd_code, get_usage_stats
    
    tool_name = request.name
    arguments = request.arguments
    
    # Map tool names to their corresponding functions
    tool_mapping = {
        "fda_drug_lookup": lambda args: fda_drug_lookup(None, **args),
        "pubmed_search": lambda args: pubmed_search(None, **args),
        "health_topics": lambda args: health_topics(None, **args),
        "clinical_trials_search": lambda args: clinical_trials_search(None, **args),
        "lookup_icd_code": lambda args: lookup_icd_code(None, **args),
        "get_usage_stats": lambda _: get_usage_stats(None)
    }
    
    if tool_name not in tool_mapping:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    try:
        # Call the appropriate tool function
        result = await tool_mapping[tool_name](arguments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create dedicated API endpoints for each tool
@app.post("/api/fda_drug_lookup")
async def api_fda_drug_lookup(drug_name: str, search_type: str = "general"):
    from src.main import fda_drug_lookup
    return await fda_drug_lookup(None, drug_name, search_type)

@app.post("/api/pubmed_search")
async def api_pubmed_search(query: str, max_results: int = 5, date_range: str = ""):
    from src.main import pubmed_search
    return await pubmed_search(None, query, max_results, date_range)

@app.post("/api/health_topics")
async def api_health_topics(topic: str, language: str = "en"):
    from src.main import health_topics
    return await health_topics(None, topic, language)

@app.post("/api/clinical_trials_search")
async def api_clinical_trials(condition: str, status: str = "recruiting", max_results: int = 10):
    from src.main import clinical_trials_search
    return await clinical_trials_search(None, condition, status, max_results)

@app.post("/api/lookup_icd_code")
async def api_lookup_icd_code(code: str = None, description: str = None, max_results: int = 10):
    from src.main import lookup_icd_code
    return await lookup_icd_code(None, code, description, max_results)

@app.get("/api/usage_stats")
async def api_usage_stats():
    from src.main import get_usage_stats
    return await get_usage_stats(None)

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
