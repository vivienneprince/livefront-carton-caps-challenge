"""Functions that define the behavior of the chat agent."""

import itertools
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv

from utils.agentic_tools import GET_REFERRAL_CODE_TOOL
from utils.llms import CustomOpenAIClient
from utils.dummy_apis import get_referal_code
from utils.nlp import extract_json_from_response
from utils.prompts import (
    format_query_classification_prompt,
    format_referral_query_prompt,
    # format_other_answer_prompt,
)


load_dotenv()
log = logging.getLogger(__name__)


def classify_query(
    query: str,
    chat_history: list[dict[str, str]] = [],
    classifier: Any = CustomOpenAIClient(enable_streaming=False),
) -> str:
    """Classify the query using the text classifier. Classes: "product recommendation", "referral", "unsure", "other".

    Currently, the classifier is not avaliable in the demo, so this function uses the LLM instead to classify the query.

    Args:
        query (str): The query to classify.
        chat_history (list[dict[str, str]])
        classifier (str): The URL of the text classifier. Defaults to os.getenv("CLASSIFIER_URL").

    Returns:
        str: The classification result as one of: "product recommendation", "referral", "unsure", "other".
    """

    categories = ["product recommendation", "referral", "unsure", "other"]
    messages = format_query_classification_prompt(query=query, chat_history=chat_history)

    log.debug("Classifying query; query= %s", query)
    log.debug("Classifying query; prompt= %s", messages)

    result = classifier.generate(messages=messages)
    classification = extract_json_from_response(result)

    log.debug("Classification result: %s", classification)

    try: 
        classification = classification["category"]
    except KeyError as e:
        log.error(f"Failed to classify query: {e}")
        classification = {"category": "unsure"}
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        classification = {"category": "unsure"}
    if classification not in categories:
        log.error(f"Invalid classification: {classification}. Defaulting to 'unsure'.")
        classification = "unsure"

    return classification


def answer_referral_query(
    query: str,
    chat_history: list[dict[str, str]],
    llm_model: Any = CustomOpenAIClient(enable_streaming=True),
) -> str:
    """Answer the referral query using the LLM.

    Args:
        query (str): The query to answer.
        chat_history (list[dict[str, str]]): The chat history, which is a list of dictionaries 
            containing the role and content of each message.
        llm_model (str): The model to use for the text generation.

    Returns:
        str: The answer to the query.
    """

    # format the request body
    messages=format_referral_query_prompt(query=query, chat_history=chat_history)

    # Determine if the query requires a function call
    response = llm_model.generate(
        messages=messages,
        tools=GET_REFERRAL_CODE_TOOL,
    )
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_referal_code":
                function_response = get_referal_code(
                    user_id=function_args.get("user_id"),
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
    # Generate the final response with the function call results.
    # Ideally, there should be a seperate prompt for non-function call responses.
    stream_obj = llm_model.generate(messages=messages)
    return stream_obj


def chat_agent(
    query: str,
    chat_history: list[dict[str, str]] = [],
    llm_model: Any = CustomOpenAIClient(enable_streaming=True),
) -> str:
    """Main function to handle the chat agent's behavior.

    Args:
        query (str): The user query.
        chat_history (list[dict[str, str]]): Defaults to [].
            The chat history, which is a list of dictionaries containing the role and content of each message.
        llm_model (str): The model to use for the text generation.

    Returns:
        str: The answer to the query.
    """

    # Classify the query
    classification = classify_query(query, chat_history=chat_history)
    log.debug("Query classification: %s", classification)

    # Field the query to the appropriate function based on classification
    if classification == "referral":
        return answer_referral_query(query, chat_history, llm_model)
    elif classification == "product recommendation":
        return "I would love to help out with shopping recommendations, but my creator has not given me the power, sorry!"
    elif classification == "unsure":
        return "Sorry, can you please rephrase your question? Are you asking about shopping recommendations or need assistance with referrals?"
    elif classification == "other":
        return "Sorry, I can only assist with shopping recommendations and customer referral reward quetsions at this time. For other inquiries, please contact customer service at support@cartoncaps.org about your question. If you would like to get a referral code, please let me know."