import pytest
import collections

# ---------------------------------------------------------------------------
# Compatibility shims for Python 3.11+
#
# A number of third-party libraries still import abstract base classes such as
# ``MutableMapping`` and ``Iterable`` directly from :mod:`collections`.  These
# attributes were moved to :mod:`collections.abc` in newer Python versions.  To
# maintain compatibility without modifying the bundled libraries themselves, we
# backfill the missing names onto :mod:`collections` before any imports that may
# rely on them run.
# ---------------------------------------------------------------------------
for _name in (
    "MutableMapping",
    "Mapping",
    "MutableSet",
    "MutableSequence",
    "Sequence",
    "Iterable",
):  # pragma: no cover - defensive best-effort patch
    try:
        setattr(collections, _name, getattr(collections.abc, _name))
    except AttributeError:
        continue

from dotenv import load_dotenv

from flask_testing import TestCase

if __name__ == '__main__' and __package__ is None:
    load_dotenv()
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from call_server.app import create_app, db
from call_server.config import TestingConfig
from call_server.extensions import assets

class BaseTestCase(TestCase):
    __test__ = False

    def create_app(self):
        assets._named_bundles = {}
        return create_app(TestingConfig)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
    pytest.main(['tests'])
