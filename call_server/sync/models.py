from datetime import datetime

from flask import current_app

from ..extensions import db, rq

from ..call.models import Call
from ..campaign.models import Campaign
from .constants import SCHEDULE_IMMEDIATE, SCHEDULE_HOURLY, SCHEDULE_NIGHTLY

class SyncCampaign(db.Model):
    __tablename__ = 'sync_campaign'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), nullable=True) # UUID4
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_sync_time = db.Column(db.DateTime)

    campaign_id = db.Column(db.ForeignKey('campaign_campaign.id'), unique=True)
    campaign = db.relationship('Campaign', backref=db.backref('sync_campaign', uselist=False))
    schedule = db.Column(db.String(25), default=SCHEDULE_HOURLY) # nightly, hourly, immediate

    crm_id = db.Column(db.String(40), nullable=True) # id of the campaign in the CRM

    def __init__(self, campaign_id):
        self.campaign_id = campaign_id
        db.session.add(self)
        db.session.commit()

    def has_schedule(self):
        return self.schedule in (SCHEDULE_NIGHTLY, SCHEDULE_HOURLY, SCHEDULE_IMMEDIATE)

    def is_immediate(self):
        return self.schedule == SCHEDULE_IMMEDIATE

    def start(self, schedule):
        self.schedule = schedule
        if self.schedule == SCHEDULE_IMMEDIATE:
            cron_data = {'minute': '*', 'hour': '*', 'day_of_week':'*', 'month':'*', 'day_of_month': '*'}
        elif self.schedule == SCHEDULE_HOURLY:
            cron_data = {'minute': 0, 'hour': '*', 'day_of_week':'*', 'month':'*', 'day_of_month': '*'}
        elif self.schedule == SCHEDULE_NIGHTLY:
            cron_data = {'minute': 0, 'hour': 23, 'day_of_week':'*', 'month':'*', 'day_of_month': '*'}
        # elif self.schedule == SCHEDULE_END_OF_WEEK:
        #     cron_data = {'minute': 0, 'hour': 23, 'day_of_week':7, 'month':'*', 'day_of_month': '*'}
        # elif self.schedule == SCHEDULE_END_OF_MONTH:
            # actually very start of a new month, because dates are hard
        #     cron_data = {'minute': 0, 'hour': 0, 'month':'*', 'day_of_month': 1}
        else:
            return False
        from jobs import sync_campaigns
        crontab = '{minute} {hour} {day_of_month} {month} {day_of_week}'.format(**cron_data)
        cron_job = sync_campaigns.cron(crontab, 'sync:sync_campaigns:{}'.format(self.campaign_id), self.campaign_id)
        self.job_id = cron_job.id

    def stop(self):
        if self.job_id:
            rq.get_scheduler().cancel(self.job_id)
            return True
        else:
            current_app.logger.warning('unable to stop crm_sync for SyncCampaign {}'.format(self.id))
            return False

    def is_running(self):
        if self.job_id:
            return self.job_id in rq.get_scheduler()
        else:
            return False

    def sync_calls(self, integration):
        # sync all calls for campaign which don't already have a SyncCall

        unsynced_calls = Call.query.filter_by(campaign=self.campaign, sync_call=None)
        if len(unsynced_calls.all()) == 0:
            current_app.logger.info('no calls to sync, exiting early')
            return None
        else:
            current_app.logger.info('{} calls to sync'.format(len(unsynced_calls.all())))
        for call in unsynced_calls:
            # guard for changes after unsynced_call query
            if call.sync_call.first():
                current_app.logger.info('{} has an existing sync_call, continuing'.format(call.id))
                continue

            sync_call = SyncCall(call.id)
            result = sync_call.save_to_crm(self, integration)
            if result:
                db.session.add(sync_call)

            if integration.BATCH_ALL_CALLS_IN_SESSION:
                # get all the other calls in this session
                # create SyncCalls for them too, but skip save_to_crm
                other_calls_in_session = Call.query.filter(
                    Call.session_id==call.session_id,
                    Call.campaign_id==self.campaign.id,
                    Call.id!=call.id
                )
                for other_call in other_calls_in_session:
                    skip_sync = SyncCall(other_call.id)
                    # don't save_to_crm here
                    skip_sync.saved = False
                    db.session.add(skip_sync)
            db.session.commit()

        completed_calls = Call.query.filter_by(campaign=self, status='completed')
        try:
            integration.save_campaign_meta(self.crm_id, {'count': completed_calls.count()})
        except NotImplementedError:
            current_app.logger.info('crm_integration.save_campaign_meta not implemented')
        self.last_sync_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class SyncCall(db.Model):
    __tablename__ = 'sync_call'

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    call_id = db.Column(db.ForeignKey('calls.id'))
    call = db.relationship('Call', backref=db.backref('sync_call', lazy='dynamic'))

    saved = db.Column(db.Boolean, default=False)

    def __init__(self, call_id):
        self.call_id = call_id
        self.call = Call.query.get(self.call_id)

    def save_to_crm(self, sync_campaign, integration):
        # we only keep a hash of the phone locally, for privacy
        # so hit twilio to get the actual phone to match to the CRM
        
        if self.call:
            twilio_sid = self.call.call_id
            user_phone = integration.get_phone(twilio_sid)
        else:
            current_app.logger.warning('unable to get twilio_sid for call: %s' % self.call)
            return False

        if not user_phone:
            current_app.logger.warning('unable to get user_phone for twilio_sid: %s' % twilio_sid)
            return False

        crm_user = integration.get_user(user_phone)
        if not crm_user:
            current_app.logger.warning('unable to get crm user for phone: %s' % user_phone)
            return False

        self.saved = integration.save_action(self.call, sync_campaign.crm_id, crm_user)
        current_app.logger.info('synced call %s by %s' % (self.call.id, crm_user['id']))
        return True
