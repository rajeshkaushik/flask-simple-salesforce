from flask import current_app

from tests.conftest import AppTestCase

from flask_simple_salesforce.api import SingletonSalesforce
from flask_simple_salesforce.exceptions import EngageApiException


class EngageExceptionsTest(AppTestCase):

    def test_resource_not_found(self):
        with self.assertRaises(EngageApiException) as error:
            engage = SingletonSalesforce()
            engage.sf.Club__c.get_by_custom_id(145755721)
        self.assertEqual(error.exception.message, 'Resource Club__c not found')

#    def test_auth_failed(self):
#        with self.assertRaises(EngageApiException) as error:
#            with current_app.app_context():
#                SingletonSalesforce.destroy_instance()
#                current_app.config['SF_USERNAME'] = 'random'
#                SingletonSalesforce()
#        self.assertEqual(
#            error.exception.message, 'Authentication failed with salesforce'
#            )
#
#    def test_unknown_error_handled(self):
#        with self.assertRaises(EngageApiException) as error:
#            with current_app.app_context():
#                SingletonSalesforce.destroy_instance()
#                current_app.config['SF_DOMAIN'] = 'random'
#                SingletonSalesforce()
#        self.assertIn(
#            'SalesForce call raises exception:', error.exception.message
#            )
