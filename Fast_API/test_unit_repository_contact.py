import unittest
import redis
import pickle
from datetime import datetime
from unittest.mock import MagicMock, patch
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
        self.user = User(id=1)
        self.mock_redis = MagicMock(return_value=None)


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
        contacts = [Contact(), Contact(), Contact(), Contact()]
        self.mock_redis.get.return_value = {'1': contacts}

        # self.mock_redis.get.return_value = pickle.dumps([Contact(), Contact(), Contact(), Contact()])
        self.session.query().filter().offset().limit().all.return_value = [Contact(), Contact(), Contact()]
        result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
        print(result)
        self.assertEqual(len(result), 3)
        
        # self.mock_redis.set.assert_called_once_with()
        # self.mock_redis.expire.assert_called_once_with()

    async def test_get_contact(self):
        ...
#     contacts = db.query(Contact).filter(Contact.user_id==user_id).offset(skip).limit(limit).all()
#     return contacts






if __name__ == '__main__':
    unittest.main()