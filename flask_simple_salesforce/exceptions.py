from requests.exceptions import ConnectionError
from simple_salesforce.exceptions import (
    SalesforceError,
    SalesforceMoreThanOneRecord,
    SalesforceResourceNotFound,
    SalesforceAuthenticationFailed,
    SalesforceExpiredSession
)


def exception_handler(func):
    """
    catch Salesforce exceptions and raise EngageApiException
    """
    def wrapper(*args, **kwargs):
        try:
            try:
                return func(*args, **kwargs)
            except SalesforceExpiredSession as e:
                from engage.api import Engage
                # update the sf instance for one retry
                Engage.update_sf_obj()
                return func(*args, **kwargs)
            except ConnectionError:
                try:
                    return func(*args, **kwargs)
                except SalesforceExpiredSession as e:
                    from engage.api import Engage
                    # update the sf instance for one retry
                    Engage.update_sf_obj()
                    return func(*args, **kwargs)
        except SalesforceResourceNotFound as e:
            raise EngageApiException(
                "Resource {} not found".format(e.resource_name),
                e.url, e.status, e.content
                )
        except SalesforceMoreThanOneRecord as e:
            raise EngageApiException(
                "More than one resource for given {}".format(e.resource_name),
                e.url, e.status, e.content
                )
        except SalesforceAuthenticationFailed as e:
            raise EngageApiException(
                "Authentication failed with salesforce",
                '', e.code, e.message
            )
        except SalesforceExpiredSession as e:
            from engage.api import Engage
            # delete the existing engage instance
            # engage instance will be created in next api call
            Engage.update_sf_obj()
            raise EngageApiException(
                "Session was expired, please try again to continue",
                e.url, e.status, e.content
            )
        except SalesforceError as e:
            raise EngageApiException(
                "Unknown error occurred in Salesforce",
                e.url, e.status, e.content
                )
        except EngageApiException as e:
            raise e
        except Exception as e:
            raise EngageApiException(
                    "SalesForce call raises exception: {}".format(str(e)),
                    '', '', ''
                )
    return wrapper


class EngageException(Exception):
    def __init__(self, message, url, status, content):
        self.message = message
        self.url = url
        self.status = status
        self.content = content


class EngageApiException(EngageException):
    pass
