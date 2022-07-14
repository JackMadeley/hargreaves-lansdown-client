from HLClient import HLClient
import os

client = HLClient()
client.login(username=os.getenv(key='hl_username'), date_of_birth=os.getenv(key='hl_dob'),
             password=os.getenv(key='hl_password'), secure_number=os.getenv(key='hl_secure_number'))

client.get_my_accounts()