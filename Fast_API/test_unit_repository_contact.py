import unittest
from unittest.mock import MagicMock 
from sqlalchemy.orm import Session

from src.database.models import Contact
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
    ...








if __name__ == '__main__':
    unittest.main()