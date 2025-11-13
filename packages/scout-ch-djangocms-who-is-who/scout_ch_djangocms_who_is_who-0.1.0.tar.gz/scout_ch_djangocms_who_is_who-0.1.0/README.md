# django CMS Who-Is-Who

**django CMS Who-Is-Who** allows users of a django CMS application to integrate the results of the [Who-Is-Who application](https://github.com/scout-ch/who-is-who) on an arbitrary webpage.

It serves soley as a connecting plugin and manages only the connection information required to load Who-Is-Who pages.

## Installation

- run `pip install scout-ch-djangocms-who-is-who`
- add `djangocms_who_is_who` to your `INSTALLED_APPS`
- run `python manage.py migrate djangocms_who_is_who`
