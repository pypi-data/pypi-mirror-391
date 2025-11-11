
import os
import sys
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting import (
    Campaign,
    CampaignStatus,
    Category,
    Contact,
    Services,
    TingTingClient,
)

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_campaign_test_voice(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()
        voices = client.get_voices()
        assert voices.__len__() > 0
        voice = voices[0]

        campaign = Campaign(
            client = client,
            name = "Test Campaign Test Voice",
            services = Services.PHONE,
            status = CampaignStatus.NOT_STARTED,
            message = "Phone Campaign Message",
            category = Category.TEXT,
            dialers = dialers,
            voice = voice,
            draft = False,
            lengthFactor = 1,
        )
        campaign.create()

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

        campaign.add_contact(contact)

        audio_url = campaign.test_voice()
        assert audio_url.startswith("\"https://")