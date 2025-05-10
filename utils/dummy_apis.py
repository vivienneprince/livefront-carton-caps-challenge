"""Functions that return dummy data for demo purposes."""

from datetime import datetime, timedelta
import json



def get_referal_code(user_id: str) -> dict[str, str]:
    """Returns a dummy referral code.

    This function is a placeholder and should be replaced with an API call
    to a real service that manages the referral codes.

    Args:
        user_id (str)

    Returns:
        dict[str, str]: A dictionary containing a dummy referral code and an expiration time.
        The referral code is a string formatted as "REF-{user_id}".
        The expiration time is a string in ISO 8601 format.
    """
    two_days_from_now = datetime.now() + timedelta(days=2)
    dummy_api_response = {
        "referral_code": f"REF-{user_id}",
        "expiration_time": two_days_from_now.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return json.dumps(dummy_api_response)
