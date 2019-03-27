from flask import current_app

import requests
from requests_toolbelt import sessions
from . import CRMIntegration
import phonenumbers

class RogueIntegration(CRMIntegration):

    def __init__(self, domain, api_key):
        super(RogueIntegration, self).__init__()
        if api_key:
            self.rogue_session = sessions.BaseUrlSession(
                base_url=domain)
        else:
            raise Exception('unable to authenticate to Rogue')

    def get_user(self, phone_number):
        """Not required for Rogue, we have a one-shot API with phone number"""
        raise NotImplementedError()


    def save_action(self, call, crm_campaign_id, crm_user):
        """Given a sync_call, crm_campaign and crm_user
        Save the call attributes (target, duration and status) to the CRM
        Returns a boolean status"""
        
        # create the call action
        call_action = {
            'mobile': crm_user['phone'], # required
            'callpower_campaign_id': crm_campaign_id,
            'status': call.status,
            'call_timestamp':
            'call_duration': call.duration,
            'campaign_target_name': call.target.name
            'campaign_target_title': call.target.title,
            'campaign_target_district': call.target.district,
            'callpower_campaign_name': call.campaign.name,
            'number_dialed_into': call.session.from_number, 
        }
        current_app.logger.info("creating action: %s" % call_action) 
        rogue_response = self.rogue_session.post('api/v1/callpower/call', call_action)
        return rogue_response.ok


    def save_campaign_meta(self, crm_campaign_id, meta={}):
        """Given a page name (crm_campaign_id) 
        Save meta values to pagefields
        Returns a boolean status"""
        raise NotImplementedError()
