import unittest
from datetime import datetime
from unittest.mock import MagicMock 
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contact import ContactUpdate, ContactDataUpdate, ContactResponse, ContactSchema
from src.repository.contact import (
                                    create_contact, 
                                    remove_contact,
                                    update_contact,
                                    update_data_contact,  
                                    get_contact,
                                    get_contacts,
                                    search_contacts,
                                    get_birstdays
                                    )


class TestContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.body = ContactSchema(first_name="max",
                                last_name="krivitskyh",
                                email="max.lol@ex.ua",
                                phone="+380991235634",
                                birthday=datetime(2000, 1, 1),
                                data="Work")
        
        ...

    async def test_create_contact(self):
        result = await create_contact(user_id=self.user.id, body=self.body, db=self.session)
        self.session.add.assert_called()
        self.session.commit.assert_called()
        self.session.refresh.assert_called()
        print(result.birthday)


# async def create_contact(user_id: int, body: ContactSchema,  db: Session):
#     # contact = Contact(**body.model_dump())
#     contact = Contact(
#         first_name = body.first_name,
#         last_name = body.last_name,
#         email = body.email,
#         phone = body.phone,
#         birthday = body.birthday,
#         data = body.data,
#         user_id = user_id
#     )
#     db.add(contact)
#     db.commit()
#     db.refresh(contact)
#     return contact






if __name__ == '__main__':
    unittest.main()