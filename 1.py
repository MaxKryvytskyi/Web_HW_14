import unittest
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from Fast_API.src.database.models import Contact, User
from Fast_API.src.schemas.contact import ContactSchema
from Fast_API.src.services.client_redis import client_redis 
from Fast_API.src.repository.contact import get_contacts


class TestContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user=User(id=1)
        self.session=MagicMock(spec=Session)
        self.contacts = [Contact(), Contact(), Contact(), Contact(), Contact()]
        self.contact = [Contact()]
        self.contact_none = []

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

if __name__ == '__main__':
    unittest.main()