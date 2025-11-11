
import os
import sys
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting import (
    Campaign,
    Contact,
    Services,
    SurveyContentType,
    SurveyResponseType,
    SurveyStep,
    TingTingClient,
)

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_survey_launch(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()
        voices = client.get_voices()
        assert voices.__len__() > 0
        voice = voices[0]

        file1 = open("sample_audio.mp3","rb")

        campaign = Campaign(
            client = client,
            name = "Test Survey Launch",
            services = Services.SURVEY,
            dialers = dialers,
            voice = voice,
            draft = False,
            lengthFactor = 1,
            surveySteps=[
                SurveyStep(
                    order=0,
                    client = client,
                    contentType = SurveyContentType.SAY,
                    responseType = SurveyResponseType.DTMF,
                    textOrUrl = "Hello Step1",
                    inputName = "field_1",
                ),
                SurveyStep(
                    order=1,
                    client = client,
                    contentType = SurveyContentType.SAY,
                    responseType = SurveyResponseType.SPEECH,
                    textOrUrl = "Hello Step2",
                    inputName = "field_2",
                ),
                SurveyStep(
                    order=2,
                    client = client,
                    contentType = SurveyContentType.PLAY,
                    responseType = SurveyResponseType.DTMF,
                    inputName = "field_3",
                    audioFile = file1,
                ),
            ]
        ).create()
        file1.close()
        assert type(campaign) is Campaign
        assert type(campaign.id) is int
        

        contact = Contact(
            client = client,
            phoneNumber = "9990000000",
            attributes = {
                "name" : "John",
                "age": 99,
            },
        )
        contact1 = Contact(
            client = client,
            phoneNumber = "9990000001",
            attributes = {
                "name" : "John",
                "age": 99,
            },
        )

        campaign.add_contact(contact)
        campaign.add_contact(contact1)

        campaign.run()