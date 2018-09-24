import time
from copy import deepcopy
import uuid

from tests.conftest import AppTestCase
from flask_simple_salesforce.api import SingletonSalesforce


class EngageTestCase(AppTestCase):

    def test_engage_singleton_behaviour(self):
        sf_instance1 = SingletonSalesforce()
        sf_instance2 = SingletonSalesforce()
        self.assertEqual(sf_instance1.sf, sf_instance2.sf)

    def test_destroy_instance_remove_sf_instance(self):
        SingletonSalesforce()
        self.assertTrue(hasattr(SingletonSalesforce, '_instance'))
        SingletonSalesforce.destroy_instance()
        self.assertFalse(hasattr(SingletonSalesforce, '_instance'))

