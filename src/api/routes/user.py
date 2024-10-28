from typing import Union, Any, Annotated

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlmodel import Session, select, func
from starlette.requests import Request

from src.models.user.schemas import  User, APIAccountType, AccountType
from src.models.generic.data import SimpleResponse, ResponseStatus
from src.core.security import verify_password, get_password_hash
from src.models.profile.data import (
    ProfilePublic,
    UpdateProfile,
    ProfilePublicEmployer,
    ProfilePublicFreelancer
)
from src.models.user.data import (
    UserCreate, 
    UsersPublic,
    UserPublic,
    UserPublicWithProfile,
    UsersPublicWithProfiles,
    UpdatePassword,
    UserUpdateMe
)
from src.api.deps import SessionDep, CurrentUser
from src.crud.user import create_user, get_user_by_email


router = APIRouter()


@router.get(
    "/me",
    response_model=Union[UserPublicWithProfile, UserPublic]
)
async def get_user(
    session: SessionDep,
    current_user: CurrentUser,
    profile: Annotated[bool, Query(
     description="Profile info is returned alongside basic user info when enabled."
    )] = False,
) -> Any:
    """
    Retrieve user's account details.Can send details with or without profile info.
    """
    if not profile:
        current_user.profile = None
    return current_user

@router.patch("/me", response_model=UserPublic)
async def update_user_basic_info(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: CurrentUser
) -> Any:
    """ 
    This endpoint is for updating basic user info i.e email, username and full_name.
    It doesn't include update for profile info.
    """
    # Checks for existing emails, if email update is needed.
    if user_in.email:
        existing_user = get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.pk != current_user.pk:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists."
            )
    
    user_data = user_in.model_dump(exclude_unset=True) # Allow for partial updates
    current_user.sqlmodel_update(user_data)
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user

# Freelancer and Employer example request bodies
freelancer_example = {
    "bio": "Freelancer specializing in software development.",
    "profile_image": "https://example.com/freelancer.jpg",
    "program": "Computer Science"
}

employer_example = {
    "bio": "Owner of a growing tech company.",
    "profile_image": "https://example.com/employer.jpg",
    "location": "Accra, Ghana",
    "name": "John Doe",
    "company_website": "https://examplecompany.com",
    "company_name": "Example Tech Ltd."
}

@router.patch(
    "/me/profile",
    response_model=Union[ProfilePublic, ProfilePublicEmployer, ProfilePublicFreelancer],
    responses={
        200: {
        "content": {
            "application/json": {
                "examples": {
                    "freelancer_example": {
                        "summary": "Freelancer Profile",
                        "description": "Example response for a freelancer user profile.",
                        "value": {
                            "bio": "Freelancer specializing in web development.",
                            "profile_image": "https://example.com/freelancer.jpg",
                            "program": "Computer Science"
                        }
                    },
                    "employer_example": {
                        "summary": "Employer Profile",
                        "description": "Example response for an employer user profile.",
                        "value": {
                            "bio": "CEO of a growing tech company.",
                            "profile_image": "https://example.com/employer.jpg",
                            "location": "Accra, Ghana",
                            "name": "John Doe",
                            "company_website": "https://examplecompany.com",
                            "company_name": "Example Tech Ltd."
                        }
                    }
                }
            }
        }
    }
    }
)
async def update_user_profile(
    *,
    session: SessionDep,
    data: Annotated[UpdateProfile, Body(
        ...,
        openapi_examples={
            "freelancer": {
                "summary": "Freelancer Profile Request",
                "description": "Request body for updating a freelancer's profile.",
                "value": freelancer_example
            },
            "employer": {
                "summary": "Employer Profile Request",
                "description": "Request body for updating an employer's profile.",
                "value": employer_example
            }
        }   
)],
    current_user: CurrentUser
) -> Any:
    # Run updates according to account types
    employer_fields = {"location", "company_website", "company_name", "name"}
    freelancer_fields = {"program"}
    
    if current_user.account_type is AccountType.EMPLOYER:
        user_data = data.model_dump(exclude_unset=True, exclude=freelancer_fields)
    else:
        user_data = data.model_dump(exclude_unset=True, exclude=employer_fields)
    
    current_user.sqlmodel_update(user_data)
    
    session.add(current_user)
    session.commit()
    
    response = (
         ProfilePublicEmployer(**user_data)
         if current_user.account_type is AccountType.EMPLOYER
         else ProfilePublicFreelancer(**user_data)
    )
    
    return response
        
        
    
@router.patch("/me/password", response_model=SimpleResponse)
async def update_password(
    *,
    session: SessionDep,
    data: UpdatePassword,
    current_user: CurrentUser
) -> Any:
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Incorrect password")
    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    
    hashed_password = get_password_hash(data.new_password)
    current_user.hashed_password = hashed_password
    
    session.add(current_user)
    session.commit()
    
    return SimpleResponse(
        status=ResponseStatus.SUCCESS,
        message="Password updated successfully"
    )
    
@router.post(
    "/{account_type}",
    response_model=UserPublic
)
async def _create_user(
    *, 
    account_type: APIAccountType,
    session: SessionDep,
    user_in: UserCreate,
    institution_nick: Annotated[str, Query(
        description="Required for freelancer accounts.University's nickname"
    )] = None
) -> Any:
    user = get_user_by_email(session=session, email=user_in.email)
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    if account_type is APIAccountType.FREELANCER and not institution_nick:
        raise HTTPException(
            status_code=400,
            detail="`institution_nick` is required for freelancer account type."
        )
        
    # Create user account with minimum profile setup
    user = create_user(
        session=session,
        user_create=user_in,
        account_type=account_type,
        institution_nick=institution_nick
    )
        
    return user

    
    

