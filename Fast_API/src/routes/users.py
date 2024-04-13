import cloudinary
import cloudinary.uploader
from decouple import config
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile, File, Request

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.user import UserDb
from src.services.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
@limiter.limit("1/minute")
async def read_users_me(request: Request, current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserDb)
@limiter.limit("1/minute")
async def update_avatar_user(request: Request, file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=config("cloudinary_name"), 
        api_key=config("cloudinary_api_key"),
        api_secret=config("cloudinary_api_secret"),
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
