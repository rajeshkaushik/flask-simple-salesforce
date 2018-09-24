from requests.exceptions import ConnectionError
from simple_salesforce.exceptions import SalesforceExpiredSession

from flask_simple_salesforce.api import SingletonSalesforce


def retry_on_session_expire(func):
    """
    Decorator to retry once on SalesforceExpiredSession or ConnectionError.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SalesforceExpiredSession as e:
            # update the sf instance for one retry
            SingletonSalesforce.update_sf_obj()
            return func(*args, **kwargs)
        except ConnectionError:
            try:
                return func(*args, **kwargs)
            except SalesforceExpiredSession as e:
                # update the sf instance for one retry
                SingletonSalesforce.update_sf_obj()
                return func(*args, **kwargs)
    return wrapper
