import unittest
import requests
from datetime import datetime
from unittest.mock import MagicMock, patch, Mock
from sqlalchemy.orm import Session
# from Fast_API.src.services.client_redis import ClientRedis
from src.database.models import Contact, User
from src.schemas.contact import ContactUpdate, ContactDataUpdate, ContactResponse, ContactSchema
from src.repository.contact import (
                                    create_contact, 
                                    remove_contact,
                                    update_contact,
                                    update_data_contact,  
                                    # get_contact,
                                    get_contacts,
                                    search_contacts,
                                    get_birstdays, redis_get
                                    )

def send_request(url):
    response = requests.get(url)
    return response.status_code


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


    async def test_get_contacts(self):
        contact = [Contact(), Contact(), Contact(), Contact(), Contact()]
        mock_get = Mock(return_value=Mock({"1": contact}))
        self.session.query().filter().offset().limit().all.return_value = [Contact()]
        with patch('redis_get', mock_get):
            result = await get_contacts(user_id=self.user.id, skip=10, limit=100, db=self.session)
            print(result)
            assert result == contact

 
        # self.assertEqual(len(result), 1)
        
        # self.set.assert_called_once_with()
        # self.mock_redis.expire.assert_called_once_with()

    async def test_get_contact(self):
        ...

    # async def test_send_request(self):
    #     mock_get = Mock(return_value=Mock(status_code=201))
    #     with patch('requests.get', mock_get):
    #         status_code = send_request('http://example.com')
    #         assert status_code == 201
    #         mock_get.assert_called_once_with('http://example.com')

if __name__ == '__main__':
    unittest.main()