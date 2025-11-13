import logging

import inngest

from django_inngest.defaults import (
    DJANGO_INNGEST_API_BASE_URL,
    DJANGO_INNGEST_APP_ID,
    DJANGO_INNGEST_CLIENT_LOGGER,
    DJANGO_INNGEST_IS_PRODUCTION,
    INNGEST_EVENT_KEY,
    INNGEST_SIGNING_KEY,
)

# Create an Inngest client

client_config = {
    "app_id": DJANGO_INNGEST_APP_ID or "unset-django-inngest-app-id",
    "is_production": DJANGO_INNGEST_IS_PRODUCTION,
    "api_base_url": DJANGO_INNGEST_API_BASE_URL,
}

# Only add event_key and signing_key in production
if DJANGO_INNGEST_IS_PRODUCTION:
    if INNGEST_EVENT_KEY:
        client_config["event_key"] = INNGEST_EVENT_KEY
    if INNGEST_SIGNING_KEY:
        client_config["signing_key"] = INNGEST_SIGNING_KEY

if DJANGO_INNGEST_CLIENT_LOGGER:
    client_config["logger"] = logging.getLogger(DJANGO_INNGEST_CLIENT_LOGGER)

inngest_client = inngest.Inngest(**client_config)
