from datetime import datetime, timedelta
from src.database.models import User, Contact


async def mock_get_birstdays(user_id, skip, limit, db):
    from sqlalchemy import func, and_
    from src.schemas.contact import ContactResponse
    #sqlite
    today = datetime.today()
    seven_days_later = today + timedelta(days=7)
    contact_birthdays = db.query(Contact).filter(and_(Contact.user_id == user_id,
        func.strftime('%m-%d', Contact.birthday) >= today.strftime('%m-%d'),
        func.strftime('%m-%d', Contact.birthday) <= seven_days_later.strftime('%m-%d'))).offset(skip).limit(limit).all()
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




def test_create_contact_incorrect_type_email(client, token):
    response = client.post(
        "/api/contacts", json={
        "first_name": "string",
        "last_name": "string",
        "email": "userexamplemcom",
        "phone": "string",
        "birthday": "2024-04-22",
        "data": "string"
        }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422, "Unprocessable Entity"

def test_create_contact_incorrect_type_birthday(client, token):
    response = client.post(
        "/api/contacts", json={
        "first_name": "string",
        "last_name": "string",
        "email": "userexamplemcom",
        "phone": "string",
        "birthday": "2024 04 22",
        "data": "string"
        }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422, "Unprocessable Entity"
    
def test_create_contact(client, session, user, token):
    for num in range(0, 20):
        n = datetime(2000, 4, 20)
        response = client.post(
            "/api/contacts", json={
            "first_name": f"string{num}",
            "last_name": f"string{num}",
            "email": f"user{num}@example.com",
            "phone": f"string{num}",
            "birthday": f"{n + timedelta(days=num)}",
            "data": f"string{num}"
            }, headers={"Authorization": f"Bearer {token}"})
        users = session.query(User).filter(User.email==user["email"]).first()
        contact = session.query(Contact).filter(Contact.user_id==users.id).first()
        assert response.status_code == 201, "Created"
        assert user is not None
        assert contact is not None


def test_get_birstdays_no_contacts(client, token2, monkeypatch):
    monkeypatch.setattr("src.routes.contacts.repository_contact.get_birstdays", mock_get_birstdays)
    response = client.get("/api/contacts/birstdays", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not found"
    data = response.json() 
    assert data["detail"] == "Birstday not found"

def test_get_birstdays(client, token, monkeypatch):
    monkeypatch.setattr("src.routes.contacts.repository_contact.get_birstdays", mock_get_birstdays)
    response = client.get("/api/contacts/birstdays", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data != None
    assert len(data) == 8 


def test_search_contacts_first_name(client, token):
    params = {"first_name": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert len(data) == 2

def test_search_contacts_last_name(client, token):
    params = {"last_name": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert len(data) == 2

def test_search_contacts_email(client, token):
    params = {"email": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert len(data) == 2

def test_search_contacts_phone(client, token):
    params = {"phone": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert len(data) == 2

def test_search_contacts_birthday(client, token):
    params = {"birthday": "2000-04-30"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert len(data) == 1

def test_search_contacts_first_name_no_contacts(client, token2):
    params = {"first_name": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Birstday not found"

def test_search_contacts_last_name_no_contacts(client, token2):
    params = {"last_name": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Birstday not found"

def test_search_contacts_email_no_contacts(client, token2):
    params = {"email": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Birstday not found"

def test_search_contacts_phone_no_contacts(client, token2):
    params = {"phone": "0"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Birstday not found"

def test_search_contacts_birthday_no_contacts(client, token2):
    params = {"birthday": "2000-04-30"}
    response = client.get("/api/contacts/search", params=params, headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Birstday not found"


def test_get_contacts(client, token):
    response = client.get("/api/contacts/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert len(data) == 20

def test_get_contacts_no_contacts(client, token2):
    response = client.get("/api/contacts/", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contact_no_contacts(client, token2):
    contact_id = 1
    response = client.get(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_get_contact(client, token):
    contact_id = 1
    response = client.get(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["id"] == 1


def test_update_data_contact(client, token, session):
    contact_id = 1
    contact = session.query(Contact).filter(Contact.id==contact_id).first()
    old = contact.data
    
    response = client.patch(f"/api/contacts/{contact_id}", json={"data": "Update"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    update_contact = response.json()
    assert update_contact["data"] != old

def test_update_data_contact_no_contacts(client, token2):
    contact_id = 1
    response = client.patch(f"/api/contacts/{contact_id}", json={"data": "Update"}, headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact(client, token, session):
    import copy
    contact_id = 1
    contact = session.query(Contact).filter(Contact.id==contact_id).first()
    contact = copy.deepcopy(contact)
    response = client.put(f"/api/contacts/{contact_id}", 
                            json={
                                "first_name": "string",
                                "last_name": "string",
                                "email": "user@example.com",
                                "phone": "string",
                                "birthday": "2024-04-22",
                                "data": "string"
                                }, 
                            headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["first_name"] != contact.first_name
    assert data["last_name"] != contact.last_name
    assert data["email"] != contact.email
    assert data["phone"] != contact.phone
    assert data["birthday"] != contact.birthday
    assert data["data"] != contact.data

def test_update_contact_no_contacts(client, token2):
    contact_id = 1
    response = client.put(f"/api/contacts/{contact_id}", 
                            json={
                                "first_name": "string",
                                "last_name": "string",
                                "email": "user@example.com",
                                "phone": "string",
                                "birthday": "2024-04-22",
                                "data": "string"
                                }, 
                            headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_remove_contact(client, token, session):
    import copy
    for contact_id in range(1, 21):
        contact = session.query(Contact).filter(Contact.id==contact_id).first()
        contact = copy.deepcopy(contact)
        response = client.delete(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, "OK"
        data = response.json()
        assert data["id"] == contact.id
        assert None == session.query(Contact).filter(Contact.id==contact_id).first()

def test_remove_contact_no_contacts(client, token2):
    contact_id = 20
    response = client.delete(f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 404, "Not Found"
    data = response.json()
    assert data["detail"] == "Contact not found"
