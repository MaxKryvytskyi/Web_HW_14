import unittest
from unittest.mock import MagicMock 
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.user import UserDb, UserSchema 
from src.repository.users import (
                                  create_user, 
                                  remove_user,
                                  update_token,
                                  update_avatar,  
                                  confirmed_email, 
                                  get_user_by_email, 
                                  get_user_by_username
                                  )



class TestUser(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.user_db = UserDb(
            id=1, 
            username="max", 
            email="max.lol@ex.ua", 
            avatar="http://www.example.com/example.jpg", 
            created_at="2024-04-14T12:00:00", 
            confirmed=False)
    
    async def test_create_user(self):
        body = UserSchema(username="max", email="max.lol@ex.ua", password="qwerty")
        result = await create_user(body=body, db=self.session)
        self.session.commit.assert_called()
        self.session.refresh.assert_called()
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "created_at"))
        self.assertTrue(hasattr(result, "updated_at"))
        self.assertTrue(hasattr(result, "refresh_token"))
        self.assertTrue(hasattr(result, "avatar"))
        self.assertTrue(hasattr(result, "confirmed"))

    async def test_confirmed_email(self):
        mocked_metod = MagicMock()
        mocked_metod.scalar_one_or_none.return_value = self.user_db
        self.session.execute.return_value = mocked_metod
        result = await confirmed_email(email="max.lol@ex.ua", db=self.session)
        self.session.commit.assert_called()
        self.assertEqual(result.confirmed, True)
        self.assertTrue(result.confirmed)

    async def test_update_avatar(self):
        new_avatar="http://www.example.com/example1.jpg"
        self.assertNotEqual(new_avatar, self.user_db.avatar)
        mocked_metod = MagicMock()
        mocked_metod.scalar_one_or_none.return_value = self.user_db
        self.session.execute.return_value = mocked_metod
        result = await update_avatar(email="max.lol@ex.ua", url=new_avatar, db=self.session)
        self.session.commit.assert_called()
        self.assertEqual(result.avatar, self.user_db.avatar)

    async def test_update_token(self):
        new_token = "new_refresh_token"
        result = await update_token(user=self.user, token=new_token, db=self.session)
        self.session.commit.assert_called()
        self.assertEqual(result.refresh_token, new_token)

    async def test_get_user_by_email(self):
        mocked_metod = MagicMock()
        mocked_metod.scalar_one_or_none.return_value = self.user_db
        self.session.execute.return_value = mocked_metod
        result = await get_user_by_email(email="max.lol@ex.ua", db=self.session)
        self.assertEqual(result.email, "max.lol@ex.ua")

    async def test_get_user_by_username(self):
        mocked_metod = MagicMock()
        mocked_metod.scalar_one_or_none.return_value = self.user_db
        self.session.execute.return_value = mocked_metod
        result = await get_user_by_username(username="max", db=self.session)
        self.assertEqual(result.username, "max")

    async def test_remove_user(self):
        mocked_metod = MagicMock()
        mocked_metod.scalar_one_or_none.return_value = self.user_db
        self.session.execute.return_value = mocked_metod
        result = await remove_user(email="max.lol@ex.ua", db=self.session)
        self.assertEqual(result.email, self.user_db.email)

# if __name__ == '__main__':
#     unittest.main()