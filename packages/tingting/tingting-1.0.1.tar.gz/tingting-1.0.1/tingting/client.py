from typing import IO, List, Optional

import requests

from .campaign import Campaign
from .contact import Contact
from .dialer import Dialer
from .endpoint import Endpoint
from .enums import CampaignStatus
from .survey_step import SurveyStep
from .user import User
from .voice import Voice


class TingTingClient:
    def __init__(self, baseUrl: str, token: str = None):
        self.baseUrl = baseUrl
        self.token = token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}" if self.token else "",
        }

    def get_data(self, endpoint: str, params: dict = None):
        response = requests.get(f"{self.baseUrl}/{endpoint}", headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    def post_data(self, endpoint: str, data: dict):
        response = requests.post(f"{self.baseUrl}/{endpoint}", headers=self._headers(), json=data)
        response.raise_for_status()
        return response.json()


    def get_user(self) -> User:
        response = requests.get(f"{self.baseUrl}/{Endpoint.USER_INFO.value}", headers=self._headers())
        response.raise_for_status()
        data = response.json()
        return User.from_data(self,data)


    def get_dialers(self) -> List[Dialer]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.DIALER_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data:list = response.json()
        dialers = [Dialer.from_data(self,dialer) for dialer in data]
        return dialers

    def get_dialer_by_id(self,id) -> Optional[Dialer]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.DIALER_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data:list = response.json()

        filteredData = list(filter(lambda dialer: dialer.get("id")==id,data))

        if filteredData:
            return Dialer.from_data(self,filteredData[0])
        
        return None

    def get_dialer_by_number(self,phoneNumber) -> Optional[Dialer]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.DIALER_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data:list = response.json()

        filteredData = list(filter(lambda dialer: dialer.get("phone_number")==phoneNumber,data))

        if filteredData:
            return Dialer.from_data(self,filteredData[0])
        
        return None


    def get_voices(self) -> List[Voice]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.VOICE_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data:list = response.json()
        voices = [Voice.from_data(self,voice) for voice in data]
        return voices

    def get_voice_by_id(self,id:int) -> Optional[Voice]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.VOICE_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data:list = response.json()

        filteredData = list(filter(lambda voice: voice.get("id")==id,data))

        if filteredData:
            return Voice.from_data(self,filteredData[0])
        
        return None

    def get_voice_by_name(self,name:str) -> Optional[Voice]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.VOICE_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data:list = response.json()

        filteredData = list(filter(lambda voice: voice.get("voice_display_name","").lower()==name.lower(),data))

        if filteredData:
            return Voice.from_data(self,filteredData[0])
        
        return None


    def get_campaigns(self) -> List[Campaign]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.CAMPAIGN_LIST.value}", headers=self._headers())
        response.raise_for_status()
        data = response.json()
        campaigns = []
        if "results" in data:
            campaigns = [Campaign.from_data(self,camp) for camp in data["results"]]
        
        return campaigns

    def get_campaigns_by_name(self,name:str) -> List[Campaign]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.CAMPAIGN_LIST.value}", headers=self._headers(), params={
            "search":name
        })
        response.raise_for_status()
        data = response.json()
        campaigns = []
        if "results" in data:
            campaigns = [Campaign.from_data(self,camp) for camp in data["results"]]
        
        return campaigns

    def get_campaigns_with_filter(self,name:str=None,status:CampaignStatus=None,draft:bool=False,sort_by=None,from_date=None,to_date=None) -> List[Campaign]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.CAMPAIGN_LIST.value}", headers=self._headers(), params={
            "search":name,
            "status":status,
            "draft":draft,
            "sort_by":sort_by,
            "from_date":from_date,
            "to_date":to_date,
        })
        response.raise_for_status()
        data = response.json()
        campaigns = []
        if "results" in data:
            campaigns = [Campaign.from_data(self,camp) for camp in data["results"]]
        
        return campaigns
    
    def get_campaign(self,id:int) -> List[Campaign]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.CAMPAIGN_GET(id)}", headers=self._headers())
        response.raise_for_status()
        data = response.json()
        return Campaign.from_data(self,data)


    def create_campaign(self,data:dict)->Campaign:
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_CREATE.value}",
            headers=self._headers(),
            json=data,
        )
        response.raise_for_status()
        data = response.json()
        return Campaign.from_data(self,data)

    def update_campaign(self,campaign:Campaign):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_UPDATE(campaign.id)}",
            headers=self._headers(),
            data=campaign.json(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def delete_campaign(self,campaign:Campaign):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_DELETE(campaign.id)}",
            headers=self._headers(),
            data=campaign.json(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def test_voice_campaign(self,campaign:Campaign) -> str:
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_TEST_VOICE(campaign.id)}",
            headers=self._headers(),
            data={
                "voice_input": campaign.voiceId,
                "message": campaign.message,
            },
        )
        response.raise_for_status()
        # data = response.json()
        return response.text
    
    def run_campaign(self,campaign:Campaign):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_RUN_CAMPAIGN(campaign.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def stop_campaign(self,campaign:Campaign):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_STOP_CAMPAIGN(campaign.id)}",
            headers=self._headers(),
            data=campaign.json(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def get_campaign_report(self,campaign:Campaign):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_REPORT(campaign.id)}",
            headers=self._headers(),
            data=campaign.json(),
        )
        response.raise_for_status()
        # data = response.json()


    def add_contact(self,campaignId:int,data:dict) -> Contact:
        response = requests.post(f"{self.baseUrl}/{Endpoint.CONTACT_ADD(campaignId)}",
            headers=self._headers(),
            json=data,
        )
        response.raise_for_status()
        data = response.json()
        return Contact.from_data(self,campaignId,data)

    def add_contact_file(self,campaign:Campaign,file:IO[bytes]):
        response = requests.patch(f"{self.baseUrl}/{Endpoint.CONTACT_ADD_BULK(campaign.id)}",
            headers=self._headers(),
            files = {"bulk_file": ("contacts.csv", file, "text/csv")}
        )
        response.raise_for_status()
        # data = response.json()
    
    def get_contacts(self,campaign:Campaign)->List[Contact]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.CONTACT_LIST(campaign.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def update_contact(self,contact:Contact):
        response = requests.patch(f"{self.baseUrl}/{Endpoint.CONTACT_UPDATE(contact.id)}",
            headers=self._headers(),
            data=contact.json()
        )
        response.raise_for_status()
        # data = response.json()
    
    def delete_contact(self,contact:Contact):
        response = requests.delete(f"{self.baseUrl}/{Endpoint.CONTACT_DELETE(contact.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()

    def get_contact_attribute(self,contact:Contact):
        response = requests.get(f"{self.baseUrl}/{Endpoint.CONTACT_DELETE(contact.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()

    def update_contact_attribute(self,contact:Contact):
        response = requests.delete(f"{self.baseUrl}/{Endpoint.CONTACT_DELETE(contact.id)}",
            headers=self._headers(),
            data=contact.json(),
        )
        response.raise_for_status()
        # data = response.json()

    def test_call(self,contact:Contact):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_DEMO_CALL(contact.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def get_survey_steps(self, campaign:Campaign) -> List[SurveyStep]:
        response = requests.get(f"{self.baseUrl}/{Endpoint.CAMPAIGN_GET_SURVEY_STEPS(campaign.id)}", headers=self._headers())
        response.raise_for_status()
        data = response.json()
        surveySteps = []
        if "results" in data:
            surveySteps = [SurveyStep.from_data(self,step) for step in data["results"]]
        
        return surveySteps

    def create_survey_campaign(self, data:dict,files:list) -> Campaign:
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_CREATE.value}",
            headers=self._headers(),
            json=data,
        )
        response.raise_for_status()
        data_ = response.json()
        campaign = Campaign.from_data(self,data_)

        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_CREATE_SURVEY_STEPS(campaign.id)}",
            headers=self._headers(),
            data=data,
            files=files,
        )

        response.raise_for_status()
        data = response.json()

        surveySteps = self.get_survey_steps(campaign)
        for surveyStep in surveySteps:
            campaign.add_survey_step(surveyStep)
        
        return campaign

    def update_survey_campaign(self, campaign:Campaign,files:list) -> Campaign:
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_UPDATE(campaign.id)}",
            headers=self._headers(),
            data=campaign.json(),
        )
        response.raise_for_status()
        data_ = response.json()
        campaign = Campaign.from_data(self,data_)

        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_UPDATE_SURVEY_STEPS(campaign.id)}",
            headers=self._headers(),
            data=campaign.json(),
            files=files,
        )

        response.raise_for_status()
        _ = response.json()

        surveySteps = self.get_survey_steps(campaign)
        for surveyStep in surveySteps:
            campaign.add_survey_step(surveyStep)
        
        return campaign
    
    def run_survey(self,campaign:Campaign):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_RUN_SURVEY(campaign.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()
    
    def test_survey(self,contact:Contact):
        response = requests.post(f"{self.baseUrl}/{Endpoint.CAMPAIGN_TEST_SURVEY(contact.id)}",
            headers=self._headers(),
        )
        response.raise_for_status()
        # data = response.json()
    