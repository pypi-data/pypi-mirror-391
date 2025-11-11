
import os
import sys
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting.client import Dialer, TingTingClient

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_get_dialers(self):
        client = TingTingClient(BASE_URL,TOKEN)
        dialers = client.get_dialers()

        assert type(dialers) is list
        assert dialers.__len__() > 0

        for dialer in dialers:
            assert type(dialer) is Dialer

    def test_get_dialer_by_id(self):
        client = TingTingClient(BASE_URL,TOKEN)
        id = 10
        dialer = client.get_dialer_by_id(id)

        assert type(dialer) is Dialer
        assert dialer.id == id

    def test_get_dialer_by_name(self):
        client = TingTingClient(BASE_URL,TOKEN)
        phoneNumber = "+97715970969"
        dialer = client.get_dialer_by_number(phoneNumber)

        assert type(dialer) is Dialer
        assert dialer.phoneNumber == phoneNumber
