# src/utils/auth.py

# Simple token-based authentication for demonstration
# In a production environment, replace with OAuth2/OpenID Connect or a secure system.

USER_DATABASE = {
    "alice-token": {"role": "admin"},
    "bob-token": {"role": "metadata-verifier"},
    "carol-token": {"role": "metadata-embedder"}
}

def authenticate_user(token: str) -> dict:
    # Returns a dict with "role" based on the token provided.
    # If token not found, defaults to "guest".
    return USER_DATABASE.get(token, {"role": "guest"})
