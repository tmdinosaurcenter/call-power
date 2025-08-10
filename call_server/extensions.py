# define flask extensions in separate file, to resolve import dependencies

from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
# workaround to enable pool_pre_ping
# per https://github.com/pallets/flask-sqlalchemy/issues/589#issuecomment-361075700
class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        options["pool_pre_ping"] = True
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
db = SQLAlchemy()

from flask_caching import Cache
cache = Cache()

from flask_assets import Environment
assets = Environment()

from flask_babel import Babel
babel = Babel()

from flask_mail import Mail
mail = Mail()

from flask_login import LoginManager
login_manager = LoginManager()

# ``flask-restless`` depends on the deprecated ``url_quote_plus`` helper that
# was removed in Werkzeug 3. To maintain compatibility we reintroduce the
# function using :func:`urllib.parse.quote_plus` before importing
# ``flask_restless``.
import urllib.parse
import hmac
import json
import jinja2
from markupsafe import Markup
import flask
import flask.json as flask_json
import werkzeug
import werkzeug.security as _wz_security
from werkzeug import urls as _werkzeug_urls

# ---------------------------------------------------------------------------
# Compatibility shims for newer Flask/Werkzeug ecosystems.  Several of the
# pinned third-party dependencies import helpers that were removed in recent
# releases.  We provide stand-ins here so that those packages continue to work
# without modification.
# ---------------------------------------------------------------------------
if not hasattr(_werkzeug_urls, "url_quote_plus"):  # pragma: no cover
    _werkzeug_urls.url_quote_plus = urllib.parse.quote_plus

if not hasattr(_wz_security, "safe_str_cmp"):  # pragma: no cover
    _wz_security.safe_str_cmp = hmac.compare_digest

if not hasattr(werkzeug, "url_encode"):  # pragma: no cover
    werkzeug.url_encode = urllib.parse.urlencode

if not hasattr(werkzeug, "LocalProxy"):  # pragma: no cover
    from werkzeug.local import LocalProxy as _LocalProxy

    werkzeug.LocalProxy = _LocalProxy

if not hasattr(flask, "Markup"):  # pragma: no cover
    flask.Markup = Markup

if not hasattr(flask_json, "JSONEncoder"):  # pragma: no cover
    flask_json.JSONEncoder = json.JSONEncoder

if not hasattr(jinja2, "Markup"):  # pragma: no cover
    jinja2.Markup = Markup

from flask_restless import APIManager
rest = APIManager()

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

from flask_cors import CORS as cors

from flask_store import Store
store = Store()

from flask_rq2 import RQ
rq = RQ(default_timeout=60*60)

from flask_talisman import Talisman
CALLPOWER_CSP = {
    'default-src':'\'self\'',
    'script-src':['\'self\'', '\'unsafe-inline\'', '\'unsafe-eval\'', # for local scripts
        'cdnjs.cloudflare.com', 'ajax.cloudflare.com', 'media.twiliocdn.com',  # required for jquery, twilio
        'js-agent.newrelic.com', '*.nr-data.net'], # additional analytics platforms
    'style-src': ['\'self\'', '\'unsafe-inline\'', 'fonts.googleapis.com'], 
    'font-src': ['\'self\'', 'data:', 'fonts.gstatic.com'],
    'media-src': ['\'self\'', 'blob:', 'media.twiliocdn.com'],
    'connect-src': ['\'self\'', 'https://*.twilio.com', 'wss://*.twilio.com', 'media.twiliocdn.com', 'openstates.org'],
    'object-src': ['\'self\'', 'blob:'],
    'img-src': ['\'self\'', 'data:']
}
# unsafe-inline needed to render <script> tags without nonce
# unsafe-eval needed to run bootstrap templates
talisman = Talisman()

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
