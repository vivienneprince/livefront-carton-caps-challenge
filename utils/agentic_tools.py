"""Tool definitions for Agentic calls"""


GET_REFERRAL_CODE_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "get_referal_code",
            "description": "Get the referal code for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID for which to get the referal code."
                    }
                }
            }
        }
    }
]