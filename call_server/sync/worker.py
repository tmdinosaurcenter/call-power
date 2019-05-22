from rq.worker import HerokuWorker
from flask import current_app
import logging

logger = logging.getLogger("rq.worker")
logHandler = logging.StreamHandler()
logger.addHandler(logHandler)

class CleanSlateHerokuWorker(HerokuWorker):
    def register_birth(self):
        logger.info('Registering birth of CleanSlateHerokuWorker %s' % self.name)
        super(CleanSlateHerokuWorker, self).register_birth()

    def execute_job(self, *args, **kwargs):
        # close all the sessions before starting to work
        # to avoid SSL issues with Postgres on second work attempt
        current_app.db.close_all_sessions()
        super(CleanSlateHerokuWorker, self).execute_job(*args, **kwargs)