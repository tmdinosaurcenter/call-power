from flask import current_app
import requests

class CRMIntegration(object):
    BATCH_ALL_CALLS_IN_SESSION = False

    def __init__(self, *args, **kwargs):
        self.twilio_client = current_app.config['TWILIO_CLIENT']

    def get_phone(self, twilio_sid):
        """Gets the dialed phone for a Session from Twilio in e164 format"""
        twilio_call = self.twilio_client.calls.get(twilio_sid).fetch()

        # we want the user's phone number, which is either twilio_call.to or from_
        # depending on direction (can be inbound, outbound-api, outbound-dial, or trunking)
        if twilio_call.direction == 'inbound':
            return twilio_call.from_
        elif twilio_call.direction.startswith('outbound'):
            return twilio_call.to

    def get_user(self, phone_number):
        """Gets a user from the CRM with the given phone number
        Returns a unique ID, implementation dependent"""
        raise NotImplementedError()

    def save_action(self, call, crm_campaign_id, crm_user):
        """Given a call, crm_campaign and crm_user
        Save the call attributes (target, duration and status) to the CRM
        Returns a tuple of (boolean status, string message)"""
        raise NotImplementedError()

    def save_campaign_meta(self, crm_campaign_id, meta):
        """Given a crm_campaign
        Save aggregate call counts to the CRM
        Returns a boolean status"""
        raise NotImplementedError()

class CRMIntegrationError(Exception):
    def __init__(self, message):
        self.message = message

def get_crm_integration():
    # setup integration from config values
    if current_app.config['CRM_INTEGRATION'].lower() == 'actionkit':
        from .actionkit_crm import ActionKitIntegration
        ak_credentials = {'domain': current_app.config['ACTIONKIT_DOMAIN'],
                          'username': current_app.config['ACTIONKIT_USER']}
        if 'ACTIONKIT_PASSWORD' in current_app.config:
            ak_credentials['password'] = current_app.config['ACTIONKIT_PASSWORD']
        elif 'ACTIONKIT_API_KEY' in current_app.config:
            ak_credentials['api_key'] = current_app.config['ACTIONKIT_API_KEY']
        else:
            raise CRMIntegrationError('either ACTIONKIT_API_KEY or ACTIONKIT_PASSWORD must be configured')
        crm_integration = ActionKitIntegration(**ak_credentials)
    elif current_app.config['CRM_INTEGRATION'].lower() == 'rogue':
        from .rogue_crm import RogueIntegration
        rogue_credentails = {'domain': current_app.config['ROGUE_DOMAIN'],
                          'api_key': current_app.config['ROGUE_API_KEY']}
        crm_integration = RogueIntegration(**rogue_credentails)
    elif current_app.config['CRM_INTEGRATION'].lower() == 'mobilecommons':
        from .mobile_commons import MobileCommonsIntegration
        mobile_commons_credentials = {
            'username': current_app.config['MOBILE_COMMONS_USERNAME'],
            'password': current_app.config['MOBILE_COMMONS_PASSWORD']
        }
        crm_integration = MobileCommonsIntegration(**mobile_commons_credentials)
    else:
        raise CRMIntegrationError('no CRM_INTEGRATION configured')
        return False
    return crm_integration