from importlib import import_module

from django.conf import settings

GOVBRDS = {"foo": "bar"}
GOVBRDS_DEFAULTS = {
    "css_url": {
        "url": "govbrds3/css/style.min.css",
    },
    "javascript_url": {
        "url": "govbrds3/js/script.js",
    },
    "theme_url": None,
    "color_mode": None,
    "javascript_in_head": False,
    "wrapper_class": "mb-3",
    "inline_wrapper_class": "",
    "horizontal_label_class": "col-sm-2",
    "horizontal_field_class": "col-sm-10",
    "horizontal_field_offset_class": "offset-sm-2",
    "set_placeholder": True,
    "checkbox_layout": None,
    "checkbox_style": None,
    "required_css_class": "",
    "error_css_class": "",
    "success_css_class": "",
    "server_side_validation": True,
    "formset_renderers": {"default": "django_govbrds.renderers.FormsetRenderer"},
    "form_renderers": {"default": "django_govbrds.renderers.FormRenderer"},
    "field_renderers": {
        "default": "django_govbrds.renderers.FieldRenderer",
    },
}


def get_govbrds_setting(name, default=None):
    """
    Read a setting.

    Lookup order is:

    1. Django settings
    2. `django-govbrds` defaults
    3. Given default value
    """
    govbrds_settings = getattr(settings, "GOVBRDS", {})
    return govbrds_settings.get(name, GOVBRDS_DEFAULTS.get(name, default))


def javascript_url():
    """Return the full url to the GovBR-DS JavaScript file."""
    return get_govbrds_setting("javascript_url")


def css_url():
    """Return the full url to the GovBR-DS CSS file."""
    return get_govbrds_setting("css_url")


def theme_url():
    """Return the full url to the theme CSS file."""
    return get_govbrds_setting("theme_url")


def get_renderer(renderers, **kwargs):
    layout = kwargs.get("layout", "")
    path = renderers.get(layout, renderers["default"])
    mod, cls = path.rsplit(".", 1)
    return getattr(import_module(mod), cls)


def get_formset_renderer(**kwargs):
    renderers = get_govbrds_setting("formset_renderers")
    return get_renderer(renderers, **kwargs)


def get_form_renderer(**kwargs):
    renderers = get_govbrds_setting("form_renderers")
    return get_renderer(renderers, **kwargs)


def get_field_renderer(**kwargs):
    renderers = get_govbrds_setting("field_renderers")
    return get_renderer(renderers, **kwargs)
