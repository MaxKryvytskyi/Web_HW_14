from datetime import date
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.contact import ContactSchema, ContactResponse, ContactDataUpdate, ContactUpdate
from src.database.models import User 
from src.repository import contact as repository_contact 
from src.services.auth import auth_service
from src.services.limiter import limiter

router = APIRouter(prefix='/contacts', tags=['contacts'])



@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_contact(request: Request, body: ContactSchema, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    return await repository_contact.create_contact(user_id, body, db)


@router.get("/search", response_model=list[ContactResponse])
@limiter.limit("10/minute")
async def search_contacts(request: Request,
    first_name: str = Query(None, description="Search contacts by first name"),
    last_name: str = Query(None, description="Search contacts by last name"),
    email: str = Query(None, description="Search contacts by email"),
    phone: str = Query(None, description="Search contacts by phone"), 
    birthday: date = Query(None, description="Search contacts by birthday"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contacts = await repository_contact.search_contacts(user_id, first_name, last_name, email, phone, birthday, db)
 
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birstday not found")
    return contacts


@router.get("/birstdays/all", response_model=list[ContactResponse])
@limiter.limit("10/minute")
async def get_birstdays(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contacts = await repository_contact.get_birstdays(user_id, skip, limit, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birstday not found")
    return contacts


@router.get("/", response_model=list[ContactResponse])
@limiter.limit("10/minute")
async def read_contacts(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contacts = await repository_contact.get_contacts(user_id, skip, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def read_contact(request: Request, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contact = await repository_contact.get_contact(user_id, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def remove_contact(request: Request, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contact = await repository_contact.remove_contact(user_id, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def update_contact(request: Request, contact_id: int, body: ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contact = await repository_contact.update_contact(user_id, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def update_data_contact(request: Request, contact_id: int, body: ContactDataUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    user_id = current_user.id
    contact = await repository_contact.update_data_contact(user_id, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact






