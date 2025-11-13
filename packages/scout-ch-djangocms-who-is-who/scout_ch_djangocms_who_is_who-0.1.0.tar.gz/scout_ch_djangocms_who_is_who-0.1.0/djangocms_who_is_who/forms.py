from django import forms

from .models import WhoIsWhoPluginModel


class WhoIsWhoPluginForm(forms.ModelForm):
    class Meta:
        model = WhoIsWhoPluginModel
        fields = [
            "who_is_who_url",
            "locale",
            "midata_group_index",
            "use_auth",
            "auth_user",
            "auth_password",
        ]
        widgets = {
            "use_auth": forms.CheckboxInput(),
            "auth_password": forms.PasswordInput(),
        }
        help_texts = {
            "who_is_who_url": "Host URL",
            "locale": "Darstellungs Sprache",
            "midata_group_index": "Gruppen Index wie in der Midata Datenbank gespeichert. Muss eventuell via API request ausgelesen werden.",
            "auth_user": "Basic Auth Benutzer",
            "auth_password": "Basic Auth Passwort",
        }

    class Media:
        js = ("djangocms_who_is_who/js/toggle_password.js",)
