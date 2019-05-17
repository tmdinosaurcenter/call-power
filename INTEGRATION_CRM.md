CRM Integrations
===========

CallPower is designed to keep as little data as required to place calls connecting their members to targets. However, it can be useful for some organizations to track the duration of individual calls, to sign up users to a text list, or to identify conversations that may be useful for staff to follow-up.

An out-of-band sync system copies call information to a CRM, joining user records on their phone number or other unique ID, and storing the duration of the call, which target(s) they were connected to, and the overall status of their call session. Each campaign syncs on its own frequency (nightly, hourly, or immediately), specified in the 'Launch' page.

These jobs are run with redis and [rq](http://python-rq.org/docs/), and requires a scheduler and at least one worker process. 

Configuration
----

ActionKit

- `CRM_INTEGRATION=ActionKit`
- `ACTIONKIT_DOMAIN=client.actionkit.com`
- `ACTIONKIT_USER`
- `ACTIONKIT_PASSWORD` or `ACTIONKIT_API_KEY`

MobileCommons

- `CRM_INTEGRATION=MobileCommons`
- `MOBILE_COMMONS_USERNAME` email address of the API account
- `MOBILE_COMMONS_PASSWORD` password of the API account
- `MOBILE_COMMONS_COMPANY` required if If your account has multiple clients/affiliates or if your email is used in multiple company accounts. If unspecified we default to your firm.

Rogue

- `CRM_INTEGRATION=Rogue`
- `ROGUE_DOMAIN=importer.dosomething.org`
- `ROGUE_API_KEY`