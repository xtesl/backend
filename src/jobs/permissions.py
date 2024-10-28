

from src.core.permissions import Permission

class JobPermissions(Permission):
    
    def can_create_job(self) -> bool:
        """
        Check whether an employer can create you job or not.
        """
        current_user = self.current_user
        