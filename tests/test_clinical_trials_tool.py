import asyncio
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.clinical_trials_tool import ClinicalTrialsTool

async def test_clinical_trials_search():
    """Test the clinical trials search functionality"""
    print("\n=== Testing Clinical Trials Search ===")
    
    # Initialize the tool
    tool = ClinicalTrialsTool()
    
    # Test searching for diabetes trials from ClinicalTrials.gov
    print("\nSearching for diabetes trials (ClinicalTrials.gov)...")
    result = await tool.search_trials("diabetes", "recruiting", 3)
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    
    # Print error message if there is one
    if result['status'] == 'error':
        print(f"Error: {result.get('error_message', 'Unknown error')}")
    
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show trials
    trials = result.get('trials', [])
    print(f"Returned {len(trials)} trials:")
    
    for i, trial in enumerate(trials):
        print(f"\n{i+1}. {trial.get('title', 'No title')}")
        print(f"   ID: {trial.get('nct_id', 'No ID')}")
        print(f"   Status: {trial.get('status', 'Unknown')}")
        print(f"   Phase: {trial.get('phase', 'Unknown')}")
        
        # Show locations (limited to first 2)
        locations = trial.get('locations', [])
        if locations:
            print(f"   Locations ({len(locations)} total):")
            for j, loc in enumerate(locations[:2]):
                print(f"     - {loc.get('facility', 'Unknown')} ({loc.get('city', '')}, {loc.get('state', '')})")
            if len(locations) > 2:
                print(f"     - ...and {len(locations) - 2} more")

if __name__ == "__main__":
    asyncio.run(test_clinical_trials_search())