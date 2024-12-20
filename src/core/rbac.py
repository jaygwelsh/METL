# src/core/rbac.py

ROLES_PERMISSIONS = {
    "admin": ["embed", "verify"],
    "metadata-embedder": ["embed"],
    "metadata-verifier": ["verify"]
}

def check_permission(role: str, action: str) -> bool:
    allowed_actions = ROLES_PERMISSIONS.get(role, [])
    return action in allowed_actions
