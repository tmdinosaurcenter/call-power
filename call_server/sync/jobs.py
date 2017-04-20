from flask import current_app

from ..extensions import db

from .models import SyncCampaign
from .integrations import CRMIntegrationError

def CRMSync(campaign_id_list='all'):
    # setup integration from config values
    if current_app.config['CRM_INTEGRATION'] == 'ActionKit':
        from .integrations.actionkit_crm import ActionKitIntegration
        ak_credentials = {'domain': current_app.config['ACTIONKIT_DOMAIN'],
                          'username': current_app.config['ACTIONKIT_USER']}
        if 'ACTIONKIT_PASSWORD' in current_app.config:
            ak_credentials['password'] = current_app.config['ACTIONKIT_PASSWORD']
        elif 'ACTIONKIT_API_KEY' in current_app.config:
            ak_credentials['api_key'] = current_app.config['ACTIONKIT_API_KEY']
        else:
            raise CRMIntegrationError('either ACTIONKIT_API_KEY or ACTIONKIT_PASSWORD must be configured')
        crm_integration = ActionKitIntegration(**ak_credentials)
    else:
        raise CRMIntegrationError('no CRM_INTEGRATION configured')
        return False

    print "campaign_id_list",campaign_id_list
    if campaign_id_list == 'all':
        campaigns_to_sync = SyncCampaign.query.all()
    else:
        campaigns_to_sync = SyncCampaign.query.filter(SyncCampaign.campaign_id.in_(campaign_id_list)).all()

    for sync_campaign in campaigns_to_sync:
        current_app.logger.info('sync campaign ID: %s' % sync_campaign.campaign_id)
        sync_campaign.run(crm_integration)