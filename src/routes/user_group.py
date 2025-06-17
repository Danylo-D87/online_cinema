from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.setup import get_db
from src.schemas.user.user_group import UserGroupCreate, UserGroupUpdate, UserGroupResponse
from src.services.user.user_group import UserGroupService
# from src.dependencies.auth import get_current_user, role_required # Для контролю доступу


router = APIRouter(
    prefix="/user_groups",
    tags=["User Groups"]
)

@router.post(
    "/",
    response_model=UserGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user group",
    description="Allows creating a new user group (e.g., 'guest', 'premium'). Requires admin privileges."
    # dependencies=[Depends(role_required(["admin"]))], # Розкоментуйте для захисту роуту
)
async def create_user_group_endpoint(
    group_data: UserGroupCreate,
    db: AsyncSession = Depends(get_db)
):
    user_group_service = UserGroupService(db)
    return await user_group_service.create_user_group(group_data)


@router.get(
    "/",
    response_model=List[UserGroupResponse],
    summary="Get all user groups",
    description="Retrieves a list of all defined user groups."
)
async def get_all_user_groups_endpoint(
    db: AsyncSession = Depends(get_db)
):
    user_group_service = UserGroupService(db)
    return await user_group_service.get_all_user_groups()


@router.get(
    "/{group_id}",
    response_model=UserGroupResponse,
    summary="Get user group by ID",
    description="Retrieves a single user group by its unique ID."
)
async def get_user_group_by_id_endpoint(
    group_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_group_service = UserGroupService(db)
    return await user_group_service.get_user_group_by_id(group_id)

@router.put(
    "/{group_id}",
    response_model=UserGroupResponse,
    summary="Update a user group",
    description="Updates an existing user group's name. Requires admin privileges."
    # dependencies=[Depends(role_required(["admin"]))], # Розкоментуйте для захисту роуту
)
async def update_user_group_endpoint(
    group_id: int,
    group_data: UserGroupUpdate,
    db: AsyncSession = Depends(get_db)
):
    user_group_service = UserGroupService(db)
    return await user_group_service.update_user_group(group_id, group_data)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user group",
    description="Deletes a user group by its ID. Requires admin privileges. Caution: ensure no users are assigned to this group before deletion."
    # dependencies=[Depends(role_required(["admin"]))], # Розкоментуйте для захисту роуту
)
async def delete_user_group_endpoint(
    group_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_group_service = UserGroupService(db)
    await user_group_service.delete_user_group(group_id)
    return {}
