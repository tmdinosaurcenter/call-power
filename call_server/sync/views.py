from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort, jsonify)
from flask.ext.login import login_required


from .models import (SyncCampaign, SyncCall)
sync = Blueprint('sync', __name__, url_prefix='/admin/crmsync')


# all sync routes require login
@sync.before_request
@login_required
def before_request():
    pass


@sync.route('/<int:campaign_id>/', methods=['POST'])
def manual_job(campaign_id):
    campaigns_to_sync = SyncCampaign.query.filter_by(campaign_id=campaign_id).all()
    for sync_campaign in campaigns_to_sync:
        sync_campaign.run(integration)

    # TODO run jobs out of band
    # with scheduler

    return render_template('admin/sync_campaign.html', campaign=campaign, start=start, end=end)