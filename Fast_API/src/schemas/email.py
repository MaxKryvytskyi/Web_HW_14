from pydantic import BaseModel, EmailStr


class RequestEmail(BaseModel):
    email: EmailStr
    

class RequestUserNewPassword(BaseModel):
    new_password: str