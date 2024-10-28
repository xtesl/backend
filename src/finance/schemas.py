

from sqlmodel import SQLModel

from .models import SubscriptionPlanType
import constants


class SubscriptionPlanDetailsBase(SQLModel):
    """Subscription plan package description and features"""
    type: SubscriptionPlanType
    description: str
    verifieable: bool

class SubscriptionPlanDetailsFreelancer(SubscriptionPlanDetailsBase):
    can_bid_jobs_per_month: int 
    concurrent_jobs: int 

class SubscriptionPlanDetailsEmployer(SubscriptionPlanDetailsBase):
    can_create_jobs: int 
    bids_per_job: int 


# Freemium plan for a freelancer user
freemium_plan_freelancer = SubscriptionPlanDetailsFreelancer(
    verifieable=False,
    type=SubscriptionPlanType.FREEMIUM,
    description="Freemium plan offers you 200 job bids per month and 4 concurrent jobs at a time.",
    can_bid_jobs_per_month=constants.CAN_BID_JOBS_PER_MONTH,
    concurrent_jobs=constants.CONCURRENT_JOBS
)

# Freemium plan for employer user
freemium_plan_employer = SubscriptionPlanDetailsEmployer(
    verifieable=False,
    type=SubscriptionPlanType.FREEMIUM,
    description="Freemium plan offers you 50 job space and 10 bids per a job.",
    can_create_jobs=constants.CAN_CREATE_JOBS,
    bids_per_job=constants.BIDS_PER_JOB 
)
    