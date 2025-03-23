#!/usr/bin/env python3
import asyncio
import sys
import os
import argparse

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_fda_tool import test_fda_drug_lookup
from tests.test_pubmed_tool import test_pubmed_search
from tests.test_healthfinder_tool import test_health_topics
from tests.test_clinical_trials_tool import test_clinical_trials_search
from tests.test_medical_terminology_tool import test_icd_code_lookup

async def run_all_tests():
    """Run all tests sequentially"""
    print("\n=== Running All Tests ===\n")
    
    # Run existing tool tests
    await test_fda_drug_lookup()
    await test_pubmed_search()
    await test_health_topics()
    
    # Run new tool tests
    await test_clinical_trials_search()
    await test_icd_code_lookup()
    
    print("\n=== All Tests Completed ===\n")

def test_http_server():
    """Test running the HTTP server"""
    print("\n=== Testing HTTP Server ===\n")
    
    # Import the app
    from src.server import app
    import uvicorn
    
    # Start the server (this will block until Ctrl+C)
    print("Starting HTTP server on port 8000...")
    print("Open http://localhost:8000/ in your browser to see the API documentation")
    print("Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run tests for Healthcare MCP")
    parser.add_argument("--server", action="store_true", help="Test HTTP server")
    parser.add_argument("--fda", action="store_true", help="Test FDA drug lookup tool only")
    parser.add_argument("--pubmed", action="store_true", help="Test PubMed search tool only")
    parser.add_argument("--health", action="store_true", help="Test Health Topics tool only")
    parser.add_argument("--trials", action="store_true", help="Test clinical trials tool only")
    parser.add_argument("--icd", action="store_true", help="Test ICD-10 tool only")
    args = parser.parse_args()
    
    # Run the appropriate test(s)
    if args.server:
        test_http_server()
    elif args.fda:
        asyncio.run(test_fda_drug_lookup())
    elif args.pubmed:
        asyncio.run(test_pubmed_search())
    elif args.health:
        asyncio.run(test_health_topics())
    elif args.trials:
        asyncio.run(test_clinical_trials_search())
    elif args.icd:
        asyncio.run(test_icd_code_lookup())
    else:
        # Run all tests by default
        asyncio.run(run_all_tests())