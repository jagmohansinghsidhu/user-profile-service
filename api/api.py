from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import func, Session, select


from .models import UserProfileBase, UserProfile, UserProfileList, UserProfilePatch, PaginationQueryParams
from .db import get_db_session
from .cache import cache_response, update_response_cache

router = APIRouter(prefix='/users', tags=['user_profiles'])


@router.post('', response_model=UserProfile, status_code=201)
def create_user_profile(
        user_profile: UserProfileBase,
        session: Session = Depends(get_db_session)
):
    email_exists_query = select(UserProfile).where(
        UserProfile.email == user_profile.email
    ).exists()
    if session.scalar(select(email_exists_query)):
        raise HTTPException(
            status_code=422,
            detail=f'User Profile with email: {user_profile.email} already exists'
        )
    new_user_profile = UserProfile(**user_profile.model_dump())
    session.add(new_user_profile)
    session.commit()
    session.refresh(new_user_profile)
    return new_user_profile


@router.patch('/{user_id}', response_model=UserProfile)
@update_response_cache(ttl=60, key_prefix="user_id", params=["user_id"])
def update_user_profile(
        user_id: int,
        user_update: UserProfilePatch,
        session: Session = Depends(get_db_session)
):

    user_profile = session.exec(select(UserProfile).where(UserProfile.id == user_id)).one()
    if not user_profile:
        raise HTTPException(status_code=404, detail="UserProfile not found")

    update_fields = user_update.model_dump(exclude_unset=True)
    user_profile.sqlmodel_update(update_fields)

    session.add(user_profile)
    session.commit()
    return user_profile


@router.get('', response_model=UserProfileList)
def get_user_profiles(
        pagination_params: Annotated[PaginationQueryParams, Query()],
        session: Session = Depends(get_db_session)
):
    users = session.exec(
        select(
            UserProfile
        ).order_by(
            getattr(UserProfile, pagination_params.sort_by)
        ).offset(
            pagination_params.offset
        ).limit(
            pagination_params.limit
        )
    )

    total_user_profiles = session.exec(select(func.count(UserProfile.id))).one()

    return UserProfileList(
        users=users,
        offset=pagination_params.offset,
        limit=pagination_params.limit,
        total=total_user_profiles
    )


@router.get('/{user_id}', response_model=UserProfile)
@cache_response(ttl=60, key_prefix="user_id", params=["user_id"])
def get_user_profile(
        user_id: int,
        session: Session = Depends(get_db_session)
):

    user_profile = session.exec(select(UserProfile).where(UserProfile.id == user_id)).one()
    if not user_profile:
        raise HTTPException(status_code=404, detail="UserProfile not found")
    return user_profile
