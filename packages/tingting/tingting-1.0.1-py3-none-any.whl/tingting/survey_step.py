import uuid
from typing import IO, TYPE_CHECKING, Optional

from .enums import SurveyContentType, SurveyResponseType

if TYPE_CHECKING:
    from .client import TingTingClient
    
class SurveyStep:
    @classmethod
    def from_data(cls, client:"TingTingClient",data:dict) -> "SurveyStep":
        return SurveyStep(
            client = client,
            id = data.get("id"),
            survey = data.get("survey"),
            order = data.get("order"),
            contentType = data.get("content_type"),
            textOrUrl = data.get("text_or_url"),
            responseType = data.get("response_type"),
            inputName = data.get("input_name"),
            audioFile = data.get("audio_file"),
        )

    def __init__(self,
        client:"TingTingClient",
        id: Optional[int] = None,
        survey: Optional[int] = None,
        order: int = 0,
        contentType: SurveyContentType = SurveyContentType.SAY,
        textOrUrl: str = "",
        responseType: SurveyResponseType = SurveyResponseType.DTMF,
        inputName: str = "field_1",
        audioFile: Optional[IO[bytes]] = None,
    ):
        self._client = client
        self.id = id
        self.survey = survey
        self.order = order
        self.contentType = contentType
        self.textOrUrl = textOrUrl
        self.responseType = responseType
        self.inputName = inputName
        self.audioFile = audioFile
    
    def __str__(self) -> str:
        return f"{self.inputName}"
    
    def json(self) -> dict:
        return {
            "id": self.id or str(uuid.uuid4()),
            "survey": self.survey,
            "order": self.order,
            "content_type": self.contentType.value,
            "text_or_url": self.textOrUrl,
            "response_type": self.responseType.value,
            "input_name": self.inputName,
            "audio_file": None,
        }