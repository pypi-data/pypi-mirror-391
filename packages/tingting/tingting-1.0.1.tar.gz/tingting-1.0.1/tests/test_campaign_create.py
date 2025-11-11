
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting import (
    Campaign,
    CampaignStatus,
    Category,
    FailoverTarget,
    Services,
    TingTingClient,
)

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_create_campaign(self):
        client = TingTingClient(BASE_URL,TOKEN)
        campaign = Campaign(
            client=client,
            name="Test Campaign Create",
        ).create()

        assert type(campaign) is Campaign
        assert type(campaign.id) is int

    def test_create_phone_campaign(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()
        voices = client.get_voices()
        assert voices.__len__() > 0
        voice = voices[0]

        campaign = Campaign(
            client=client,
            name = "Test Create Phone Campaign",
            services = Services.PHONE,
            status = CampaignStatus.NOT_STARTED,
            message = "Phone Campaign Message",
            category = Category.TEXT,
            dialers = dialers,
            voice = voice,
            draft = False,
            lengthFactor = 1,
        ).create()

        assert type(campaign) is Campaign
        assert type(campaign.id) is int

    def test_create_sms_campaign(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()

        campaign = Campaign(
            client = client,
            name = "Test Create SMS Campaign",
            services = Services.SMS,
            status = CampaignStatus.NOT_STARTED,
            smsMessage = "SMS Campaign Message",
            category = Category.TEXT,
            dialers = dialers,
            draft = False,
        ).create()

        assert type(campaign) is Campaign
        assert type(campaign.id) is int

    def test_create_phone_and_sms_campaign(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()
        voices = client.get_voices()
        assert voices.__len__() > 0
        voice = voices[0]

        campaign = Campaign(
            client = client,
            name = "Test Create Phone and SMS Campaign",
            services = Services.SMS_PHONE,
            status = CampaignStatus.NOT_STARTED,
            message = "Phone and SMS campaign Phone Message",
            smsMessage = "Phone and SMS campaign SMS Message",
            category = Category.TEXT,
            dialers = dialers,
            voice = voice,
            draft = False,
            lengthFactor = 1,
            failoverTarget = [
                FailoverTarget.HUNGUP,
                FailoverTarget.UNANSWERED,
                FailoverTarget.FAILED,
            ],
        ).create()

        assert type(campaign) is Campaign
        assert type(campaign.id) is int

    def test_create_scheduled_campaign(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()
        voices = client.get_voices()
        assert voices.__len__() > 0
        voice = voices[0]
        schedule = datetime.now(timezone.utc) + timedelta(minutes=5)

        campaign = Campaign(
            client=client,
            name = "Test Create Scheduled Campaign",
            services = Services.PHONE,
            status = CampaignStatus.NOT_STARTED,
            message = "Scheduled Campaign Message",
            category = Category.TEXT,
            dialers = dialers,
            voice = voice,
            draft = False,
            lengthFactor = 1,
            schedule = schedule,
        ).create()

        assert type(campaign) is Campaign
        assert type(campaign.id) is int
        assert abs((campaign.schedule - schedule).total_seconds()) < 10
