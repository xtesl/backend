from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from datetime import datetime

from sqlmodel import Field, Relationship, String

from src.models import Base
from src.jobs.models import Job, PaymentType

if TYPE_CHECKING:
    from src.users.models import User
    
class ProposalStatus(str, Enum):
    SENT = "sent"
    WITHDRAWN = "withdrawn"
    NEGOTIATION = "negotiation"
    REJECTED = "rejected" 
    ACCEPTED = "accepted"
    JOB_STARTED = "job_started"
    JOB_FINISHED_SUCCESS = "job_finished_success"
    JOB_FINISHED_UNSUCCESS = "job_finished_unsuccess"
    JOB_DISPUTED = "job_disputed"
    

class MessageSenders(str, Enum):
    FREELANCER = "freelancers"
    EMPLOYERS = "employers"
    
class Message(Base, table=True):
    __tablename__ = "messages"
    __tableprefix__ = "mssg"
    
    freelancer_pk: str | None = Field(foreign_key="freelancers.pk", default=None)
    employer_pk: str | None = Field(foreign_key="employers.pk", default=None)
    proposal_pk: str = Field(foreign_key="proposals.pk")
    proposal_status_catalog_pk: str | None = Field(foreign_key="proposal_status_catalogs.pk")
    message_text: str = Field(sa_type=String())
    sender: MessageSenders
    
    attachments: list["Attachment"] = Relationship(back_populates="message", cascade_delete=True)


class Attachment(Base, table=True):
    __tablename__ = "attachments"
    __tableprefix__ = "attmnt"
    
    message_pk: str = Field(foreign_key="messages.pk")
    attachment_link: str = Field(sa_type=String())
    
    message: Message = Relationship(back_populates="attachments")

class ProposalStatusCatalog(Base, table=True): 
    __tablename__ = "proposal_status_catalogs"
    __tableprefix__ = "prstcat"
    
    status: ProposalStatus

class Proposal(Base, table=True):
    __tablename__ = "proposals"
    __tableprefix__ = "prps"
    
    job_pk: str = Field(foreign_key="jobs.pk")
    freelancer_pk: str = Field(foreign_key="freelancers.pk")
    payment_type: PaymentType
    payment_amount: Decimal = Field(max_digits=8, decimal_places=2)
    current_proposal_status_pk: str = Field(foreign_key="proposal_status_catalogs.pk")
    employer_comment: str | None = Field(sa_type=String(), default=None)
    employer_grade: int | None = None
    freelancer_grade: int | None = None
    freelancer_comment: str | None = Field(sa_type=String(), default=None)
    
    contract: "Contract" = Relationship(
        back_populates="proposal",
        cascade_delete=True,
        sa_relationship_kwargs={"uselist": False}
    )
    job: Job = Relationship(back_populates="proposals")

class Contract(Base, table=True):
    __tablename__ = "contracts"
    __tableprefix__  = "cntr"
    
    proposal_pk: str = Field(foreign_key="proposals.pk")
    employer_pk: str = Field(foreign_key="employers.pk")
    freelancer_pk: str = Field(foreign_key="freelancers.pk")
    end_time: datetime | None = None
    payment_type: PaymentType
    payment_amount: Decimal = Field(max_digits=8, decimal_places=2)
    
    proposal: Proposal = Relationship(back_populates="contract")
    
    
    
    
    
    
    
    