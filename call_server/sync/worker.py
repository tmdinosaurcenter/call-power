from rq.worker import HerokuWorker
from flask import current_app

class CleanSlateHerokuWorker(HerokuWorker):
    def execute_job(self, *args, **kwargs):
        # close all the sessions before starting to work
        # to avoid SSL issues with Postgres on second work attempt
        current_app.db.close_all_sessions()
        super(CleanSlateHerokuWorker, self).execute_job(*args, **kwargs)