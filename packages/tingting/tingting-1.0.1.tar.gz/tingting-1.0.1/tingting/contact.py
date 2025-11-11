from typing import TYPE_CHECKING, Optional

from .enums import ContactStatus

if TYPE_CHECKING:
    from .client import TingTingClient


class Contact:
    @classmethod
    def from_data(cls, client:"TingTingClient",campaignId:int,data:dict) -> "Contact":
        return Contact(
            client = client,
            id = data.get("id"),
            phoneNumber = data.get("number"),
            campaignId = campaignId,
            status = ContactStatus.from_str(data.get("status")),
            duration = data.get("call_duration"),
            playback = data.get("playback"),
            creditConsumed = data.get("credit_consumed"),
            creditConsumedSMS = data.get("credit_consumed_SMS"),
            carrier = data.get("carrier"),
            attributes = data.get("attributes"),
        )

    def __init__(self,
        client:"TingTingClient",
        id:Optional[int] = None,
        phoneNumber: str = "",
        campaignId: int = 0,
        status: ContactStatus = ContactStatus.NOT_STARTED,
        duration: str = "",
        playback: str = "",
        creditConsumed: int = 0,
        creditConsumedSMS: int = 0,
        carrier: str = "other",
        attributes: dict = None,
    ):
        self._client = client
        self.id = id
        self.phoneNumber = phoneNumber
        self.campaignId = campaignId
        self.status = status
        self.duration = duration
        self.playback = playback
        self.creditConsumed = creditConsumed
        self.creditConsumedSMS = creditConsumedSMS
        self.carrier = carrier
        self.attributes = attributes
    
    def __str__(self):
        return f"{self.phoneNumber}"
    
    def json(self):
        return {
            "id": self.id,
            "number": self.phoneNumber,
            "campaign_id": self.campaignId,
            "status": self.status.value,
            "duration": self.duration,
            "playback": self.playback,
            "credit_consumed": self.creditConsumed,
            "credit_consumed_SMS": self.creditConsumedSMS,
            "carrier": self.carrier,
            "other_variables": self.attributes,
        }
    
    def update_from(self, other: "Contact"):
        self.id = other.id
        self.phoneNumber = other.phoneNumber
        self.campaignId = other.campaignId
        self.status = other.status
        self.duration = other.duration
        self.playback = other.playback
        self.creditConsumed = other.creditConsumed
        self.creditConsumedSMS = other.creditConsumedSMS
        self.carrier = other.carrier
        self.attributes = other.attributes

    def delete(self):
        return self._client.delete_contact(self)

    def save(self):
        if self.id:
            return self.update()
        return self.create()

    def create(self) -> "Contact":
        json = self.json()
        created = self._client.add_contact(self.campaignId,json)
        self.update_from(created)
        return self

    def update(self):
        return self._client.update_contact(self)

    def test_call(self):
        return self._client.test_call(self)

    def test_survey(self):
        return self._client.test_survey(self)