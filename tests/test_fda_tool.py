import asyncio
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.fda_tool import FDATool

async def test_fda_drug_lookup():
    """Test the FDA drug lookup functionality"""
    print("\n=== Testing FDA Drug Lookup ===")
    
    # Initialize the tool
    tool = FDATool()
    
    # Test looking up a common drug with general info
    print("\nLooking up general info for 'aspirin'...")
    result = await tool.lookup_drug("aspirin", "general")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Drug name: {result.get('drug_name', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show drug info
    drugs = result.get('results', [])
    print(f"Returned {len(drugs)} drugs:")
    
    for i, drug in enumerate(drugs):
        if i >= 2:  # Limit to first 2 results for readability
            print(f"\n...and {len(drugs) - 2} more results")
            break
            
        print(f"\n{i+1}. Generic name: {drug.get('generic_name', 'Unknown')}")
        print(f"   Brand name: {drug.get('brand_name', 'Unknown')}")
        if 'manufacturer_name' in drug.get('openfda', {}):
            print(f"   Manufacturer: {drug['openfda']['manufacturer_name'][0] if len(drug['openfda']['manufacturer_name']) > 0 else 'Unknown'}")
        if 'route' in drug:
            print(f"   Route: {', '.join(drug.get('route', ['Unknown']))}")
        if 'dosage_form' in drug:
            print(f"   Dosage form: {drug.get('dosage_form', 'Unknown')}")
    
    # Test looking up a drug with label info
    print("\nLooking up label info for 'metformin'...")
    result = await tool.lookup_drug("metformin", "label")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Drug name: {result.get('drug_name', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show drug labels (limited)
    labels = result.get('results', [])
    print(f"Returned {len(labels)} labels:")
    
    for i, label in enumerate(labels):
        if i >= 1:  # Limit to first result for readability
            print(f"\n...and {len(labels) - 1} more results")
            break
            
        print(f"\n{i+1}. Drug: {label.get('openfda', {}).get('generic_name', ['Unknown'])[0] if 'generic_name' in label.get('openfda', {}) else 'Unknown'}")
        
        # Show warnings if available
        if 'warnings' in label:
            print(f"   Warnings: {label['warnings'][:150]}...")
        
        # Show indications if available
        if 'indications_and_usage' in label:
            print(f"   Indications: {label['indications_and_usage'][:150]}...")
    
    # Test looking up a drug with adverse events
    print("\nLooking up adverse events for 'ibuprofen'...")
    result = await tool.lookup_drug("ibuprofen", "adverse_events")
    
    # Pretty print the result
    print(f"Status: {result['status']}")
    print(f"Drug name: {result.get('drug_name', '')}")
    print(f"Total results: {result.get('total_results', 0)}")
    
    # Show adverse events (limited)
    events = result.get('results', [])
    print(f"Returned {len(events)} adverse event reports:")
    
    if len(events) > 0:
        print(f"\nShowing sample adverse events:")
        
        # Get the first event
        event = events[0]
        
        # Show patient info if available
        if 'patient' in event:
            patient = event['patient']
            print(f"  Patient age: {patient.get('patientonsetage', 'Unknown')}")
            print(f"  Patient sex: {patient.get('patientsex', 'Unknown')}")
            
            # Show reactions if available
            if 'reaction' in patient:
                reactions = patient['reaction']
                print(f"  Reactions ({len(reactions)}):")
                for i, reaction in enumerate(reactions[:3]):
                    print(f"    - {reaction.get('reactionmeddrapt', 'Unknown')}")
                if len(reactions) > 3:
                    print(f"    - ...and {len(reactions) - 3} more")

if __name__ == "__main__":
    asyncio.run(test_fda_drug_lookup())