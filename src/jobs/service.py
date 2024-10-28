
from sqlmodel import Session
from fastapi import HTTPException

from src.users.models import User
from src.core.permissions import Permission, VER_TYPE
from .schemas import JobCreate
from .models import Job
from src.utils.db import save, get_object_with_pk_or_404
from src.finance.schemas import freemium_plan_employer
from src.finance.models import SubscriptionPlanType

subscriptions_features_employer = {
    SubscriptionPlanType.FREEMIUM: freemium_plan_employer
}


class JobService:
    def __init__(self, session: Session, current_user: User | None):
        self.session = session
        self.current_user = current_user
        
    def _get_permission(self) -> Permission:
        return Permission(self.current_user)
    
    async def create_job(self, data: JobCreate) -> Job:
        """
        Only employers with verified email can create jobs.
        """
        self._get_permission().check_verification(type=VER_TYPE.EMAIL)
        
        """
        Checking of user's subscription plan and job limits.
        No subscription associated with a user means user has freemium subscription plan.
        """
        subscription_plan = self.current_user.subscription
        # Set plan to freemium if user has none.
        if subscription_plan is None:
            subscription_plan = SubscriptionPlanType.FREEMIUM
        else:
            subscription_plan = SubscriptionPlanType.PREMIUM
            
        plan_features = subscriptions_features_employer[subscription_plan]
        
        number_of_posted_jobs = len(self.current_user.jobs_posted)
        if number_of_posted_jobs >= plan_features.can_create_jobs:
            raise HTTPException()
        
        job = Job.model_validate(data,  update={"employer_pk": self.current_user.pk})
        refreshed_job = save(self.session, job, True)
        return refreshed_job
    
    def get_job(self, job_pk: str) -> Job:
        """Retrieve a job"""
        return get_object_with_pk_or_404(job_pk, self.session, Job)
        
        