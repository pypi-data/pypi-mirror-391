
import os
import sys
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting.client import TingTingClient, User

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_get_user(self):
        client = TingTingClient(BASE_URL,TOKEN)
        user = client.get_user()

        assert type(user) is User
        assert type(user.id) is int
