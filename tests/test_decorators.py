from flask import current_app

from tests.conftest import AppTestCase

from simple_salesforce.exceptions import SalesforceExpiredSession

from flask_simple_salesforce.api import SingletonSalesforce
from flask_simple_salesforce.decorators import retry_on_session_expire

class FlaskSimpleSalesForceDecoratorsTest(AppTestCase):

    @retry_on_session_expire
    def find_users(self):
        engage = SingletonSalesforce()
        return engage.sf.search("FIND {Rajesh}")

    def test_expired_session_refreshed_once(self):
        engage = SingletonSalesforce()
        engage.sf.session_id = 'ufu542154dsf5df4sf45455454'
        engage.sf.headers['Authorization'] = 'ufu542154dsf5df4sf45455454'
        users = self.find_users()
        self.assertTrue(users.get('searchRecords'))
    
    @retry_on_session_expire
    def find_users_expired_session(self):
        engage = SingletonSalesforce()
        engage.sf.session_id = 'ufu542154dsf5df4sf45455454'
        engage.sf.headers['Authorization'] = 'ufu542154dsf5df4sf45455454'
        return engage.sf.search("FIND {Rajesh}")

    def test_expired_session_refreshed_only_once(self):
        with self.assertRaises(SalesforceExpiredSession) as error:
            users = self.find_users_expired_session()
            self.assertTrue(users.get('searchRecords'))
