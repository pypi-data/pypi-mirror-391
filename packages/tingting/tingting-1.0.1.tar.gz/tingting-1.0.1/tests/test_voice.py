
import os
import sys
import unittest

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tingting.client import TingTingClient, Voice

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
TOKEN = os.environ.get("TOKEN")

class TestTingTingClient(unittest.TestCase):
    def test_get_voices(self):
        client = TingTingClient(BASE_URL,TOKEN)
        voices = client.get_voices()

        assert type(voices) is list
        assert voices.__len__() > 0
        
        for voice in voices:
            assert type(voice) is Voice

    def test_get_voice_by_id(self):
        client = TingTingClient(BASE_URL,TOKEN)
        id = 1
        voice = client.get_voice_by_id(id)

        assert type(voice) is Voice
        assert voice.id == id

    def test_get_voice_by_name(self):
        client = TingTingClient(BASE_URL,TOKEN)
        name = "rija"
        voice = client.get_voice_by_name(name)

        assert type(voice) is Voice
        assert voice.displayName == name
