import time
from copy import deepcopy
import uuid

from leads.tests.conftest import AppTestCase
from leads.api.v1.key_mappings import LeadAPIMapper
from engage.api import Engage
from engage.exceptions import EngageApiException
from leads.api.v1.utils import get_lead_update_data


class EngageTestCase(AppTestCase):
    facilityId = 115
    memberId = 8888888888

    @property
    def create_lead_data(self):
        name = str(time.time())
        return {
            'company': 'default',
            'dataSourceId': '64C83CDA-EB76-DE11-828D-000C29D3B4F0',
            'notes': 'Pytest - Test Description',
            'comm_Preference': None,
            'webLead_TransID': 'dflksjdflksdklfjsdfjlksadkljfksdfljsdf',
            'googleAdWords': 'dfdfgdsgsdfgsdfgsdgsdf',
            'emailAddress': 'test-user@example.com',
            'facilityID': 115,
            'firstName': 'Test',
            'lastName': name,
            'outreachCode': 'POPUPLEAD',
            'phoneNumber': 8181818181,
            'hasOptedOutOfEmail': True,
            'wantToBeTexted': True,
            'leadChannel': 'Web'
        }

    update_data = {
        "questionAnswers": [
            {
                "questionId": "lead_ques1",
                "answers": [
                    {
                        "additionalInformation": "",
                        "answerId": 83
                    },
                    {
                        "additionalInformation": "question 1 ",
                        "answerId": 94
                    },
                    {
                        "additionalInformation": "other text",
                        "answerId": 128
                    }
                ]
            },
            {
                "questionId": "lead_ques4",
                "answers": [
                    {
                        "additionalInformation": "",
                        "answerId": 101
                    },
                    {
                        "additionalInformation": "additional text",
                        "answerId": 104
                    }
                ]
            },
            {
                "questionId": "lead_ques3",
                "answers": [
                    {
                        "additionalInformation": "",
                        "answerId": 98
                    }
                ]
            }
        ],
    }

    def generate_find_data(self, **data):
        keys_to_remove = ['googleAdWords', 'leadChannel', 'comm_Preference',
                          'wantToBeTexted', 'webLead_TransID', 'company',
                          'hasOptedOutOfEmail', 'notes']

        # fdata = data.copy()
        for key in keys_to_remove:
            data.pop(key)

        input_dict = {k: v for k, v in data.items() if str(v).strip()}
        find_data = LeadAPIMapper.map(**input_dict)
        return find_data

    def test_engage_singleton_behaviour(self):
        sf_instance1 = Engage()
        sf_instance2 = Engage()
        self.assertEqual(sf_instance1.sf, sf_instance2.sf)

    def test_destroy_instance_remove_sf_instance(self):
        Engage()
        self.assertTrue(hasattr(Engage, '_instance'))
        Engage.destroy_instance()
        self.assertFalse(hasattr(Engage, '_instance'))

    def test_get_club_with_valid_clubId(self):
        engage = Engage()
        club = engage.get_club(self.facilityId)
        self.assertIn("Id", club)

    def test_expired_session_refreshed(self):
        engage = Engage()
        engage.sf.session_id = 'ufu542154dsf5df4sf45455454'
        club = engage.get_club(self.facilityId)
        self.assertIn("Id", club)

    def test_get_club_with_invalid_clubId(self):
        with self.assertRaises(EngageApiException) as error:
            engage = Engage()
            engage.get_club(11)
        self.assertEqual(error.exception.message, 'Resource Club__c not found')

    def test_get_datasource(self):
        engage = Engage()
        datasource = engage.get_datasource(
            '64C83CDA-EB76-DE11-828D-000C29D3B4F0'
            )
        self.assertIn("Id", datasource)

    def test_invalid_data_source(self):
        with self.assertRaises(EngageApiException) as error:
            engage = Engage()
            engage.get_datasource(111)
        self.assertEqual(
            error.exception.message,
            'Resource Datasource__c not found'
        )

    def test_create_lead(self):
        engage = Engage()
        lead = engage.create_lead(self.create_lead_data)

        self.assertEqual(lead['body']['result']['isSuccess'], True)
        lead_id = lead['body']['result']['objectId']

        engage.sf.Lead.delete(lead_id)

    def test_find_lead(self):
        engage = Engage()
        create_lead_data = self.create_lead_data
        engage.create_lead(create_lead_data)
        find_lead_data = self.generate_find_data(**create_lead_data)

        leads = engage.find_leads(find_lead_data)

        self.assertEqual(leads[0]["FirstName"], "Test")
        self.assertEqual(type(leads), list)

    def test_find_lead_no_data_found(self):
        engage = Engage()
        data = {"Association_Token__c": 1234}
        lead = engage.find_leads(data)
        self.assertEqual(type(lead), list)
        self.assertEqual(lead, [])

    def test_find_lead_blank_input(self):
        engage = Engage()
        data = {}
        with self.assertRaises(EngageApiException) as error:
            engage.find_leads(data)
        self.assertEqual(
            error.exception.message,
            "Unknown error occurred in Salesforce"
        )

    def test_create_duplicate_lead(self):
        engage = Engage()

        data = dict()
        data.update(self.create_lead_data)

        resp1 = engage.create_lead(data)
        self.assertEqual(resp1['body']['result']['isSuccess'], True)

        resp2 = engage.create_lead(data)
        self.assertEqual(resp2['body']['result']['isSuccess'], False)

    def test_update_invalid_key(self):
        engage = Engage()
        lead = engage.create_lead(self.create_lead_data)
        lead_id = lead['body']['result']['objectId']
        with self.assertRaises(EngageApiException) as error:
            engage.update_lead(lead_id, {'key': 'invalid key'})
        self.assertEqual(
            error.exception.message,
            'Unknown error occurred in Salesforce'
        )
        engage.sf.Lead.delete(lead_id)

    def test_update_lead_valid_data(self):
        engage = Engage()
        lead_data = self.create_lead_data
        token_id = str(uuid.uuid4())
        status, lead = engage.create_lead_with_token_id(lead_data, token_id)
        self.assertEqual(lead['body']['result']['isSuccess'], True)
        lead_id = lead['body']['result']['objectId']
        data = deepcopy(self.update_data)
        data['tokenID'] = token_id
        data = get_lead_update_data(data)
        engage.update_lead(lead_id, data)
        engage.sf.Lead.delete(lead_id)
