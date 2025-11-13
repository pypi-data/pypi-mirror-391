import requests
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from requests.auth import HTTPBasicAuth

from .forms import WhoIsWhoPluginForm
from .models import WhoIsWhoPluginModel


@plugin_pool.register_plugin
class WhoIsWhoPublisher(CMSPluginBase):
    model = WhoIsWhoPluginModel
    form = WhoIsWhoPluginForm
    module = _("WhoIsWho")
    name = _("WhoIsWho Plugin")
    render_template = "djangocms_who_is_who/djangocms_who_is_who.html.jinja"

    def render(self, context, instance, placeholder):
        try:
            if instance.who_is_who_url:
                self.update_content(instance)

        except requests.RequestException as e:
            # print error to dev console
            context.update({"error": str(e)})

        context.update(
            {
                "html_content": mark_safe(instance.cached_html),
                "stylesheet": mark_safe(instance.cached_stylesheet),
                "script": mark_safe(instance.cached_script),
            }
        )
        return context

    def update_content(self, instance):
        html_content = self.get_content(
            instance, route=f"html/{instance.locale}/{instance.midata_group_index}"
        )

        # Link images to api host and update the instance versions for html, css, js
        instance.cached_html = html_content.replace(
            "/api/image", instance.who_is_who_url + "image"
        )
        instance.cached_stylesheet = self.get_content(instance, "static/styles.css")
        instance.cached_script = self.get_content(instance, "static/script.js")

    def get_content(self, instance, route="", backend_prefix="/api/"):
        url = self.construct_url(instance.who_is_who_url, route, backend_prefix)

        if instance.use_auth:
            basic_auth = HTTPBasicAuth(instance.auth_user, instance.auth_password)
            res = requests.get(url, auth=basic_auth)
        else:
            res = requests.get(url)
        res.raise_for_status()
        return res.text

    def construct_url(self, url, route, prefix):
        # Ensure that the host URL does not end with a slash which would result in an invalid address
        if url[-1] == "/":
            url = url[:-1]
        return url + prefix + route
