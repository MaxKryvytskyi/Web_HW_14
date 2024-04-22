from datetime import date
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.contact import ContactSchema, ContactResponse, ContactDataUpdate, ContactUpdate
from src.database.models import User 
from src.repository import contact as repository_contact 
from src.services.auth import auth_service
from src.services.limiter import limiter
from src.database.models import Contact


router = APIRouter(prefix='/contacts', tags=['contacts'])

#
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_contact(request: Request, body: ContactSchema, db: Session = Depends(get_db), 
        current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Creates a new contact for the current user.

    Args:
        request (Request): The request object.
        body (ContactSchema): The request body containing contact data.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        Contact: The newly created contact object.
    """
    user_id = current_user.id
    return await repository_contact.create_contact(user_id, body, db)

#
@router.get("/search", response_model=list[ContactResponse])
@limiter.limit("10/minute")
async def search_contacts(request: Request,
        first_name: str = Query(None, description="Search contacts by first name"),
        last_name: str = Query(None, description="Search contacts by last name"),
        email: str = Query(None, description="Search contacts by email"),
        phone: str = Query(None, description="Search contacts by phone"), 
        birthday: date = Query(None, description="Search contacts by birthday"),
        db: Session = Depends(get_db), 
        current_user: User = Depends(auth_service.get_current_user)) -> Contact | HTTPException:
    """
    Searches contacts based on provided criteria for the current user.

    Args:
        request (Request): The request object.
        first_name (str): Search contacts by first name. Defaults to None.
        last_name (str): Search contacts by last name. Defaults to None.
        email (str): Search contacts by email. Defaults to None.
        phone (str): Search contacts by phone. Defaults to None.
        birthday (date): Search contacts by birthday. Defaults to None.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        Contact, HTTPException: The contacts matching the search criteria if found,
        or an HTTPException with a status code and detail message if no contacts are found.
    """
    user_id = current_user.id
    contacts = await repository_contact.search_contacts(user_id, first_name, last_name, email, phone, birthday, db)
    if contacts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birstday not found")
    return contacts

#
@router.get("/birstdays", response_model=list[ContactResponse])
@limiter.limit("10/minute")
async def get_birstdays(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
        current_user: User = Depends(auth_service.get_current_user)) -> Contact | HTTPException:
    """
    Retrieves upcoming birthdays for the current user.

    Args:
        request (Request): The request object.
        skip (int): Number of records to skip. Defaults to 0.
        limit (int): Maximum number of records to return. Defaults to 100.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        List[Contact], HTTPException: A list of contacts with upcoming birthdays if found,
        or an HTTPException with a status code and detail message if no birthdays are found.
    """
    user_id = current_user.id
    contacts = await repository_contact.get_birstdays(user_id, skip, limit, db)
    if contacts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Birstday not found")
    return contacts

#
@router.get("/", response_model=list[ContactResponse])
@limiter.limit("10/minute")
async def get_contacts(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), 
        current_user: User = Depends(auth_service.get_current_user)) -> list[Contact] | list:
    """
    Retrieves contacts for the current user.

    Args:
        request (Request): The request object.
        skip (int): Number of records to skip. Defaults to 0.
        limit (int): Maximum number of records to return. Defaults to 100.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        List[Contact], List: A list of contacts if found, or an empty list if no contacts are found.
    """
    user_id = current_user.id
    contacts = await repository_contact.get_contacts(user_id, skip, limit, db)
    if contacts == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contacts

#
@router.get("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def get_contact(request: Request, contact_id: int, db: Session = Depends(get_db), 
        current_user: User = Depends(auth_service.get_current_user)) -> Contact | HTTPException:
    """
    Retrieves a specific contact for the current user by ID.

    Args:
        request (Request): The request object.
        contact_id (int): The ID of the contact to retrieve.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        Contact, HTTPException: The contact object if found, or an HTTPException with a status code and detail message if the contact is not found.
    """
    user_id = current_user.id
    contact = await repository_contact.get_contact(user_id, contact_id, db)
    if contact == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

#
@router.delete("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def remove_contact(request: Request, contact_id: int, db: Session = Depends(get_db), 
        current_user: User = Depends(auth_service.get_current_user)) -> Contact | HTTPException:
    """
    Removes a specific contact for the current user by ID.

    Args:
        request (Request): The request object.
        contact_id (int): The ID of the contact to remove.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        Contact, HTTPException: The removed contact object if found, or an HTTPException with a status code and detail message if the contact is not found.
    """
    user_id = current_user.id
    contact = await repository_contact.remove_contact(user_id, contact_id, db)
    if contact == [] or contact == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

#
@router.put("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def update_contact(request: Request, contact_id: int, body: ContactUpdate, 
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)) -> Contact | HTTPException:
    
    """
    Updates a specific contact for the current user by ID.

    Args:
        request (Request): The request object.
        contact_id (int): The ID of the contact to update.
        body (ContactUpdate): The request body containing the updated contact data.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        Contact, HTTPException: The updated contact object if found, or an HTTPException with a status code and detail message if the contact is not found.
    """
    user_id = current_user.id
    contact = await repository_contact.update_contact(user_id, contact_id, body, db)
    if contact == [] or contact == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

#
@router.patch("/{contact_id}", response_model=ContactResponse)
@limiter.limit("10/minute")
async def update_data_contact(request: Request, contact_id: int, body: ContactDataUpdate, 
        db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)) -> Contact | HTTPException:
    """
    Updates data of a specific contact for the current user by ID.

    Args:
        request (Request): The request object.
        contact_id (int): The ID of the contact to update.
        body (ContactDataUpdate): The request body containing the updated data for the contact.
        db (Session): The database session. Defaults to Depends(get_db).
        current_user (User): The current authenticated user obtained from the access token.

    Returns:
        Contact, HTTPException: The updated contact object if found, or an HTTPException with a status code and detail message if the contact is not found.
    """
    user_id = current_user.id
    contact = await repository_contact.update_data_contact(user_id, contact_id, body, db)
    if contact == [] or contact == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact






