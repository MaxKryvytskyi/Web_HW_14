from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile, File, Request
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.user import UserDb
from src.services.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])

#
@router.get("/me", response_model=UserDb)
@limiter.limit("1/minute")
async def read_user_me(request: Request, current_user: User = Depends(auth_service.get_current_user)) -> User:
    """
    Retrieves the details of the currently authenticated user.

    Args:
        request (Request): The request object.
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        User: The details of the currently authenticated user.
    """
    return current_user

#
@router.patch('/avatar', response_model=UserDb)
@limiter.limit("1/minute")
async def update_avatar_user(request: Request, file: UploadFile = File(), 
        current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)) -> User:
    """
    Updates the avatar of the current user with the provided image file.

    Args:
        request (Request): The request object.
        file (UploadFile): The image file to be uploaded as the new avatar. Defaults to File().
        current_user (User): The current authenticated user obtained from the access token.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        User: The updated user object with the new avatar URL.
    """
    src_url = auth_service.cloud_inary(file, current_user)
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
