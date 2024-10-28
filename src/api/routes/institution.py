from typing import Any

from fastapi import APIRouter
from sqlmodel import select, func

from src.api.deps import SessionDep
from src.models.institution.schemas import Institution
from src.models.institution.data import InstitutionsPublic
from src.models.generic.data import PaginationResponse
from src.api.deps import OffsetPaginationParams
from src.utils.helpers import offset_pagination_metadata



router = APIRouter()


@router.post("/")
async def create_institution(
    *,
    session: SessionDep,
    data: Institution,
) -> Any:
    institution = Institution.model_validate(data)
    
    session.add(institution)
    session.commit()
    
    session.refresh(institution)
    
    return institution


@router.get("/", response_model=PaginationResponse)
async def get_institutions(
    *,
    session: SessionDep,
    pagination: OffsetPaginationParams
) -> Any:
    """
    Retrieve institutions that we support.
    """
    count_statement = select(func.count()).select_from(Institution)
    count = session.exec(count_statement).one()
    
    offset = pagination.offset
    limit = pagination.limit
    
    statement = select(Institution).offset(offset).limit(limit)
    institutions = session.exec(statement).all()
    
    pagination_data = offset_pagination_metadata(offset, limit, count, "/institution")
    
    return PaginationResponse(data=institutions, pagination=pagination_data)

    