import os
import logging
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.main import mcp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("healthcare-mcp")

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Healthcare MCP API",
    description="Healthcare MCP server for medical information access",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
from typing import Dict, Any, Optional, List, Union

# Define tool request model
class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

# Define error response model
class ErrorResponse(BaseModel):
    status: str = "error"
    error_message: str

# Mount SSE endpoint (but don't mount it at the same path as other APIs)
app.mount("/mcp/sse", mcp.sse_app())

# Define API endpoints for each tool
@app.post("/api/fda_drug_lookup", 
          summary="Look up drug information from the FDA database",
          description="Search for drug information in the FDA database by drug name and search type")
async def api_fda_drug_lookup(drug_name: str, search_type: str = "general"):
    """
    Look up drug information from the FDA database
    
    - **drug_name**: Name of the drug to search for
    - **search_type**: Type of information to retrieve: 'label', 'adverse_events', or 'general'
    """
    try:
        from src.main import fda_drug_lookup
        logger.info(f"FDA drug lookup request: {drug_name}, {search_type}")
        return await fda_drug_lookup(None, drug_name, search_type)
    except Exception as e:
        logger.error(f"Error in FDA drug lookup: {str(e)}")
        return ErrorResponse(error_message=f"Error looking up drug information: {str(e)}")

@app.post("/api/pubmed_search",
          summary="Search for medical literature in PubMed database",
          description="Search for medical literature in PubMed's database of scientific articles")
async def api_pubmed_search(query: str, max_results: int = 5, date_range: str = ""):
    """
    Search for medical literature in PubMed database
    
    - **query**: Search query for medical literature
    - **max_results**: Maximum number of results to return
    - **date_range**: Limit to articles published within years (e.g. '5' for last 5 years)
    """
    try:
        from src.main import pubmed_search
        logger.info(f"PubMed search request: {query}, max_results={max_results}, date_range={date_range}")
        return await pubmed_search(None, query, max_results, date_range)
    except Exception as e:
        logger.error(f"Error in PubMed search: {str(e)}")
        return ErrorResponse(error_message=f"Error searching PubMed: {str(e)}")

@app.post("/api/health_topics",
          summary="Get evidence-based health information on various topics",
          description="Access evidence-based health information from Health.gov")
async def api_health_topics(topic: str, language: str = "en"):
    """
    Get evidence-based health information on various topics
    
    - **topic**: Health topic to search for information
    - **language**: Language for content (en or es)
    """
    try:
        from src.main import health_topics
        logger.info(f"Health topics request: {topic}, language={language}")
        return await health_topics(None, topic, language)
    except Exception as e:
        logger.error(f"Error in health topics: {str(e)}")
        return ErrorResponse(error_message=f"Error fetching health information: {str(e)}")

@app.post("/api/clinical_trials_search",
          summary="Search for clinical trials by condition and status",
          description="Search for ongoing and completed clinical trials")
async def api_clinical_trials(condition: str, status: str = "recruiting", max_results: int = 10):
    """
    Search for clinical trials by condition, status, and other parameters
    
    - **condition**: Medical condition or disease to search for
    - **status**: Trial status (recruiting, completed, active, not_recruiting, or all)
    - **max_results**: Maximum number of results to return
    """
    try:
        from src.main import clinical_trials_search
        logger.info(f"Clinical trials search request: {condition}, status={status}, max_results={max_results}")
        return await clinical_trials_search(None, condition, status, max_results)
    except Exception as e:
        logger.error(f"Error in clinical trials search: {str(e)}")
        return ErrorResponse(error_message=f"Error searching clinical trials: {str(e)}")

@app.post("/api/lookup_icd_code",
          summary="Look up ICD-10 codes by code or description",
          description="Look up ICD-10 codes and medical terminology definitions")
