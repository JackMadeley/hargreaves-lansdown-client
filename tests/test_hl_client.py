
from HLClient import HLClient
import os
import unittest


class TestHLClient(unittest.TestCase):

    def setUp(self):
        self.client = HLClient()

    def test_hl_client_login(self):
        self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                          password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))
        self.assertEqual(len(self.client.cookie_jar), 2)

    def test_get_accounts(self):
        if len(self.client.cookie_jar) == 0:
            self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                              password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))
        accounts = self.client.get_my_accounts()
        self.assertEqual(accounts.empty, False)
