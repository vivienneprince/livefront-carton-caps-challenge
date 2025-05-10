import json
import re
import logging


log = logging.getLogger(__name__)


def extract_json_from_response(json_response: str) -> dict:
    """
    Extracts the JSON part from a string that contains JSON data.
    
    Args:
        json_response (str): string containing JSON data.
        
    Returns:
        dict: The extracted data as a dictionary.
    """
    try: 
        json_string = re.findall(r'(?s)\{.*\}', json_response)[0] 
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        log.error(f"Failed to decode JSON: {e}")
        data = {}
    except IndexError as e:
        log.error(f"Failed to find JSON in response: {e}")
        data = {}
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        data = {}
    return data