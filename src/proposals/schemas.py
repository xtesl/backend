

from sqlmodel import SQLModel

from .schemas import ProposalStatus, ProposalBase

class ProposalCreate(ProposalBase):
    pass

class ProposalPublic(ProposalBase):
    status: ProposalStatus
    pk: str