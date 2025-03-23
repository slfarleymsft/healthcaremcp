import requests
import hashlib
from src.services.cache_service import CacheService

class ClinicalTrialsTool:
    def __init__(self):
        """Initialize Clinical Trials tool with caching"""
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.cache = CacheService(db_path="healthcare_cache.db")
    
    async def search_trials(self, condition, status="recruiting", max_results=10):
        """
        Search for clinical trials by condition, status, and other parameters
        
        Args:
            condition: Medical condition or disease to search for
            status: Trial status (recruiting, completed, etc.)
            max_results: Maximum number of results to return
        """
        # Create cache key
        cache_key = f"clinical_trials_{condition}_{status}_{max_results}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result and cached_result.get('status') == 'success':
            return cached_result
            
        try:
            return await self._search_clinicaltrials_gov(condition, status, max_results, cache_key)
        except requests.RequestException as e:
            result = {
                "status": "error",
                "error_message": f"Error searching clinical trials: {str(e)}"
            }
            return result
        except Exception as e:
            # Catch any other unexpected errors
            result = {
                "status": "error",
                "error_message": f"Unexpected error: {str(e)}"
            }
            return result
    
    async def _search_clinicaltrials_gov(self, condition, status, max_results, cache_key):
        """Search ClinicalTrials.gov API"""
        # Set up parameters according to the API spec
        params = {
            "query.cond": condition,  # Use query.cond for condition search
            "format": "json",
            "pageSize": max_results,
            "countTotal": "true"
        }
        
        # Add status filter if provided
        if status and status.lower() != "all":
            # Map status to API format if needed
            status_map = {
                "recruiting": "RECRUITING",
                "not_recruiting": "ACTIVE_NOT_RECRUITING",
                "completed": "COMPLETED",
                "active": "RECRUITING"
            }
            mapped_status = status_map.get(status.lower(), status.upper())
            params["filter.overallStatus"] = mapped_status
        
        # Make request
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Format the response
        studies = data.get('studies', [])
        trials = []
        
        for study in studies:
            # Extract data from the nested structure based on the API response
            protocol_section = study.get('protocolSection', {})
            identification = protocol_section.get('identificationModule', {})
            status_module = protocol_section.get('statusModule', {})
            design_module = protocol_section.get('designModule', {})
            conditions_module = protocol_section.get('conditionsModule', {})
            contacts_locations = protocol_section.get('contactsLocationsModule', {})
            sponsor_module = protocol_section.get('sponsorCollaboratorsModule', {})
            
            # Get phases as a string
            phases = design_module.get('phases', [])
            phase_str = ', '.join(phases) if phases else 'Not Specified'
            
            # Get sponsor name
            sponsor_name = ''
            if 'leadSponsor' in sponsor_module:
                sponsor_name = sponsor_module['leadSponsor'].get('name', '')
            
            # Create trial object
            trial = {
                "nct_id": identification.get('nctId', ''),
                "title": identification.get('briefTitle', ''),
                "status": status_module.get('overallStatus', ''),
                "phase": phase_str,
                "study_type": design_module.get('studyType', ''),
                "conditions": conditions_module.get('conditions', []),
                "locations": [],
                "sponsor": sponsor_name
            }
            
            # Add locations if available
            locations = contacts_locations.get('locations', [])
            
            for loc in locations:
                location = {
                    "facility": loc.get('facility', ''),
                    "city": loc.get('city', ''),
                    "state": loc.get('state', ''),
                    "country": loc.get('country', '')
                }
                trial["locations"].append(location)
            
            trials.append(trial)
        
        result = {
            "status": "success",
            "condition": condition,
            "search_status": status,
            "total_results": data.get('totalCount', 0),
            "trials": trials
        }
        
        # Cache for 24 hours (86400 seconds)
        self.cache.set(cache_key, result, ttl=86400)
        
        return result
    