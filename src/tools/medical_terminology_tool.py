import requests
import hashlib
import json
from src.services.cache_service import CacheService

class MedicalTerminologyTool:
    def __init__(self):
        """Initialize Medical Terminology tool with caching"""
        self.icd10_base_url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
        self.cache = CacheService(db_path="healthcare_cache.db")
    
    async def lookup_icd_code(self, code=None, description=None, max_results=10):
        """
        Look up ICD-10 codes by code or description
        
        Args:
            code: ICD-10 code to look up (optional if description is provided)
            description: Medical condition description to search for (optional if code is provided)
            max_results: Maximum number of results to return
        """
        if not code and not description:
            return {
                "status": "error",
                "error_message": "Either code or description must be provided"
            }
        
        # Determine search term
        search_term = code if code else description
        
        # Create cache key
        cache_key = f"icd10_{search_term}_{max_results}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
            
        try:
            # Build parameters
            params = {
                "terms": search_term,
                "maxList": max_results,
                "df": "code,name"  # Display fields
            }
            
            # Make request
            response = requests.get(self.icd10_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format the results
            codes = []
            if len(data) >= 4 and isinstance(data[3], list):
                code_values = data[1]  # The codes are in the second element
                descriptions = data[3]  # The descriptions are in the fourth element
                
                for i in range(len(code_values)):
                    # Parse out the ICD-10 code details
                    code_text = code_values[i]
                    description_text = descriptions[i][1] if len(descriptions[i]) > 1 else "No description"
                    
                    # Extract category information (usually the first 3 characters)
                    category = code_text.split('.')[0] if '.' in code_text else code_text[:3]
                    
                    code_info = {
                        "code": code_text,
                        "description": description_text,
                        "category": category
                    }
                    
                    # Add chapter information if we can determine it
                    chapter = self._get_icd10_chapter(category)
                    if chapter:
                        code_info["chapter"] = chapter["number"]
                        code_info["chapter_description"] = chapter["description"]
                    
                    codes.append(code_info)
                
                result = {
                    "status": "success",
                    "search_term": search_term,
                    "total_results": len(codes),
                    "results": codes
                }
            else:
                result = {
                    "status": "success",
                    "search_term": search_term,
                    "total_results": 0,
                    "results": []
                }
            
            # Cache for 30 days (ICD-10 codes don't change frequently)
            self.cache.set(cache_key, result, ttl=30*86400)
            
            return result
                
        except requests.RequestException as e:
            result = {
                "status": "error",
                "error_message": f"Error looking up ICD-10 code: {str(e)}"
            }
            return result
        except Exception as e:
            # Catch any other unexpected errors
            result = {
                "status": "error",
                "error_message": f"Unexpected error: {str(e)}"
            }
            return result
    
    def _get_icd10_chapter(self, category_code):
        """
        Get the ICD-10 chapter information for a given category code.
        This is a simplified version that works for the main ICD-10-CM chapters.
        """
        # Convert to uppercase just to be safe
        category_code = category_code.upper()
        
        # The first character of the category code determines the chapter
        first_char = category_code[0] if category_code else ''
        
        # Define chapters
        if 'A' <= first_char <= 'B':
            return {"number": "I", "description": "Certain infectious and parasitic diseases"}
        elif first_char == 'C' or (first_char == 'D' and category_code <= 'D48'):
            return {"number": "II", "description": "Neoplasms"}
        elif first_char == 'D' and category_code >= 'D50':
            return {"number": "III", "description": "Diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism"}
        elif first_char == 'E':
            return {"number": "IV", "description": "Endocrine, nutritional and metabolic diseases"}
        elif first_char == 'F':
            return {"number": "V", "description": "Mental and behavioral disorders"}
        elif first_char == 'G':
            return {"number": "VI", "description": "Diseases of the nervous system"}
        elif first_char == 'H' and category_code <= 'H59':
            return {"number": "VII", "description": "Diseases of the eye and adnexa"}
        elif first_char == 'H' and category_code >= 'H60':
            return {"number": "VIII", "description": "Diseases of the ear and mastoid process"}
        elif first_char == 'I':
            return {"number": "IX", "description": "Diseases of the circulatory system"}
        elif first_char == 'J':
            return {"number": "X", "description": "Diseases of the respiratory system"}
        elif first_char == 'K':
            return {"number": "XI", "description": "Diseases of the digestive system"}
        elif first_char == 'L':
            return {"number": "XII", "description": "Diseases of the skin and subcutaneous tissue"}
        elif first_char == 'M':
            return {"number": "XIII", "description": "Diseases of the musculoskeletal system and connective tissue"}
        elif first_char == 'N':
            return {"number": "XIV", "description": "Diseases of the genitourinary system"}
        elif first_char == 'O':
            return {"number": "XV", "description": "Pregnancy, childbirth and the puerperium"}
        elif first_char == 'P':
            return {"number": "XVI", "description": "Certain conditions originating in the perinatal period"}
        elif first_char == 'Q':
            return {"number": "XVII", "description": "Congenital malformations, deformations and chromosomal abnormalities"}
        elif first_char == 'R':
            return {"number": "XVIII", "description": "Symptoms, signs and abnormal clinical and laboratory findings, not elsewhere classified"}
        elif first_char == 'S' or first_char == 'T':
            return {"number": "XIX", "description": "Injury, poisoning and certain other consequences of external causes"}
        elif first_char == 'V' or first_char == 'W' or first_char == 'X' or first_char == 'Y':
            return {"number": "XX", "description": "External causes of morbidity and mortality"}
        elif first_char == 'Z':
            return {"number": "XXI", "description": "Factors influencing health status and contact with health services"}
        else:
            return None