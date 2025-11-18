from django.conf import settings
from django.contrib.sites.models import Site


def format_professional_url(path, schema="https"):
    site = Site.objects.get(id=settings.SITE_IDS["professional"])
    return f"{schema}://{site.domain}/{path}"
