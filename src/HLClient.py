import pandas as pd
import re
import logging
from requests import Session
from bs4 import BeautifulSoup as bs
from requests.cookies import RequestsCookieJar


class HLClient(object):

    def __init__(self):
        self.stage_one_url = "https://online.hl.co.uk/my-accounts/login-step-one"
        self.stage_two_url = "https://online.hl.co.uk/my-accounts/login-step-two"
        self.accounts_url = "https://online.hl.co.uk/my-accounts"
        self.portfolio_overview_url = "https://online.hl.co.uk/my-accounts/portfolio_overview"
        self.session = Session()
        self.cookie_jar: RequestsCookieJar = RequestsCookieJar()

    def login(self, username: str, date_of_birth: str, password: str, secure_number: str):
        with self.session as s:
            page = s.get(url=self.stage_one_url)
            if page.status_code == 200:
                page_content = bs(page.content, 'lxml')
                try:
                    hl_vt = page_content.select_one('input[name=hl_vt]')['value']
                    form_data = {"hl_vt": hl_vt, "username": f"{username}", "date-of-birth": f"{date_of_birth}"}
                    s1_post_request = s.post(url=self.stage_one_url, data=form_data, cookies=page.cookies)
                    if s1_post_request.status_code == 200:
                        s1_post_response = bs(s1_post_request.content, 'lxml')
                        identity = s1_post_response.find(lambda tag: tag.name == 'div' and
                                                                     tag.get('class') == ['identity'])
                        errors = identity.find_all("div",{"class": "error-message"})
                        if len(errors) == 0:
                            secure_number_containers = \
                                s1_post_response.find_all("div",{"class": "secure-number-container__label"})
                            if len(secure_number_containers) > 0:
                                keys = [int((div.contents[2].strip()[0])) - 1 for div in secure_number_containers]
                                try:
                                    hl_vt = s1_post_response.select_one('input[name=hl_vt]')['value']
                                    form_data = {'hl_vt': hl_vt, "online-password-verification": password,
                                                 "secure-number[1]": str(secure_number[keys[0]]),
                                                 "secure-number[2]": str(secure_number[keys[1]]),
                                                 "secure-number[3]": str(secure_number[keys[2]]),
                                                 "submit": "+Log+in+++"}
                                    s2_post_request = s.post(url=self.stage_two_url, data=form_data,
                                                             cookies=s1_post_request.cookies)
                                    if s2_post_request.status_code == 200:
                                        self.cookie_jar = s2_post_request.cookies
                                    else:
                                        logging.error(
                                            f"Unable to load stage one url {self.stage_two_url}, post request returned "
                                            f"{s2_post_request.status_code} status code ")
                                except TypeError:
                                    logging.error(
                                        f"Unable to locate hl_vt verification token in stage two of authentication.")
                            else:
                                logging.error(f"Unable to locate secure number fields, cannot complete authentication")
                        else:
                            logging.error(f"Invalid username or date of birth credentials, please check again")
                except TypeError:
                    logging.error(f"Unable to locate hl_vt verification token in stage one of authentication.")
            else:
                logging.error(f'Unable to load stage one url {self.stage_one_url}, get request returned status code '
                              f'{page.status_code}')

    def get_account_links(self) -> dict:
        if len(self.cookie_jar.keys()) > 0:
            with self.session as s:
                get_request = s.get(url=self.accounts_url, cookies=self.cookie_jar)
                if get_request.status_code == 200:
                    get_context = bs(get_request.content, 'lxml')
                    accounts_table = get_context.find_all("a",{"class": "product-name"})
                    if len(accounts_table) > 0:
                        output_dict = {}
                        for tag in accounts_table:
                            href = tag.attrs['href']
                            account = str(tag.contents[0]).strip()
                            output_dict[account] = href
                        return output_dict
                    else:
                        logging.error(f"Could not find accounts table at {self.accounts_url}.")
                else:
                    logging.error(f"Unable to load {self.accounts_url}, get request returned status code "
                                  f"{get_request.status_code}")
        else: logging.error("Unable to get portfolio overview, session is not authenticated.")

    def get_portfolio_overview(self) -> pd.DataFrame:
        if len(self.cookie_jar.keys()) > 0:
            with self.session as s:
                get_request = s.get(url=self.portfolio_overview_url, cookies=self.cookie_jar)
                if get_request.status_code == 200:
                    get_context = bs(get_request.content, 'lxml')
                    portfolio_table = get_context.find_all(id='portfolio')
                    if len(portfolio_table) > 0:
                        html_string = f"<html><body>{str(portfolio_table[0])}</body></html>"
                        df: pd.DataFrame = pd.read_html(html_string)[0]
                        df.drop(columns=['Action'], inplace=True)
                        return df
                    else:
                        logging.error(f"Unable to locate portfolio table at {self.portfolio_overview_url}")
                else:
                    logging.error(f"Unable to load {self.portfolio_overview_url}, get request returned status code "
                                  f"{get_request.status_code}")
        else:
            logging.error("Unable to get portfolio overview, session is not authenticated. Please login before proceeding.")
