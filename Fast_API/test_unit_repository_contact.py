import unittest
import redis
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas.contact import ContactUpdate, ContactDataUpdate, ContactResponse, ContactSchema
from src.services.client_redis import client_redis 
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
        self.user = User(id=1)
        self.session = MagicMock(spec=Session)
        self.body = ContactSchema(first_name="max",
                                last_name="krivitskyh",
                                email="max.lol@ex.ua",
                                phone="+380991235634",
                                birthday=datetime(2000, 1, 1),
                                data="Work")
    
    #
    async def test_create_contact(self):
        result = await create_contact(user_id=self.user.id, body=self.body, db=self.session)
        self.session.add.assert_called()
        self.session.commit.assert_called()
        self.session.refresh.assert_called()
        self.assertEqual(result.user_id, self.user.id)

    #
    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact(), Contact(), Contact()]
        contact = [Contact()]
        contact_none = []
        client_redis.redis_get = MagicMock(return_value=contacts)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = None
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertEqual(result, contacts)

        client_redis.redis_get = MagicMock(return_value=contact)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = None
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertEqual(result, contact)

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = contact
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertEqual(result, contact)

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = contact_none
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertEqual(result, contact_none)

    #
    async def test_get_contact(self):
        contact = Contact()
        client_redis.redis_get = MagicMock(return_value=contact)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query.return_value.filter.return_value.first.return_value = None
        result = await get_contact(user_id=self.user.id, contact_id=1, db=self.session)
        self.assertEqual(result, contact)  

        contact = Contact()
        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query.return_value.filter.return_value.first.return_value = contact
        result = await get_contact(user_id=self.user.id, contact_id=1, db=self.session)
        self.assertEqual(result, contact)   

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query.return_value.filter.return_value.first.return_value = None
        result = await get_contact(user_id=self.user.id, contact_id=1, db=self.session)
        self.assertIsNone(result)   
 
    
    async def test_update_contact(self):
        contact_id=1
        user_id=1
        contact = Contact(id=1)
       
        body = ContactUpdate(first_name="max",
                             last_name="krivitskyh",
                             email="max.lol@ex.ua",
                             phone="+380991235634",
                             birthday=datetime(1990, 1, 31),
                             data="work")
        self.session.query.return_value.filter.return_value.first.return_value = contact
        result = await update_contact(user_id=user_id, contact_id=contact_id, body=body, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.data, body.data)
        self.session.commit.assert_called()

        self.session.query.return_value.filter.return_value.first.return_value = None
        result = await update_contact(user_id=user_id, contact_id=contact_id, body=body, db=self.session)
        self.assertIsNone(result)
        self.assertIsNone(self.session.commit.assert_called())


# async def update_contact(user_id: int, contact_id: int, body: ContactUpdate, db: Session):
#     contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user_id)).first()
#     if contact:
#         contact.first_name = body.first_name
#         contact.last_name = body.last_name
#         user = db.query(Contact).filter(Contact.email==body.email).first()
        
#         if user is None:
#             contact.email = body.email
#         user = db.query(Contact).filter(Contact.phone==body.phone).first()

#         if user is None:
#             contact.phone = body.phone
#         contact.birthday = body.birthday
#         contact.data = body.data
#         db.commit()
#     return contact

if __name__ == '__main__':
    unittest.main()