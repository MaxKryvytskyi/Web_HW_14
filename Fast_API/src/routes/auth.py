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


router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


# регистрация 
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def signup(request: Request, background_tasks: BackgroundTasks, body: UserSchema, db: Session = Depends(get_db)):
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


# авторизация
@router.post("/login",  response_model=TokenModel, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def login(request: Request, body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        user = await repository_users.get_user_by_username(body.username, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
 
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# генерация мастер токена
@router.get('/refresh_token',  response_model=TokenModel)
@limiter.limit("10/minute")
async def refresh_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: Session = Depends(get_db)):
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



# Запрос на скидання паролю User треба Email
@router.post('/reset_password')
@limiter.limit("10/minute")
async def reset_password(request: Request, body: RequestEmail, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email address not found")
    if user:
        background_tasks.add_task(send_resets_password, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
 


# Скидання паролю, якщо токен живий, приймає new_password
@router.post('/reset_password/{token}')
@limiter.limit("10/minute")
async def reset_password_token(body: RequestUserNewPassword, request: Request, token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset password error")
    if user:
        user.password = auth_service.get_password_hash(body.new_password)
        db.commit()
        return {"message": "Password has been changed"}


# Подтверждение Email
@router.get('/confirmed_email/{token}')
@limiter.limit("1/minute")
async def confirmed_email(request: Request, token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


# Запрос на подтверждение Email
@router.post('/request_email')
@limiter.limit("1/minute")
async def request_email(request: Request, body: RequestEmail, background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}

