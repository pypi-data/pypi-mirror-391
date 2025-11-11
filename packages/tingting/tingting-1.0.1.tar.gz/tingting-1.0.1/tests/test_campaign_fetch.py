
import os
import sys
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting.client import Campaign, TingTingClient

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_get_campaign_list(self):
        client = TingTingClient(BASE_URL,TOKEN)
        campaigns = client.get_campaigns()

        assert type(campaigns) is list
        assert campaigns.__len__() > 0

        for campaign in campaigns:
            assert type(campaign) is Campaign
    
    def test_get_campaign_list_by_name(self):
        client = TingTingClient(BASE_URL,TOKEN)
        campaigns = client.get_campaigns_by_name("t")

        assert type(campaigns) is list
        if campaigns.__len__() > 0:
            assert type(campaigns[0]) is Campaign
    
    def test_get_campaign_list_with_filter(self):
        client = TingTingClient(BASE_URL,TOKEN)
        campaigns = client.get_campaigns_with_filter()

        assert type(campaigns) is list
        if campaigns.__len__() > 0:
            assert type(campaigns[0]) is Campaign
    
    def test_get_campaign(self):
        client = TingTingClient(BASE_URL,TOKEN)
        campaign = client.get_campaign(723)

        assert type(campaign) is Campaign
