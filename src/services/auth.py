import cloudinary
import cloudinary.uploader
from decouple import config
from typing import Optional
from decouple import config
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.client_redis import client_redis
from src.services.logger import logger


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config('SECRET_KEY')
    ALGORITHM = config('ALGORITHM')

    def verify_password(self, plain_password, hashed_password) -> True | False:
        """
        Verifies if the provided plain password matches the hashed password.

        Args:
            plain_password (str): The plain text password to be verified.
            hashed_password (str): The hashed password against which the plain password will be compared.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes the provided password using the configured hashing algorithm.

        Args:
            password (str): The plain text password to be hashed.

        Returns:
            str: The hashed password.
        """ 
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates an access token using the provided data and optional expiration time.

        Args:
            data (dict): The data to be encoded into the access token.
            expires_delta (Optional[float]): The optional expiration time of the token in seconds. If not provided, the token will expire after 60 minutes by default.

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Creates an access token using the provided data and optional expiration time.

        Args:
            data (dict): The data to be encoded into the access token.
            expires_delta (Optional[float]): The optional expiration time of the token in seconds. If not provided, the token will expire after 60 minutes by default.

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decodes the provided refresh token to extract the email address.

        Args:
            refresh_token (str): The refresh token to be decoded.

        Returns:
            str: The email address extracted from the refresh token.

        Raises:
            HTTPException: If the provided token cannot be decoded or if it has an invalid scope.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Retrieves the current user based on the provided access token.

        Args:
            token (str): The access token used for authentication.
            db (Session): The database session.

        Returns:
            User: The current user.

        Raises:
            HTTPException: If the provided token cannot be decoded, has an invalid scope, or if the user cannot be retrieved from the database.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = client_redis.redis_get(email)
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            client_redis.redis_set(email, user)
            client_redis.redis_expire(email)
            return user
        return user


    def create_email_token(self, data: dict) -> str:
        """
        Creates an email verification token using the provided data.

        Args:
            data (dict): The data to be encoded into the token.

        Returns:
            str: The encoded email verification token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def create_email_reset_password_token(self, data: dict) -> str:
        """
        Creates a token for resetting the password using the provided data.

        Args:
            data (dict): The data to be encoded into the token.

        Returns:
            str: The encoded token for resetting the password.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=10)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Retrieves the email address from the provided token.

        Args:
            token (str): The token containing the email information.

        Returns:
            str: The email address extracted from the token.

        Raises:
            HTTPException: If the provided token cannot be decoded or if the decoding process fails.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")
        
    async def cloud_inary(file, current_user):
        cloudinary.config(
            cloud_name=config("cloudinary_name"), 
            api_key=config("cloudinary_api_key"),
            api_secret=config("cloudinary_api_secret"),
            secure=True
        )

        r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
        return cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                            .build_url(width=250, height=250, crop='fill', version=r.get('version'))

auth_service = Auth()