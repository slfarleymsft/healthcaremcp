import os
import requests
import hashlib
from src.services.cache_service import CacheService

class FDATool:
    def __init__(self):
        self.api_key = os.getenv("FDA_API_KEY", "")
        self.base_url = "https://api.fda.gov/drug"
        self.cache = CacheService(db_path="healthcare_cache.db")
    
    async def lookup_drug(self, drug_name, search_type="general"):
        """Look up drug information from the FDA database with caching"""
        # Create cache key
        cache_key = f"fda_drug_{search_type}_{drug_name}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # If not in cache, fetch from API
        try:
            if search_type == "label":
                endpoint = f"{self.base_url}/label.json"
                query = f"openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}"
            elif search_type == "adverse_events":
                endpoint = f"{self.base_url}/event.json"
                query = f"patient.drug.medicinalproduct:{drug_name}"
            else:  # general
                endpoint = f"{self.base_url}/ndc.json"
                query = f"generic_name:{drug_name}+OR+brand_name:{drug_name}"
            
            api_url = f"{endpoint}?search={query}&limit=3"
            if self.api_key:
                api_url += f"&api_key={self.api_key}"
            
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            # Process and cache the response
            result = {
                "status": "success",
                "drug_name": drug_name,
                "results": data.get("results", []),
                "total_results": data.get("meta", {}).get("results", {}).get("total", 0)
            }
            
            # Cache for 24 hours (86400 seconds)
            self.cache.set(cache_key, result, ttl=86400)
            
            return result
                
        except requests.RequestException as e:
            result = {
                "status": "error",
                "error_message": f"Error fetching drug information: {str(e)}"
            }
            return result
