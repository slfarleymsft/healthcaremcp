import os
import requests
import hashlib
from src.services.cache_service import CacheService

class HealthFinderTool:
    def __init__(self):
        self.base_url = "https://health.gov/myhealthfinder/api/v3"
        self.cache = CacheService(db_path="healthcare_cache.db")
    
    async def get_health_topics(self, topic, language="en"):
        """Get evidence-based health information on various topics with caching"""
        # Create cache key
        cache_key = f"health_topics_{topic}_{language}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
            
        try:
            # Validate language
            if language not in ["en", "es"]:
                language = "en"  # Default to English
            
            # Search for health topics
            search_url = f"{self.base_url}/topicsearch.json?keyword={topic}&lang={language}"
            
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()
            
            # Process and return the response
            if "Result" not in data:
                result = {
                    "status": "error",
                    "error_message": "Invalid response from Health.gov API"
                }
                return result
            
            result_data = data["Result"]
            
            # Extract topics with more defensive coding
            topics = []
            resources = result_data.get("Resources", {})
            
            # Check if Resources is a dictionary
            if isinstance(resources, dict):
                resource_list = resources.get("Resource", [])
                
                # Check if Resource is a list
                if not isinstance(resource_list, list):
                    resource_list = [resource_list] if resource_list else []
                
                for resource in resource_list:
                    # Make sure resource is a dictionary
                    if not isinstance(resource, dict):
                        continue
                    
                    # Extract title
                    title = resource.get("Title", "")
                    
                    # Extract URL
                    url = resource.get("AccessibleVersion", "")
                    
                    # Extract last updated
                    last_updated = resource.get("LastUpdate", "")
                    
                    # Extract section
                    section = resource.get("Section", "")
                    
                    # Extract description
                    description = ""
                    categories = resource.get("Categories", {})
                    if isinstance(categories, dict):
                        category_list = categories.get("Category", [])
                        if not isinstance(category_list, list):
                            category_list = [category_list] if category_list else []
                        
                        if category_list and isinstance(category_list[0], dict):
                            description = category_list[0].get("Title", "")
                    
                    topics.append({
                        "title": title,
                        "url": url,
                        "last_updated": last_updated,
                        "section": section,
                        "description": description
                    })
            
            result = {
                "status": "success",
                "search_term": topic,
                "language": language,
                "total_results": result_data.get("Total", 0) if isinstance(result_data, dict) else 0,
                "topics": topics
            }
            
            # Cache for 1 week (604800 seconds) since health information doesn't change often
            self.cache.set(cache_key, result, ttl=604800)
            
            return result
                
        except requests.RequestException as e:
            result = {
                "status": "error",
                "error_message": f"Error fetching health information: {str(e)}"
            }
            return result
        except Exception as e:
            # Catch any other unexpected errors
            result = {
                "status": "error",
                "error_message": f"Unexpected error: {str(e)}"
            }
            return result
