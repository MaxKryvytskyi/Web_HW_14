import unittest
import fastapi
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas.contact import ContactUpdate, ContactDataUpdate, ContactSchema
from src.services.client_redis import client_redis 
from src.repository.contacts import (
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
    
    async def test_create_contact(self):
        result = await create_contact(user_id=self.user.id, body=self.body, db=self.session)
        self.session.add.assert_called()
        self.session.commit.assert_called()
        self.session.refresh.assert_called()
        self.assertEqual(result.user_id, self.user.id)

    async def test_get_contacts(self):
        user_id=1
        contacts = [Contact(), Contact(), Contact(), Contact(), Contact()]
        contact = [Contact()]
        contact_none = []
        client_redis.redis_get = MagicMock(return_value=contacts)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = None
        result = await get_contacts(user_id=user_id, skip=0, limit=100, db=self.session)
        self.assertEqual(result, contacts)

        client_redis.redis_get = MagicMock(return_value=contact)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = None
        result = await get_contacts(user_id=user_id, skip=0, limit=100, db=self.session)
        self.assertEqual(result, contact)

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = contact
        result = await get_contacts(user_id=user_id, skip=0, limit=100, db=self.session)
        self.assertEqual(result, contact)

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = contact_none
        result = await get_contacts(user_id=user_id, skip=0, limit=100, db=self.session)
        self.assertEqual(result, contact_none)

    async def test_get_contact(self):
        user_id=1
        contact_id=1
        contact = Contact()
        client_redis.redis_get = MagicMock(return_value=contact)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query.return_value.filter.return_value.first.return_value = None
        result = await get_contact(user_id=user_id, contact_id=contact_id, db=self.session)
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
        contact = Contact(id=contact_id)
       
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

    async def test_remove_contact(self):
        user_id=1
        contact_id=1
        contact = Contact(id=contact_id)
        self.session.query.return_value.filter.return_value.first.return_value = contact
        result = await remove_contact(user_id=user_id, contact_id=contact_id, db=self.session)
        self.session.delete.assert_called()
        self.session.commit.assert_called()
        self.assertEqual(result, contact)

        self.session.query.return_value.filter.return_value.first.return_value = None
        result = await remove_contact(user_id=user_id, contact_id=contact_id, db=self.session)
        self.assertIsNone(self.session.delete.assert_called())
        self.assertIsNone(self.session.commit.assert_called())
        self.assertIsNone(result)

    async def test_update_data_contact(self):
        user_id=1
        contact_id=1
        body = ContactDataUpdate(data="Test_update_data_contact")
        contact = Contact(id=contact_id)
        self.session.query.return_value.filter.return_value.first.return_value = contact
        result = await update_data_contact(user_id=user_id, contact_id=contact_id, body=body, db=self.session)   
        self.session.commit.assert_called()
        self.assertEqual(result.data, body.data)

        self.session.query.return_value.filter.return_value.first.return_value = None
        result = await update_data_contact(user_id=user_id, contact_id=contact_id, body=body, db=self.session)   
        self.assertIsNone(self.session.commit.assert_called())
        self.assertIsNone(result)

        contact = Contact(id=contact_id, data="Test_update_data_contact")
        self.session.query.return_value.filter.return_value.first.return_value = contact
        with self.assertRaises(fastapi.exceptions.HTTPException):
            result = await update_data_contact(user_id=user_id, contact_id=contact_id, body=body, db=self.session)   
        self.assertIsNone(self.session.commit.assert_called())
        self.assertIsNone(result)

    async def test_get_birstdays(self):
        user_id = 1
        contacts = [Contact(
                id = 1,
                first_name="max",
                last_name="krivitskyh",
                email="max.lol@ex.ua", 
                phone="+380991235634", 
                birthday=datetime(2000, 1, 1), 
                data="Work",  
                user_id = 1), 
                    Contact(
                id = 2,
                first_name="max1",
                last_name="krivitskyh1",
                email="max1.lol@ex.ua", 
                phone="+380991235632", 
                birthday=datetime(1991, 1, 1), 
                data="Work1",  
                user_id = 1), 
                     Contact(                
                id = 3,
                first_name="max2",
                last_name="krivitskyh2",
                email="max2.lol@ex.ua", 
                phone="+380991235631", 
                birthday=datetime(2001, 1, 1), 
                data="Work2",  
                user_id = 1)]
        self.session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = contacts
        result = await get_birstdays(user_id=user_id, skip=0, limit=100, db=self.session)
        self.assertNotEqual(result, contacts)

        self.session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = None
        result = await get_birstdays(user_id=user_id, skip=0, limit=100, db=self.session)
        self.assertEqual(result, [])

    async def test_search_contacts(self):
        user_id=1
        first_name='max'
        last_name=None
        email=None
        phone=None
        contacts = [Contact(
                id = 1,
                first_name="max",
                last_name="krivitskyh",
                email="max.lol@ex.ua", 
                phone="+380991235634", 
                birthday=datetime(2000, 1, 1), 
                data="Work",  
                user_id = 1), 
                    Contact(
                id = 2,
                first_name="artem",
                last_name="grid",
                email="grid.lol@ex.ua", 
                phone="+380991235632", 
                birthday=datetime(1991, 1, 1), 
                data="Work",  
                user_id = 1), 
                     Contact(                
                id = 3,
                first_name="olena",
                last_name="krivitskyh",
                email="olena.lol@ex.ua", 
                phone="+380991235631", 
                birthday=datetime(2001, 1, 1), 
                data="Family",  
                user_id = 1)]
        birthday=datetime(1999, 4, 18)
        self.session.query.return_value.filter.return_value = None
        result = await search_contacts(user_id=user_id, first_name=first_name, last_name=last_name, email=email, phone=phone, birthday=birthday, db=self.session)   
        self.assertListEqual(result, [])

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.ilike.return_value = query_mock
        query_mock.all.return_value = contacts
        self.session.query.return_value = query_mock
        result = await search_contacts(user_id=user_id, first_name=first_name, last_name=last_name, email=email, phone=phone, birthday=birthday, db=self.session)   
        self.assertEqual(len(result), len(contacts))

# if __name__ == '__main__':
#     unittest.main()