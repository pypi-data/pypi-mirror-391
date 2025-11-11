from enum import Enum


class Endpoint(Enum):
    USER_INFO = "api/v1/auths/user-profile/"
    DIALER_LIST = "api/v1/active-broker-phone/"
    VOICE_LIST = "api/v1/voice-models/"

    CAMPAIGN_LIST = "api/v1/campaign/"
    CAMPAIGN_CREATE = "api/v1/campaign/create/"
    CAMPAIGN_GET = lambda campaignId : f"api/v1/campaign/{campaignId}/"
    CAMPAIGN_UPDATE = lambda campaignId : f"api/v1/campaign/{campaignId}/"
    CAMPAIGN_DELETE = lambda campaignId : f"api/v1/campaign/{campaignId}/"
    CAMPAIGN_TEST_VOICE = lambda campaignId : f"api/v1/test-speak/riri/{campaignId}/"
    CAMPAIGN_RUN_CAMPAIGN = lambda campaignId : f"api/v1/run-campaign/{campaignId}/"
    CAMPAIGN_STOP_CAMPAIGN = lambda campaignId : f"api/v1/campaign/emergency-stop/{campaignId}/"
    CAMPAIGN_REPORT = lambda campaignId : f"api/v1/download/report/{campaignId}/"

    CAMPAIGN_GET_SURVEY_STEPS = lambda campaignId : f"api/v1/campaign/create/{campaignId}/survey/"
    CAMPAIGN_CREATE_SURVEY_STEPS = lambda campaignId : f"api/v1/campaign/create/{campaignId}/survey/"
    CAMPAIGN_UPDATE_SURVEY_STEPS = lambda campaignId : f"api/v1/campaign/create/{campaignId}/survey/"
    CAMPAIGN_DELETE_SURVEY_STEPS = lambda campaignId : f"api/v1/campaign/create/{campaignId}/survey/"

    CAMPAIGN_RUN_SURVEY = lambda campaignId : f"api/v1/run-survey/{campaignId}/"
    CAMPAIGN_TEST_SURVEY = lambda contactId : f"api/v1/test-survey/{contactId}/"

    CONTACT_ADD = lambda campaignId : f"api/v1/campaign/{campaignId}/add-contact/"
    CONTACT_ADD_BULK = lambda campaignId : f"api/v1/campaign/create/{campaignId}/detail/"
    CONTACT_LIST = lambda campaignId: f"api/v1/campaign-detail/{campaignId}/"
    CONTACT_UPDATE = lambda contactId: f"api/v1/phone-number/update/{contactId}/"
    CONTACT_DELETE = lambda contactId: f"api/v1/phone-number/delete/{contactId}/"
    CAMPAIGN_DEMO_CALL = lambda contactId : f"api/v1/demo-call/{contactId}/"

    CONTACT_ATTRIBUTES = lambda id: f"api/v1/campaign/{id}/attributes/"
    CONTACT_ATTRIBUTES_UPDATE = lambda id: f"api/v1/campaign/{id}/attributes/"

