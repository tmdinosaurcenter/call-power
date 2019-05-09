from flask import current_app

import requests
from xml.etree import ElementTree
from requests.auth import HTTPBasicAuth
from requests_toolbelt import sessions
import dateutil.parser
from utils import utc_now

from . import CRMIntegration

class MobileCommonsIntegration(CRMIntegration):
    BATCH_ALL_CALLS_IN_SESSION = True
    # this forces the SyncCampaign to save only the first call in a session, to avoid duplicates

    def __init__(self, username, password):
        super(MobileCommonsIntegration, self).__init__()
        if username and password:
            self.mc_api = sessions.BaseUrlSession(
                base_url='https://secure.mcommons.com')
            self.mc_api.auth = HTTPBasicAuth(username, password)
        else:
            raise Exception('unable to authenticate to MobileCommons')

    def get_user(self, phone_number):
        """Not required for MobileCommons, we have a one-shot API with phone number"""
        # this is basically a no-op, but wraps the data in the desired format
        return {
            'id': phone_number,
            'phone': phone_number
        }

    def ok_to_subscribe_user(self, crm_campaign_id, crm_user):
        # check user profile for existing subscription or opt-out
        # returns True to go ahead
        # False if we should stop
        # None if there isn't an existing user in the CRM
        data = {
            'phone_number': crm_user['phone'],
        }

        response = self.mc_api.get('/api/profile', params=data)
        results = ElementTree.fromstring(response.content)
        user_profile = results.find('profile')
        if not user_profile:
            return None

        user_status = user_profile.find('status').text
        profile_subscriptions = user_profile.find('subscriptions')
        campaign_subscriptions = []
        for s in profile_subscriptions:
            if s.get('campaign_id') == crm_campaign_id:
                # copy matching subscriptions to a local list, so we can sort and reverse
                campaign_subscriptions.append({
                    'created_at': dateutil.parser.isoparse(s.get('created_at')),
                    'status': s.get('status')    
                })

        # should already be ordered by created_at, double check tho
        sorted_subscriptions = sorted(campaign_subscriptions, key=lambda k: k['created_at'])

        most_recent_subscription = sorted_subscriptions[-1]
        # if user's most recent action is to opt out, don't re-prompt
        if most_recent_subscription.get('status') == 'Opted-Out':
            current_app.logger.warning('user (%s) opted out of campaign (%s)' % (crm_user['phone'], crm_campaign_id))
            return False

        # if user is subscribed, don't re-prompt
        if most_recent_subscription.get('status') == 'Active':
            current_app.logger.info('user (%s) already subscribed to campaign (%s)' % (crm_user['phone'], crm_campaign_id))
            return False

        # if user was prompted within last 30 days, don't re-prompt
        since_last_prompt = most_recent_subscription.get('created_at') - utc_now()
        if since_last_prompt.days < 30:
            current_app.logger.info('user (%s) prompted about campaign (%s) at ' %
                (crm_user['phone'], crm_campaign_id, most_recent_subscription.get('created_at').isoformat())
            )
            return False
    
        # no flags? go ahead
        return True


    def save_action(self, call, crm_campaign_id, crm_user):
        """Given a crm_user and crm_campaign_id (opt in path)
        Subscribe the user's phone number via the opt-in path
        Returns a boolean status"""

        if not self.ok_to_subscribe_user(crm_campaign_id, crm_user):
            current_app.logger.info('not ok to subscribe user (%s) to campaign (%s)' % (crm_user['phone'], crm_campaign_id))
            return False

        data = {
            'phone_number': crm_user['phone'],
            'opt_in_path_id': crm_campaign_id
        }

        response = self.mc_api.post('/api/profile_update', data)
        results = ElementTree.fromstring(response.content)
        success = bool(results.get('success'))
        # coerce 'true'/'false' into boolean

        return success


    def save_campaign_meta(self, crm_campaign_id, meta={}):
        """Given a page name (crm_campaign_id) 
        Save meta values to pagefields
        Returns a boolean status"""
        raise NotImplementedError()
