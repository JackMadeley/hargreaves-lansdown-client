import pandas as pd

from HLClient import HLClient
import os
import unittest
from typing import List


class TestHLClient(unittest.TestCase):

    def setUp(self):
        self.client = HLClient()
        self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                          password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))

    def test_hl_client_login(self):
        if len(self.client.cookie_jar) == 0:
            self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                              password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))
        self.assertEqual(len(self.client.cookie_jar), 2)

    def test_get_account_links(self):
        if len(self.client.cookie_jar) == 0:
            self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                              password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))
        accounts: dict = self.client.get_account_links()
        self.assertEqual(len(accounts.keys()) > 0, True)

    def test_get_portfolio_overview(self):
        if len(self.client.cookie_jar) == 0:
            self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                              password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))
        portfolio = self.client.get_portfolio_overview()
        self.assertEqual(portfolio.empty, False)

    def test_get_account_dataframes(self):
        if len(self.client.cookie_jar) == 0:
            self.client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
                              password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))
        dataframes = self.client.get_account_dataframes()
        status: List[bool] = []
        for df in dataframes:
            status.append(not df.empty)
        self.assertEqual(all(status), True)
