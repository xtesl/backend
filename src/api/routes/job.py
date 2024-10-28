from typing import Any, Annotated

from fastapi import APIRouter, Query

from src.api.deps import (
     SessionDep, 
     CurrentUser, 
     CurrentEmployerUser, 
     OffsetPaginationParams,
     CurrentFreelancerUser
)
from src.models.job.data import JobCreate, JobPublic, JobsPublic, JobUpdate
from src.models.job.schemas import Job
from src.models.user.schemas import AccountType
from src.crud.job import create_job, update_job, delete_job, get_job_by_pk
from src.models.generic.data import SimpleResponse, ResponseStatus, PaginationResponse
from src.utils.helpers import offset_pagination_metadata
from src.models.proposal.schemas import Proposal, ProposalStatus
from src.models.proposal.data import ProposalCreate, ProposalPublic

router = APIRouter()


@router.post("/", response_model=JobPublic)
async def _create_job(
    current_user: CurrentEmployerUser, 
    session: SessionDep, 
    job_in: JobCreate
) -> Any:
    """
    Job creation can be done by only employers.
    """
    job = create_job(
            job_create=job_in,
            session=session,
            employer_pk=current_user.pk
    )
    
    return job


@router.post("/proposal/{job_pk}", response_model=ProposalPublic)
async def submit_proposal(
        session: SessionDep,
        current_user: CurrentFreelancerUser,
        job_pk: str,
        data: ProposalCreate
) -> Any:
    """
    Submit a proposal on a particular job.
    """
    job = get_job_by_pk(session=session, job_pk=job_pk)
    
    proposal = Proposal.model_validate(
        data,
        update={
            "job_pk": job_pk,
            "freelancer_pk": current_user.pk,
            "status": ProposalStatus.SUBMITTED
        }
    )
    
    session.add(proposal)
    session.commit()
    session.refresh(proposal)
    
    return proposal
    
  

@router.get("/me", response_model=PaginationResponse)
async def get_jobs_me(
    session: SessionDep, 
    current_user: CurrentEmployerUser,
    pagination: OffsetPaginationParams
) -> Any:
    """
    Retrieve employer posted jobs with offset-based pagination.
    In most cases, you will only need to set the `offset` and `limit` query paramters
    once and that's it. You can retrive data on subsequent requests using
    prev and next links in pagination data of the API response.
    """
    limit = pagination.limit
    offset = pagination.offset
    
    jobs_posted = current_user.jobs_posted
    jobs_count = len(jobs_posted)
    data = jobs_posted[offset: offset + limit]
    
    # Generate pagination data
    pagination = offset_pagination_metadata(offset, limit, jobs_count, "/job/me")
    
    return PaginationResponse(data=jobs_posted, pagination=pagination)
    


@router.patch("/me/{job_pk}", response_model=JobPublic)
async def _update_job(
    session: SessionDep, 
    job: JobUpdate,
    current_user: CurrentEmployerUser, 
    job_pk: str
) -> Any:
    job = update_job(
        session=session,
        current_user=current_user,
        job=job, 
        job_pk=job_pk
    )
    
    return job

@router.delete("/me/{job_pk}", response_model=SimpleResponse)
async def _delete_job(session: SessionDep, job_pk: str, current_user: CurrentEmployerUser) -> Any:
    """
    To delete job, its status must not be `in_progress` and `disputed`.
    """
    if delete_job(session, job_pk, current_user):
        return SimpleResponse(status=ResponseStatus.SUCCESS, message="Job deleted successfully")
    return SimpleResponse(status=ResponseStatus.FAILED, message="Failed to delete job")


    
