from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.email import RequestEmail, RequestUserNewPassword
from src.schemas.user import UserSchema, TokenModel, UserResponse
from src.services.auth import auth_service
from src.services.limiter import limiter
from src.services.email import send_email, send_resets_password
from src.database.models import User
from src.services.logger import logger

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()

#
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def signup(request: Request, background_tasks: BackgroundTasks, body: UserSchema, db: Session = Depends(get_db)) -> User | HTTPException:
    """
    Registers a new user.

    Args:
        request (Request): The request object.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        body (UserSchema): The request body containing user data.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        User, HTTPException: The newly created user object if the signup is successful,
        or an HTTPException with a status code and detail message if there's a conflict with existing user data.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email exists")
    exist_user = await repository_users.get_user_by_username(body.username, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this username exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return new_user

#
@router.post("/login",  response_model=TokenModel, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def login(request: Request, body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict | HTTPException: 
    """
    Logins in a user.

    Args:
        request (Request): The request object.
        body (OAuth2PasswordRequestForm): The request body containing the username (email) and password.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        Dict, HTTPException: A dictionary with the access token, refresh token, and token type if the login is successful,
        or an HTTPException with a status code and detail message if there's an issue with the login credentials.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        user = await repository_users.get_user_by_username(body.username, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

#
@router.get('/refresh_token',  response_model=TokenModel)
@limiter.limit("10/minute")
async def refresh_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: Session = Depends(get_db)): # -> dict | HTTPException
    """
    Refreshes the access token using the refresh token.

    Args:
        request (Request): The request object.
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the refresh token.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        Dict, HTTPException: A dictionary with the new access token, refresh token, and token type if the refresh is successful,
        or an HTTPException with a status code and detail message if there's an issue with the refresh token.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

#
@router.post('/reset_password')
@limiter.limit("10/minute")
async def reset_password(request: Request, body: RequestEmail, background_tasks: BackgroundTasks, db: Session = Depends(get_db)): #  -> dict | HTTPException
    """
    Initiates the password reset process.

    Args:
        request (Request): The request object.
        body (RequestEmail): The request body containing the email address for password reset.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        Dict, HTTPException: A dictionary with a success message if the reset process is initiated successfully,
        or an HTTPException with a status code and detail message if the email address is not found.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email address not found")
    if user:
        background_tasks.add_task(send_resets_password, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post('/reset_password/{token}')
@limiter.limit("10/minute")
async def reset_password_token(body: RequestUserNewPassword, request: Request, token: str, db: Session = Depends(get_db)): #  -> dict | HTTPException
    logger.critical(body)
    logger.critical(token)
    """
    Resets the user's password using the reset token.

    Args:
        body (RequestUserNewPassword): The request body containing the new password.
        request (Request): The request object.
        token (str): The reset token.
        db (Sessionl): The database session. Defaults to Depends(get_db).

    Returns:
        Dict, HTTPException]: A dictionary with a success message if the password reset is successful,
        or an HTTPException with a status code and detail message if there's a reset password error.
    """
    email = await auth_service.get_email_from_token(token)
    logger.critical(email)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset password error")
    if user:
        user.password = auth_service.get_password_hash(body.new_password)
        db.commit()
        return {"message": "Password has been changed"}


@router.get('/confirmed_email/{token}')
@limiter.limit("1/minute")
async def confirmed_email(request: Request, token: str, db: Session = Depends(get_db)): #  -> dict | HTTPException
    """
    Confirms the user's email using the verification token.

    Args:
        request (Request): The request object.
        token (str): The verification token.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        Dict, HTTPException: A dictionary with a confirmation message if successful,
        or an HTTPException with a status code and detail message if there's a verification error.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
@limiter.limit("1/minute")
async def request_email(request: Request, body: RequestEmail, background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db)): #  -> dict
    """
    Endpoint to request email confirmation.

    This endpoint allows users to request email confirmation. If the email is already confirmed,
    it returns a message indicating that. If the email is not confirmed, it sends a confirmation email.
    
    Args:
        request (Request): The request object.
        body (RequestEmail): The request body containing the email.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        db (Session): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A message indicating the outcome of the request.
    """

    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}

