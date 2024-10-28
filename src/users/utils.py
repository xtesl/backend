

from .models import User, Profile
from src.config import settings

"""
Databse related functions
"""
def create_user(validated_user: User, profile: Profile) -> User:
    """
    Creates user with the minimum profile setup
    """
    