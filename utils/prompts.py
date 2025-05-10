"""This module contains all prompt templates and prompt formatting tools."""

# Define the system and user prompts for query classification
QUERY_CLASSIFICATION_SYS_PROMPT = """\
You are a query classification assistant for a shopping and referral app. Your task is to classify the indicated user query in context of the given chat history into one of the following categories:

1. "product recommendation" - if the user is asking for product suggestions, preferences, or shopping help.
2. "referral" - if the query is about referring friends, how referrals work, referral rewards, or sharing referral links.
3. "unsure" - if the query is unclear, ambiguous, or you cannot confidently determine the category.
4. "other" - if the query is valid but unrelated to products or referrals (e.g., technical issues, app features, general questions).

Respond **only** with a valid JSON object in the following format:

```json
{
  "category": <category>
}
```"""
QUERY_CLASSIFICATION_USER_PROMPT = """\
**Chat history:**
{chat_history}

**Classify the following user query:**
"{query}"

Return the result in JSON only."""


# Load the referral information from a markdown file
# Since the data volume is small, it makes more sense to process and format it manually to ensure data quality
REFFERAL_INFO_PATH = "data/referral_info.md"
with open(REFFERAL_INFO_PATH, 'r', encoding='utf-8') as file:
    REFERRAL_INFO = file.read()
# Define and format prompts for referral queries
REFFERAL_SYS_PROMPT = f"""\
You are a referral assistant for a shopping and referral app called Carton Caps that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls.

Your task is to provide information about the referral program based on the user's query.

If you need to provide a referral link, use the following format: https://cartoncaps.org/referral/<referral_code>
If you need to get the referral_code, you can access external functions to retrieve it, given the user ID.
If don't know the user ID, ask the user to provide it.

Only respond using the referral information below. If the user asks a question that is not covered in the referral information, respond with \
"Sorry, I'm not sure how to answer your question about referrals. Please contact customer service at support@cartoncaps.org about your question. If you would like to get a referral code, please let me know."

The referral information is as follows:
{REFERRAL_INFO}
"""

def chat_history_to_string(messages: list[dict[str,str]], n_messages: int=10) -> str:
    """
    Formats the last `n_messages` messages as a string where each message is on a new line,
    prefixed by the role.

    For example:
            messages = [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
                {"role": "user", "content": "What is the referral program?"}
            ]

            Would return: (str)
            user: Hello!
            assistant: Hi! How can I help you?
            user: What is the referral program?

    Args:
        messages (list): List of dictionaries with keys 'role' and 'content'. Defaults to the last 10 messages.

    Returns:
        str: Formatted string of the last n messages
    """
    last_n_messages = messages[-n_messages:]
    formatted = "\n".join(f"{msg['role']}: {msg['content']}" for msg in last_n_messages)
    return formatted


def format_query_classification_prompt(query: str, chat_history: list[dict[str,str]]) -> list[dict[str, str]]:
    """Format the query classification prompt with the user query."""
    formatted_chat_history = chat_history_to_string(chat_history)
    return [
        {"role": "system", "content": QUERY_CLASSIFICATION_SYS_PROMPT},
        {"role": "user", "content": QUERY_CLASSIFICATION_USER_PROMPT.format(query=query, chat_history=formatted_chat_history)},
    ]


def format_referral_query_prompt(query: str, chat_history: list[dict[str,str]]) -> list[dict[str, str]]:
    """Format the referral query prompt with the user query."""
    return [{"role": "system", "content": REFFERAL_SYS_PROMPT}] + chat_history + [{"role": "user", "content": query}]