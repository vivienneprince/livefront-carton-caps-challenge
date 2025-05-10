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


def string_to_stream(string: str):
    """
    Converts a string into an OpenAI stream format.
    
    Args:
        string (str): The string to split.
        
    Returns:
        list[str]: A list of strings, each containing one line.
    """
    # ChatCompletionChunk(id='ntSh7Z5-zqrih-93d72597d9d2e673', choices=[Choice(delta=ChoiceDelta(content='', function_call=None, role='assistant', tool_calls=None, token_id=None), finish_reason='stop', index=0, logprobs=None, text='')], created=1746856098, model='meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8', object='chat.completion.chunk', service_tier=None, system_fingerprint=None, usage=None),
    # ChatCompletionChunk(id='ntSh7Z5-zqrih-93d72597d9d2e673', choices=[], created=1746856098, model='meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8', object='chat.completion.chunk', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=33, prompt_tokens=132, total_tokens=165))]
    return string.splitlines()