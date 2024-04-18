from fastapi import Depends
from sqlalchemy import select, and_ 
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserSchema


# test is ready
async def create_user(body: UserSchema, db: Session=Depends(get_db)) -> User:
    """
    Creates a new user.

    Args:
        body (UserSchema): The data representing the new user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        User: The newly created user object.
    """
    new_user = User(**body.model_dump())
    new_user.avatar = "https://www.rpnation.com/gallery/250-x-250-placeholder.30091/full?d=1504582354"
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# test is ready
async def confirmed_email(email: str, db: Session) -> User:
    """
    Confirms the email address of a user.

    Args:
        email (str): The email address to confirm.
        db (Session): The database session.

    Returns:
        User: The user object with the confirmed email address.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
    return user


# test is ready
async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Updates the avatar URL of a user.

    Args:
        email (str): The email address of the user.
        url (str): The new avatar URL.
        db (Session): The database session.

    Returns:
        User: The user object with the updated avatar URL.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


# test is ready
async def update_token(user: User, token: str | None, db: Session) -> User:
    """
    Updates the refresh token of a user.

    Args:
        user (User): The user object.
        token (str, optional): The new refresh token, or None if the token should be removed.
        db (Session): The database session.

    Returns:
        User: The user object with the updated refresh token.
    """
    user.refresh_token = token
    db.commit()
    return user


# test is ready
async def get_user_by_email(email: str, db: Session=Depends(get_db)) -> User:
    """
    Retrieves a user by their email address.

    Args:
        email (str): The email address of the user.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user object if found, else None.
    """
    stmt = select(User).filter_by(email=email)
    user = db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


# test is ready
async def get_user_by_username(username: str, db: Session=Depends(get_db)) -> User:
    """
    Retrieves a user by their username.

    Args:
        username (str): The username of the user.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        User: The user object if found, else None.
    """
    stmt = select(User).filter_by(username=username)
    user = db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


# test is ready
async def remove_user(email: str, db: Session) -> User:
    """
    Removes a user based on their email address.

    Args:
        email (str): The email address of the user to remove.
        db (Session): The database session.

    Returns:
        User: The removed user object if found, else None.
    """
    user = await get_user_by_email(email, db)
    db.delete(user)
    db.commit()
    return user








