from flask import current_app

from leads.tests.conftest import AppTestCase

from engage.api import Engage
from engage.exceptions import EngageApiException


class EngageExceptionsTest(AppTestCase):

    def test_resource_not_found(self):
        with self.assertRaises(EngageApiException) as error:
            engage = Engage()
            engage.get_club(145755721)
        self.assertEqual(error.exception.message, 'Resource Club__c not found')

    def test_auth_failed(self):
        with self.assertRaises(EngageApiException) as error:
            with current_app.app_context():
                Engage.destroy_instance()
                current_app.config['SF_USERNAME'] = 'random'
                Engage()
        self.assertEqual(
            error.exception.message, 'Authentication failed with salesforce'
            )

    def test_unknown_error_handled(self):
        with self.assertRaises(EngageApiException) as error:
            with current_app.app_context():
                Engage.destroy_instance()
                current_app.config['SF_DOMAIN'] = 'random'
                Engage()
        self.assertIn(
            'SalesForce call raises exception:', error.exception.message
            )
