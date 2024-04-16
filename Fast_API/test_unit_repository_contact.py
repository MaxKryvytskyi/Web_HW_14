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
        self.contacts = [Contact(), Contact(), Contact(), Contact(), Contact()]
        self.contact = [Contact()]
        self.contact_none = []
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


    async def test_get_contacts(self):
        client_redis.redis_get = MagicMock(return_value=self.contacts)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = None
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertAlmostEqual(result, self.contacts)

        client_redis.redis_get = MagicMock(return_value=self.contact)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = None
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertAlmostEqual(result, self.contact)

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = self.contact
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertAlmostEqual(result, self.contact)

        client_redis.redis_get = MagicMock(return_value=None)
        client_redis.redis_set = MagicMock(return_value=True)
        client_redis.redis_expire = MagicMock(return_value=True)
        self.session.query().filter().offset().limit().all.return_value = self.contact_none
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        self.assertAlmostEqual(result, self.contact_none)

    async def test_get_contact(self):
        ...
 

if __name__ == '__main__':
    unittest.main()