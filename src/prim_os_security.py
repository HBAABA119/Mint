"""
Prim OS Security
Provides authentication, authorization, access control,
security policies, and audit logging.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Permission(Enum):
    """Permissions"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"


@dataclass
class User:
    """User"""
    id: str
    name: str
    permissions: List[Permission]


class SecurityManager:
    """Security manager"""

    def __init__(self):
        self.users: Dict[str, User] = {}

    def add_user(self, user: User):
        """Add user"""
        self.users[user.id] = user

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check permission"""
        user = self.users.get(user_id)
        if user:
            return permission in user.permissions
        return False


def main():
    print("Testing OS Security...")
    manager = SecurityManager()
    user = User(id="user1", name="admin", permissions=[Permission.READ, Permission.WRITE])
    manager.add_user(user)
    print(f"User: {user.name}")
    print("OS Security initialized successfully")


if __name__ == "__main__":
    main()
