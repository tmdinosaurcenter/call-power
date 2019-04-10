from flask import current_app
import requests

class CRMIntegration(object):

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
        Returns a boolean status"""
        raise NotImplementedError()

    def save_campaign_meta(self, crm_campaign_id, meta):
        """Given a crm_campaign
        Save aggregate call counts to the CRM
        Returns a boolean status"""
        raise NotImplementedError()

class CRMIntegrationError(Exception):
    def __init__(self, message):
        self.message = message

