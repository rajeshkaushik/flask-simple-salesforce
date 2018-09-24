from simple_salesforce import Salesforce

from zeep import Client
from zeep.transports import Transport

from flask import current_app


def get_sf_object():
    sf_obj = Salesforce(
        username=current_app.config['SF_USERNAME'],
        password=current_app.config['SF_PASSWORD'],
        security_token=current_app.config['SF_SECURITY_TOKEN'],
        domain=current_app.config['SF_DOMAIN']
    )
    return sf_obj


class SingletonSalesforce:

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            sf_obj = get_sf_object()
            cls._instance = super().__new__(cls)
            cls._instance.sf = sf_obj
            cls._instance.WSDL_METHODS = set()
        return cls._instance

    def get_wsdl_service(self, wsdl_path):
        domain = current_app.config['SF_DOMAIN'] + '.salesforce.com'
        wsdl = 'https://{}{}'.format(domain, wsdl_path)

        if not hasattr(self, wsdl_path):
            # Add cookie `sid` to get WSDL
            sid = self.sf.session_id
            self.sf.session.cookies['sid'] = sid
            client = Client(wsdl, transport=Transport(session=self.sf.session))

            # Add SessionHeader for accessing the service
            client.set_default_soapheaders({'SessionHeader': sid})

            setattr(self, wsdl_path, client)
            self.WSDL_METHODS.add(wsdl_path)

        return getattr(self, wsdl_path).service


    @classmethod
    def destroy_instance(cls):
        """
        delete engage instance in case of Salesforce token expires
        """
        if hasattr(cls, '_instance'):
            del cls._instance

    @classmethod
    def update_sf_obj(cls):
        """ refresh the SF instance reference on engage class """

        if hasattr(cls, '_instance'):
            sf_obj = get_sf_object()
            cls._instance.sf = sf_obj
            for client_attr in cls._instance.WSDL_METHODS:
                if hasattr(cls._instance, client_attr):
                    delattr(cls._instance, client_attr)
