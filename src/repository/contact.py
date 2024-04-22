from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_
from fastapi import HTTPException, status
from datetime import datetime, timedelta, date

from src.database.models import Contact
from src.schemas.contact import ContactUpdate, ContactSchema, ContactDataUpdate, ContactResponse
from src.services.client_redis import client_redis


# test is ready
async def create_contact(user_id: int, body: ContactSchema,  db: Session) -> Contact:
    """
    Creates a new contact for the user.

    Args:
        user_id (int): Identifier of the user.
        body (ContactSchema): New contact details.
        db (Session): Data base sessions.

    Returns:
        Contact: Established contact.
    """
    contact = Contact(
        first_name = body.first_name,
        last_name = body.last_name,
        email = body.email,
        phone = body.phone,
        birthday = body.birthday,
        data = body.data,
        user_id = user_id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


# test is ready 
async def get_contacts(user_id: int, skip: int, limit: int, db: Session) -> list[Contact] | list:
    """
    Retrieves user contacts.

    Args:
        user_id (int): The user's identifier.
        skip (int): The number of contacts to skip.
        limit (int): The maximum number of contacts to return.
        db (Session): The database session.

    Returns:
        list[Contact] | list: A list of user contacts or an empty list if no contacts are found.
    """
    contacts = client_redis.redis_get(user_id)
    if contacts:
        return contacts
    contacts = db.query(Contact).filter(Contact.user_id==user_id).offset(skip).limit(limit).all()
    client_redis.redis_set(user_id, contacts)
    client_redis.redis_expire(user_id)
    return contacts


# test is ready
async def get_contact(user_id: int, contact_id: int, db: Session) -> Contact | None:
    """
    Retrieves a user's contact by its ID.

    Args:
        user_id (int): The user's identifier.
        contact_id (int): The ID of the contact to retrieve.
        db (Session): The database session.

    Returns:
        Contact | None: The requested contact if found, else None.
    """
    contact = client_redis.redis_get(user_id)
    if contact:
        return contact
    contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user_id)).first()
    client_redis.redis_set(user_id, contact)
    client_redis.redis_expire(user_id)
    return contact


# test is ready
async def remove_contact(user_id: int, contact_id: int, db: Session) -> Contact | None:
    """
    Removes a contact associated with a user.

    Args:
        user_id (int): The user's identifier.
        contact_id (int): The ID of the contact to remove.
        db (Session): The database session.

    Returns:
        Contact | None: The removed contact if found, else None.
    """
    contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


# test is ready
async def update_contact(user_id: int, contact_id: int, body: ContactUpdate, db: Session) -> Contact | None:
    """
    Updates the details of a user's contact.

    Args:
        user_id (int): The user's identifier.
        contact_id (int): The ID of the contact to update.
        body (ContactUpdate): The updated details of the contact.
        db (Session): The database session.

    Returns:
        Contact | None: The updated contact if found, else None.
    """
    contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user_id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        # user = db.query(Contact).filter(Contact.email==body.email).first() не помню зачем я сделал єто
        
        # if user is None:
        contact.email = body.email
        # user = db.query(Contact).filter(Contact.phone==body.phone).first() не помню зачем я сделал єто

        # if user is None:
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.data = body.data
        db.commit()
    return contact


# test is ready
async def update_data_contact(user_id: int, contact_id: int, body: ContactDataUpdate, db: Session) -> Contact | None:
    """
    Updates the data field of a user's contact.

    Args:
        user_id (int): The user's identifier.
        contact_id (int): The ID of the contact to update.
        body (ContactDataUpdate): The updated data of the contact.
        db (Session): The database session.

    Returns:
        Contact | None: The updated contact if found, else None.
    Raises:
        HTTPException: If the provided data conflicts with existing data.
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user_id, Contact.id==contact_id)).first()
    if contact:
        if contact.data == body.data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'With this data "{body.data}" data exists')
        else:
            contact.data = body.data
            db.commit()
    return contact


# test is ready
async def get_birstdays(user_id: int, skip: int, limit: int, db: Session) -> list[ContactResponse] | list:
    
    """
    Retrieves upcoming birthdays of contacts for a user.

    Args:
        user_id (int): The user's identifier.
        skip (int): The number of birthdays to skip.
        limit (int): The maximum number of birthdays to return.
        db (Session): The database session.

    Returns:
        List[ContactResponse], List: A list of upcoming birthdays of contacts for the user, 
        or an empty list if no birthdays are found.
    """
    # postgres
    today = datetime.today()
    seven_days_later = today + timedelta(days=7)
    contact_birthdays = db.query(Contact).filter(and_(Contact.user_id==user_id,
        text("TO_CHAR(birthday, 'MM-DD') BETWEEN :start_date AND :end_date")).params(
        start_date=today.strftime('%m-%d'), 
        end_date=seven_days_later.strftime('%m-%d'))).offset(skip).limit(limit).all()
    contact_list = []
    if not contact_birthdays:
        return contact_list
    for contact in contact_birthdays:
        contact_response = ContactResponse(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            birthday=contact.birthday,
            data=contact.data,
            user_id=contact.user_id)
        contact_list.append(contact_response)
    return contact_list
    


# test is ready
async def search_contacts(user_id: int, first_name: str, last_name: str, email: str, phone: str, birthday: date, db: Session) -> list[Contact] | list:
    """
    Searches for contacts based on the provided criteria.

    Args:
        user_id (int): The user's identifier.
        first_name (str): The first name to search for.
        last_name (str): The last name to search for.
        email (str): The email to search for.
        phone (str): The phone number to search for.
        birthday (date): The birthday to search for.
        db (Session): The database session.

    Returns:
        List[Contact], List: A list of contacts matching the search criteria, 
        or an empty list if no contacts are found.
    """
    query = db.query(Contact).filter(Contact.user_id==user_id)
    contacts = []
    if first_name and query is not None:
        query1 = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
        contacts.extend(query1.all())
    if last_name and query is not None:
        query1 = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
        contacts.extend(query1.all())
    if email and query is not None:
        query1 = query.filter(Contact.email.ilike(f"%{email}%"))     
        contacts.extend(query1.all())
    if phone and query is not None:
        query1 = query.filter(Contact.phone.ilike(f"%{phone}%"))       
        contacts.extend(query1.all())
    if birthday and query is not None:
        query1 = query.filter(func.DATE(Contact.birthday) == birthday)
        contacts.extend(query1.all())
 
    return list(set(contacts))
