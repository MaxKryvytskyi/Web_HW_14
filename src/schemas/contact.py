from datetime import date
from pydantic import BaseModel, Field, EmailStr


class ContactSchema(BaseModel):
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=40)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date 
    data: str = Field(max_length=250)


class ContactUpdate(ContactSchema):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date 
    data: str


class ContactDataUpdate(BaseModel):
    data: str


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date 
    data: str
    user_id: int

    class Config:
        from_attributes = True
        # orm_mode = True
