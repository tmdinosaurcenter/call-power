from flask import current_app

from ..extensions import rq

from .models import SyncCampaign

@rq.job(timeout=60*60)
def sync_campaigns(campaign_id='all'):
    if campaign_id == 'all':
        campaigns_to_sync = SyncCampaign.query.all()
    else:
        campaigns_to_sync = SyncCampaign.query.filter_by(campaign_id=campaign_id)

    for sync_campaign in campaigns_to_sync:
        current_app.logger.info('sync campaign ID: %s' % sync_campaign.campaign_id)
        sync_campaign.sync_calls()