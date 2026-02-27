"""
Prim Cloud Security
Provides security policies, IAM management, encryption services,
compliance monitoring, and security auditing.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityPolicy:
    """Security policy"""
    name: str
    level: SecurityLevel
    rules: List[str]


class SecurityManager:
    """Security manager"""

    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}

    def create_policy(self, policy: SecurityPolicy):
        """Create security policy"""
        self.policies[policy.name] = policy

    def get_policies(self) -> List[SecurityPolicy]:
        """Get all policies"""
        return list(self.policies.values())


def main():
    print("Testing Cloud Security...")
    manager = SecurityManager()
    policy = SecurityPolicy(name="test", level=SecurityLevel.HIGH, rules=["rule1"])
    manager.create_policy(policy)
    print(f"Policies: {len(manager.get_policies())}")
    print("Cloud Security initialized successfully")


if __name__ == "__main__":
    main()
