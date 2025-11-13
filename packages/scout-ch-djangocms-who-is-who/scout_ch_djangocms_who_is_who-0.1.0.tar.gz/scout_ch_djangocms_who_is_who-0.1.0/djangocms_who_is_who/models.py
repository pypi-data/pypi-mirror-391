from cms.models import CMSPlugin
from django.db import models

LOCALES = {"de": "Deutsch", "it": "Italiano", "fr": "Français"}


class WhoIsWhoPluginModel(CMSPlugin):
    who_is_who_url = models.CharField(default="http://localhost:5173")
    locale = models.CharField(default="de", choices=LOCALES)
    midata_group_index = models.CharField(default="2")
    use_auth = models.BooleanField(default=False, blank=True)
    auth_user = models.CharField(default="", blank=True)
    auth_password = models.CharField(default="", blank=True)

    cached_html = models.TextField(default="")
    cached_stylesheet = models.TextField(default="")
    cached_script = models.TextField(default="")
