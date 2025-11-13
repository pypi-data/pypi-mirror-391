import inngest
import inngest.django

from django_inngest.client import inngest_client
from django_inngest.defaults import (
    DJANGO_INNGEST_AUTO_DISCOVER_FUNCTIONS,
    DJANGO_INNGEST_INACTIVE_FUNCTION_IDS,
    DJANGO_INNGEST_SERVE_PATH,
)
from django_inngest.discovery import discover_inngest_functions

inactive_inngest_functions = []
if isinstance(DJANGO_INNGEST_INACTIVE_FUNCTION_IDS, list):
    inactive_inngest_functions.extend(DJANGO_INNGEST_INACTIVE_FUNCTION_IDS)

# Automatically discover all Inngest functions, excluding inactive ones
active_inngest_functions = []
if DJANGO_INNGEST_AUTO_DISCOVER_FUNCTIONS:
    active_inngest_functions.extend(
        discover_inngest_functions(inngest_client=inngest_client)
    )

DJANGO_INNGEST_SERVE_PATH = DJANGO_INNGEST_SERVE_PATH.rstrip("/").lstrip("/")

inngest_url = inngest.django.serve(
    inngest_client, active_inngest_functions, serve_path=DJANGO_INNGEST_SERVE_PATH
)
inngest_urls = [inngest_url]
