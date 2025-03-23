import os
import requests
import hashlib
from datetime import datetime
from src.services.cache_service import CacheService

class PubMedTool:
    def __init__(self):
        self.api_key = os.getenv("PUBMED_API_KEY", "")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.cache = CacheService(db_path="healthcare_cache.db")
    
    async def search_literature(self, query, max_results=5, date_range=""):
        """Search for medical literature in PubMed database with caching"""
        # Create cache key
        cache_key = f"pubmed_search_{query}_{max_results}_{date_range}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
            
        try:
            # Add date range filter if provided
            if date_range:
                try:
                    years_back = int(date_range)
                    current_year = datetime.now().year
                    min_year = current_year - years_back
                    query += f" AND {min_year}:{current_year}[pdat]"
                except ValueError:
                    # If date_range isn't a valid integer, just ignore it
                    pass
            
            # Search PubMed to get article IDs
            search_url = f"{self.base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&format=json"
            if self.api_key:
                search_url += f"&api_key={self.api_key}"
            
            search_response = requests.get(search_url)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            total_results = search_data.get("esearchresult", {}).get("count", 0)
            
            # If we have results, fetch article details
            articles = []
            if id_list:
                ids_str = ",".join(id_list)
                summary_url = f"{self.base_url}esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
                if self.api_key:
                    summary_url += f"&api_key={self.api_key}"
                
                summary_response = requests.get(summary_url)
                summary_response.raise_for_status()
                summary_data = summary_response.json()
                
                # Process article data
                for article_id in id_list:
                    if article_id in summary_data.get("result", {}):
                        article_data = summary_data["result"][article_id]
                        
                        authors = []
                        if "authors" in article_data:
                            authors = [author.get("name", "") for author in article_data["authors"] if "name" in author]
                        
                        article = {
                            "id": article_id,
                            "title": article_data.get("title", ""),
                            "authors": authors,
                            "journal": article_data.get("fulljournalname", ""),
                            "publication_date": article_data.get("pubdate", ""),
                            "abstract_url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/",
                        }
                        
                        articles.append(article)
            
            # Create result object
            result = {
                "status": "success",
                "query": query,
                "total_results": total_results,
                "articles": articles
            }
            
            # Cache for 12 hours (43200 seconds)
            self.cache.set(cache_key, result, ttl=43200)
            
            return result
                
        except requests.RequestException as e:
            result = {
                "status": "error",
                "error_message": f"Error searching PubMed: {str(e)}"
            }
            return result
