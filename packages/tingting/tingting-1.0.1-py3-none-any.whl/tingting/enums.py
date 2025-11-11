from enum import Enum
from typing import Optional


class CampaignStatus(Enum):
    NOT_STARTED = "Not Started"
    SCHEDULED = "Scheduled"
    RUNNING = "Running"
    COMPLETED = "Completed"
    TERMINATED = "Terminated"

    @classmethod
    def from_str(cls, value: str) -> Optional["CampaignStatus"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class ContactStatus(Enum):
    NOT_STARTED = "not started"
    RINGING = "ringing"
    DIALING = "dialing"
    ANSWERED = "answered"
    HUNGUP = "hungup"
    UNANSWERED = "unanswered"
    FAILED = "failed"
    TERMINATED = "terminated"
    COMPLETED = "completed"

    @classmethod
    def from_str(cls, value: str) -> Optional["ContactStatus"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class Services(Enum):
    SMS = "SMS"
    PHONE = "PHONE"
    SMS_PHONE = "SMS & PHONE"
    SURVEY = "SURVEY"

    @classmethod
    def from_str(cls, value: str) -> Optional["Services"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class Category(Enum):
    TEXT = "Text"
    AUDIO = "Audio"

    @classmethod
    def from_str(cls, value: str) -> Optional["Category"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class FailoverTarget(Enum):
    NOT_STARTED = "not started"
    HUNGUP = "hungup"
    UNANSWERED = "unanswered"
    FAILED = "failed"
    COMPLETED = "completed"

    @classmethod
    def from_str(cls, value: str) -> Optional["FailoverTarget"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class SurveyContentType(Enum):
    SAY = "say"
    PLAY = "play"
    INFO = "info"

    @classmethod
    def from_str(cls, value: str) -> Optional["FailoverTarget"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class SurveyResponseType(Enum):
    SPEECH = "raw_record"
    DTMF = "dtmf"
    NONE = "none"

    @classmethod
    def from_str(cls, value: str) -> Optional["FailoverTarget"]:
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None