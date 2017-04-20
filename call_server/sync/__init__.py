from .views import sync
from .models import SyncCampaign, SyncCall
from .jobs import CRMSync

class SyncError(Exception):
    def __init__(self, message):
        self.message = message

