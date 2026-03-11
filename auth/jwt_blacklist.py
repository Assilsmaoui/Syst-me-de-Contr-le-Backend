# Simple in-memory blacklist for JWT tokens
# In production, use a persistent store (e.g., Redis, MongoDB)
blacklisted_tokens = set()

def add_token_to_blacklist(token: str):
    blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens
