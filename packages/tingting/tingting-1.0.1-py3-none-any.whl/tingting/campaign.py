from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from .contact import Contact
from .dialer import Dialer
from .enums import CampaignStatus, Category, FailoverTarget, Services
from .survey_step import SurveyStep
from .voice import Voice

if TYPE_CHECKING:
    from .client import TingTingClient

class Campaign:
    @classmethod
    def from_data(cls, client:"TingTingClient",data:dict) -> "Campaign":
        if isinstance(data.get("voice"),dict):
            voice = Voice.from_data(client,data.get("voice"))
            voiceId = voice.id
        else:
            voice = None
            voiceId:int = data.get("voice")
            
        failoverTarget:List[Optional[FailoverTarget]] = []
        for status in data.get("failover_target"):
            failoverTarget.append(FailoverTarget.from_str(status))
        
        schedule = data.get("schedule")
        if schedule:
            schedule = datetime.fromisoformat(schedule)
        
        return Campaign(
            client = client,
            id = data.get("id"),
            name = data.get("name"),
            services = Services.from_str(data.get("services")),
            status = CampaignStatus.from_str(data.get("status")),
            smsMessage = data.get("sms_message"),
            message = data.get("message"),
            description = data.get("description"),
            schedule = schedule,
            audioFile = data.get("audio_file"),
            bulkFile = data.get("bulk_file"),
            category = Category.from_str(data.get("category")),
            dialers = data.get("user_phone"),
            contactCount = data.get("campaign_action_count"),
            progressPercent = data.get("progress_percent"),
            updatedAt = data.get("updated_at"),
            creditLimit = data.get("credit_limit"),
            voice = voice,
            voiceId = voiceId,
            draft = data.get("draft"),
            failoverTarget = failoverTarget,
            lengthFactor = data.get("lengthFactor"),
        )

    def __init__(self,
        client:"TingTingClient",
        id: Optional[int] = None,
        name: str = "Test Campaign",
        services: Services = Services.PHONE,
        status: CampaignStatus = CampaignStatus.NOT_STARTED,
        smsMessage: str = "default sms message",
        message: str = "default message",
        description: str = "default description",
        schedule: Optional[datetime] = None,
        audioFile: Optional[str] = None,
        bulkFile: Optional[str] = None,
        category: Category = Category.TEXT,
        dialers: Union[List[int],List[Dialer]] = None,
        contactCount: int = 0,
        progressPercent: int = 0,
        updatedAt: datetime = None,
        creditLimit: int = 0,
        voiceId: Optional[int] = None,
        voice: Optional[Voice] = None,
        draft: bool = False,
        failoverTarget:List[Optional[FailoverTarget]] = None,
        lengthFactor:float = 1,
        surveySteps: Optional[List[SurveyStep]] = None
    ):
        self._client = client
        self.id = id
        self.name = name
        self.services = services
        self.status = status
        self.smsMessage = smsMessage
        self.message = message
        self.description = description
        self.schedule = schedule
        self.audioFile = audioFile
        self.bulkFile = bulkFile
        self.category = category
        self.dialers = dialers or []
        self.contactCount = contactCount
        self.progressPercent = progressPercent
        self.updatedAt = updatedAt
        self.creditLimit = creditLimit
        self.voiceId = voice.id if voice else voiceId
        self._voice = voice
        self.draft = draft
        self.failoverTarget = failoverTarget or []
        self.lengthFactor = lengthFactor
        self.surveySteps = surveySteps or []

    def __str__(self)->str:
        return f"{self.name}"
    
    def json(self)->dict:
        return {
            "id":self.id,
            "name":self.name,
            "services":self.services.value,
            "status":self.status.value,
            "sms_message":self.smsMessage,
            "message":self.message,
            "description":self.description,
            "schedule":self.schedule.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" if self.schedule else None,
            "audio_file":self.audioFile,
            "bulk_file":self.bulkFile,
            "category":self.category.value,
            "user_phone":[(dialer.id if type(dialer) is Dialer else dialer) for dialer in self.dialers],
            "campaign_action_count":self.contactCount,
            "progress_percent":self.progressPercent,
            "updated_at":self.updatedAt,
            "credit_limit":self.creditLimit,
            "voice":self.voiceId,
            "draft":self.draft,
            "failover_target":[target.value for target in self.failoverTarget if target],
            "length_factor":self.lengthFactor,
            "steps":[step.json() for step in self.surveySteps],
        }
    
    def update_from(self, other: "Campaign"):
        self.id = other.id
        self.name = other.name
        self.services = other.services
        self.status = other.status
        self.smsMessage = other.smsMessage
        self.message = other.message
        self.description = other.description
        self.schedule = other.schedule
        self.audioFile = other.audioFile
        self.bulkFile = other.bulkFile
        self.category = other.category
        self.dialers = other.dialers
        self.contactCount = other.contactCount
        self.progressPercent = other.progressPercent
        self.updatedAt = other.updatedAt
        self.creditLimit = other.creditLimit
        self.voiceId = other.voiceId
        self._voice = other._voice
        self.draft = other.draft
        self.failoverTarget = other.failoverTarget
        self.lengthFactor = other.lengthFactor


    def delete(self):
        pass

    def save(self):
        if self.id:
            return self.update()
        return self.create()
    
    def get_voice(self) -> Voice:
        if not self._voice:
            self._voice = self._client.get_voice_by_id(self.voiceId)
        return self._voice

    def _get_files(self) -> dict:
        files = {}
        for idx, step in enumerate(self.surveySteps):
            if step.audioFile:
                files[str(idx)] = step.audioFile
        return files

    def create(self) -> "Campaign":
        json = self.json()
        voice = self.get_voice()
        if voice:
            json["voice"] = voice.json()
        else:
            del json["voice"]
        
        if self.services == Services.SURVEY:
            files = self._get_files()
            created = self._client.create_survey_campaign(json,files)
        else:
            created = self._client.create_campaign(json)
        self.update_from(created)
        return self

    def update(self):
        pass


    def test_voice(self)->str:
        return self._client.test_voice_campaign(self)

    def run(self):
        if self.services == Services.SURVEY:
            return self._client.run_survey(self)
        return self._client.run_campaign(self)

    def stop(self):
        pass

    def get_report(self)->str:
        pass

    def add_contact(self,contact: Contact) -> Contact:
        contact.campaignId = self.id
        return contact.create()

    def add_contact_from_file(self,file):
        self._client.add_contact_file(self,file)

    def add_survey_step(self,surveyStep:SurveyStep):
        surveyStep.order = self.surveySteps.__len__()
        self.surveySteps.append(surveyStep)