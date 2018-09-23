from simple_salesforce import Salesforce

from zeep import Client
from zeep.transports import Transport

from flask import current_app

from .exceptions import exception_handler


def get_sf_object():
    sf_obj = Salesforce(
        username=current_app.config['SF_USERNAME'],
        password=current_app.config['SF_PASSWORD'],
        security_token=current_app.config['SF_SECURITY_TOKEN'],
        domain=current_app.config['SF_DOMAIN']
    )
    return sf_obj


class Engage:

    ZEEP_CREATE_LEAD_CLIENT = 'create_lead_client'

    @exception_handler
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            sf_obj = get_sf_object()
            cls._instance = super().__new__(cls)
            cls._instance.sf = sf_obj
        return cls._instance

    @exception_handler
    def get_club(self, club_id, field_name='ClubID__c'):
        return self.sf.Club__c.get_by_custom_id(
            custom_id=club_id, custom_id_field=field_name
        )

    @exception_handler
    def get_contact(self, member_id, field_name='Equinox_Member_ID__c'):
        return self.sf.Contact.get_by_custom_id(
            custom_id=member_id, custom_id_field=field_name
        )

    @exception_handler
    def get_datasource(self, datasource_id, field_name='DataSource_Id__c'):
        return self.sf.Datasource__c.get_by_custom_id(
            custom_id=datasource_id, custom_id_field=field_name
        )

    @exception_handler
    def find_leads(self, data):
        recent_leads = []
        data_values = []

        query_param = [
            "Id", "Communication_Preference__c", "WebLead_TransactionID__c",
            "Datasource__c", "FirstName", "LastName", "Phone", "Email",
            "Association_Token__c", "CreatedById", "CreatedDate",
            "Home_Club__c", "Outreach_Code__c", "LastModifiedById",
            "LastModifiedDate", "LeadSource"
        ]
        sql = "SELECT " + ",".join(query_param) + " From Lead Where "

        if data.get("Association_Token__c"):
            sql = sql + "Association_Token__c='{}'"
            data_values.append(str(data["Association_Token__c"]))
        else:
            if data.get('facilityID'):
                facilityID = data.pop("facilityID")
                club = self.get_club(facilityID)
                data['Home_Club__c'] = club['Id']

            for key in data:
                if key == "Datasource__c":
                    sql = sql + "Datasource__r.DataSource_Id__c='{}' AND "
                else:
                    sql = sql + str(key) + "='{}' AND "
                data_values.append(str(data[key]))

        sql = sql.rstrip(" AND")
        query_string = sql.format(*data_values)
        lead_res = self.sf.query(query_string)

        for each_lead in lead_res["records"]:
            Home_Club__c = each_lead["Home_Club__c"]
            facilityID = self.sf.Club__c.get(Home_Club__c)["ClubID__c"]

            recent_leads.append({
                "Id": each_lead["Id"],
                "FirstName": each_lead["FirstName"],
                "LastName": each_lead["LastName"],
                "Phone": each_lead["Phone"],
                "Email": each_lead["Email"],
                "TokenId": each_lead["Association_Token__c"],
                "CreatedDate": each_lead["CreatedDate"],
                "CreatedById": each_lead["CreatedById"],
                "outreachCode": each_lead['Outreach_Code__c'],
                "facilityID": facilityID,
                "customField1": each_lead['Communication_Preference__c'],
                "customField2": each_lead['WebLead_TransactionID__c'],
                "dataSourceID": each_lead['Datasource__c'],
                "LastModifiedById": each_lead['LastModifiedById'],
                "LastModifiedDate": each_lead['LastModifiedDate'],
                "LeadSource": each_lead['LeadSource'],
                })
        return recent_leads

    @exception_handler
    def update_lead(self, lead_id, data):
        self.sf.Lead.update(lead_id, data)

    def _get_create_lead_wsdl_method(self, **kwargs):
        domain = current_app.config['SF_DOMAIN'] + '.salesforce.com'
        method = 'LeadCreationWebService'
        wsdl = 'https://{}/services/wsdl/class/{}'.format(domain, method)

        if not hasattr(self, self.ZEEP_CREATE_LEAD_CLIENT):
            # Add cookie `sid` to get WSDL
            sid = self.sf.session_id
            self.sf.session.cookies['sid'] = sid
            client = Client(wsdl, transport=Transport(session=self.sf.session))

            # Add SessionHeader for accessing the service
            client.set_default_soapheaders({'SessionHeader': sid})

            setattr(self, self.ZEEP_CREATE_LEAD_CLIENT, client)

        return getattr(self, self.ZEEP_CREATE_LEAD_CLIENT).service.createLead

    @exception_handler
    def create_lead(self, data):
        createLead = self._get_create_lead_wsdl_method()
        return createLead(data)

    def create_lead_with_token_id(self, data, token_id):
        lead = self.create_lead(data)

        if lead['body']['result']['isSuccess']:
            self.update_lead(lead['body']['result']['objectId'], {
                'Association_Token__c': token_id})
            return True, lead
        else:
            return False, lead

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
            if hasattr(cls._instance, cls.ZEEP_CREATE_LEAD_CLIENT):
                delattr(cls._instance, cls.ZEEP_CREATE_LEAD_CLIENT)
