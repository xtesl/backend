from sqlmodel import Relationship, SQLModel, String

from decimal import Decimal
from sqlmodel import Field
from enum import Enum
from datetime import datetime

from src.models import Base
from src.jobs.models import Job
from src.users.models import User


class PaymentStatus(str, Enum):
    PENDING = "pending" # Amount in escrow
    RELEASED = "released" # Amount settled to freelancer
    CANCELLED = "cancelled" # Refunded to employer

class PaymentBase(SQLModel):
    transaction_id: str #  For payment integration use
    payment_method: str
    amount: Decimal = Field(max_digits=5, decimal_places=2)

class Payment(Base, PaymentBase, table=True):
    __tablename__ = "payments"
    __tableprefix__ = "pym"
    
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    job_pk: str = Field(foreign_key="jobs.pk")
    job: Job = Relationship(back_populates="payment")
    freelancer_pk: str = Field(foreign_key="users.pk")
    freelancer: User = Relationship()
    employer_pk: str = Field(foreign_key="users.pk")
    employer: User = Relationship()


class FinancialDetails(Base, table=True):
    __tablename__ = "financial_details"
    __tableprefix__ = "fdts"
    
    balance: Decimal = Field(default=0.0, max_digits=5, decimal_places=2)
    # Freelancer field
    total_earnings: Decimal = Field(default=0.0, max_digits=5, decimal_places=2)
    user_pk: str = Field(foreign_key="users.pk")
    
    user: User = Relationship()

class SubscriptionPlanType(str, Enum):
    FREEMIUM = "freemium"
    PREMIUM = "premium"

class SubscriptionPlan(Base, table=True):
    __tablename__ = "subscription_plans"
    __tableprefix__ = "sbpl"
    
    type: SubscriptionPlanType = Field(index=True)
    name: str | None = None 
    description: str = Field(sa_type=String())
    price: float | None = None
    duration_in_days: int | None = None


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"



class Subscription(Base, table=True):
    __tablename__ = "subscriptions"
    __tableprefix__ = "subs"
    
    user_pk: str = Field(foreign_key="users.pk")
    plan_pk: str = Field(foreign_key="subscription_plans.pk")
    start_date: datetime
    end_date: datetime
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    plan_type: SubscriptionPlanType
    
    plan: SubscriptionPlan = Relationship()
    user: User = Relationship(back_populates="subscription")
    