async def api_lookup_icd_code(code: str = None, description: str = None, max_results: int = 10):
    """
    Look up ICD-10 codes by code or description
    
    - **code**: ICD-10 code to look up (optional if description is provided)
    - **description**: Medical condition description to search for (optional if code is provided)
    - **max_results**: Maximum number of results to return
    """
    try:
        from src.main import lookup_icd_code
        logger.info(f"ICD code lookup request: code={code}, description={description}, max_results={max_results}")
        return await lookup_icd_code(None, code, description, max_results)
    except Exception as e:
        logger.error(f"Error in ICD code lookup: {str(e)}")
        return ErrorResponse(error_message=f"Error looking up ICD-10 code: {str(e)}")

@app.get("/api/usage_stats",
         summary="Get usage statistics for the current session",
         description="Get a summary of API usage for the current session")
async def api_usage_stats():
    """
    Get usage statistics for the current session
    
    Returns a summary of API usage for the current session
    """
    try:
        from src.main import get_usage_stats
        logger.info("Usage stats request")
        return await get_usage_stats(None)
    except Exception as e:
        logger.error(f"Error in usage stats: {str(e)}")
        return ErrorResponse(error_message=f"Error getting usage statistics: {str(e)}")

@app.get("/api/all_usage_stats",
         summary="Get overall usage statistics",
         description="Get a summary of API usage across all sessions")
async def api_all_usage_stats():
    """
    Get overall usage statistics
    
    Returns a summary of API usage across all sessions
    """
    try:
        from src.main import get_all_usage_stats
        logger.info("All usage stats request")
        return await get_all_usage_stats(None)
    except Exception as e:
        logger.error(f"Error in all usage stats: {str(e)}")
        return ErrorResponse(error_message=f"Error getting all usage statistics: {str(e)}")

# Add the specific call-tool endpoint
@app.post("/mcp/call-tool",
          summary="Call a specific tool by name",
          description="Generic endpoint to call any tool by name with arguments")
async def call_tool(request: ToolRequest = Body(...)):
    """
    Call a specific tool by name
    
    - **name**: Name of the tool to call
    - **arguments**: Arguments to pass to the tool
    """
    try:
        from src.main import fda_drug_lookup, pubmed_search, health_topics, clinical_trials_search, lookup_icd_code, get_usage_stats, get_all_usage_stats
        
        tool_name = request.name
        arguments = request.arguments
        
        logger.info(f"Tool call request: {tool_name}, arguments={arguments}")
        
        # Map tool names to their corresponding functions
        tool_mapping = {
            "fda_drug_lookup": lambda args: fda_drug_lookup(None, **args),
            "pubmed_search": lambda args: pubmed_search(None, **args),
            "health_topics": lambda args: health_topics(None, **args),
            "clinical_trials_search": lambda args: clinical_trials_search(None, **args),
            "lookup_icd_code": lambda args: lookup_icd_code(None, **args),
            "get_usage_stats": lambda _: get_usage_stats(None),
            "get_all_usage_stats": lambda _: get_all_usage_stats(None)
        }
        
        if tool_name not in tool_mapping:
            logger.warning(f"Tool not found: {tool_name}")
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # Call the appropriate tool function
        result = await tool_mapping[tool_name](arguments)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tool call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health",
         summary="Health check endpoint",
         description="Check if the server is running properly")
async def health_check():
    """
    Health check endpoint
    
    Returns the status and version of the server
    """
    logger.info("Health check request")
    return {"status": "healthy", "version": "1.0.0"}

# Redirect root to docs
@app.get("/",
         summary="Redirect to API documentation",
         description="Redirects to the Swagger UI documentation")
async def redirect_to_docs():
    """
    Redirect to API documentation
    
    Redirects to the Swagger UI documentation
    """
    from fastapi.responses import RedirectResponse
    logger.info("Root request, redirecting to docs")
    return RedirectResponse(url="/docs")

# Information about premium version
@app.get("/premium-info",
         summary="Get information about the premium version",
         description="Get information about the premium version of the Healthcare MCP Server")
async def premium_info():
    """
    Get information about the premium version
    
    Returns information about the premium version of the Healthcare MCP Server
    """
    logger.info("Premium info request")
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
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
