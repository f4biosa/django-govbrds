from math import floor
from urllib.parse import parse_qs, urlparse, urlunparse

from django import template
from django.contrib.messages import constants as message_constants
from django.template import Context
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from ..core import css_url, get_govbrds_setting, javascript_url, theme_url
from ..css import _css_class_list, merge_css_classes
from ..html import render_link_tag, render_script_tag


MESSAGE_ALERT_TYPES = {
    message_constants.DEBUG: "warning",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "danger",
}

register = template.Library()

@register.simple_tag
def govbrds_setting(value):
    """
    Return django-govbrds setting for use in in a template.

    Please consider this tag private, do not use it in your own templates.
    """
    return get_govbrds_setting(value)

@register.simple_tag
def govbrds_server_side_validation_class(widget):
    """
    Return server side validation class from a widget.

    Please consider this tag private, do not use it in your own templates.
    """
    try:
        css_classes = _css_class_list([widget["attrs"]["class"]])
    except KeyError:
        return ""
    return " ".join([css_class for css_class in css_classes if css_class in ["is-valid", "is-invalid"]])


@register.simple_tag
def govbrds_classes(*args):
    """
    Return list of classes.

    Please consider this filter private, do not use it in your own templates.
    """
    return merge_css_classes(*args)


@register.filter
def govbrds_message_alert_type(message):
    """Return the alert type for a message, defaults to `info`."""
    try:
        level = message.level
    except AttributeError:
        pass
    else:
        try:
            return MESSAGE_ALERT_TYPES[level]
        except KeyError:
            pass
    return "info"


@register.simple_tag
def govbrds_javascript_url():
    """
    Return the full url to the govbrds JavaScript library.

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        govbrds_javascript_url

    **Usage**::

        {% govbrds_javascript_url %}

    **Example**::

        {% govbrds_javascript_url %}
    """
    return javascript_url()


@register.simple_tag
def govbrds_css_url():
    """
    Return the full url to the govbrds CSS library.

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        govbrds_css_url

    **Usage**::

        {% govbrds_css_url %}

    **Example**::

        {% govbrds_css_url %}
    """
    return css_url()


@register.simple_tag
def govbrds_theme_url():
    """
    Return the full url to a govbrds theme CSS library.

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        govbrds_theme_url

    **Usage**::

        {% govbrds_theme_url %}

    **Example**::

        {% govbrds_theme_url %}
    """
    return theme_url()


@register.simple_tag
def govbrds_css():
    """
    Return HTML for govbrds CSS, or empty string if no CSS url is available.

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        govbrds_css

    **Usage**::

        {% govbrds_css %}

    **Example**::

        {% govbrds_css %}
    """
    rendered_urls = []
    if govbrds_css_url():
        rendered_urls.append(render_link_tag(govbrds_css_url()))
    if govbrds_theme_url():
        rendered_urls.append(render_link_tag(govbrds_theme_url()))
    return mark_safe("".join([url for url in rendered_urls]))


@register.simple_tag
def govbrds_javascript():
    """
    Return HTML for govbrds JavaScript, or empty string if no JavaScript URL is available.

    Adjust url in settings.
    If no url is returned, we don't want this statement to return any HTML. This is intended behavior.

    Default value: False

    This value is configurable, see Settings section. Note that any value that evaluates to True and is
    not "slim" will be interpreted as True.

    **Tag name**::

        govbrds_javascript

    **Usage**::

        {% govbrds_javascript %}

    **Example**::

        {% govbrds_javascript %}
    """
    # List of JS tags to include
    javascript_tags = []

    # govbrds JavaScript
    govbrds_js_url = govbrds_javascript_url()
    if govbrds_js_url:
        javascript_tags.append(render_script_tag(govbrds_js_url))

    # Join and return
    return mark_safe("\n".join(javascript_tags))


@register.simple_tag
def govbrds_formset(formset, **kwargs):
    """
    Render a formset.

    **Tag name**::

        govbrds_formset

    **Parameters**::

        formset
            The formset that is being rendered


        See govbrds_field_ for other arguments

    **Usage**::

        {% govbrds_formset formset %}

    **Example**::

        {% govbrds_formset formset layout='horizontal' %}
    """
    return render_formset(formset, **kwargs)


@register.simple_tag
def govbrds_formset_errors(formset, **kwargs):
    """
    Render formset errors.

    **Tag name**::

        govbrds_formset_errors

    **Parameters**::

        formset
            The formset that is being rendered

        layout
            Context value that is available in the template ``django_govbrds5/form_errors.html`` as ``layout``.

    **Usage**::

        {% govbrds_formset_errors formset %}

    **Example**::

        {% govbrds_formset_errors formset layout='inline' %}
    """
    return render_formset_errors(formset, **kwargs)


@register.simple_tag
def govbrds_form(form, **kwargs):
    """
    Render a form.

    **Tag name**::

        govbrds_form

    **Parameters**::

        form
            The form that is to be rendered

        exclude
            A list of field names (comma separated) that should not be rendered
            E.g. exclude=subject,bcc

        alert_error_type
            Control which type of errors should be rendered in global form alert.

                One of the following values:

                    * ``'all'``
                    * ``'fields'``
                    * ``'non_fields'``

                :default: ``'non_fields'``

        See govbrds_field_ for other arguments

    **Usage**::

        {% govbrds_form form %}

    **Example**::

        {% govbrds_form form layout='inline' %}
    """
    return render_form(form, **kwargs)


@register.simple_tag
def govbrds_form_errors(form, **kwargs):
    """
    Render form errors.

    **Tag name**::

        govbrds_form_errors

    **Parameters**::

        form
            The form that is to be rendered

        type
            Control which type of errors should be rendered.

            One of the following values:

                * ``'all'``
                * ``'fields'``
                * ``'non_fields'``

            :default: ``'all'``

        layout
            Context value that is available in the template ``django_govbrds5/form_errors.html`` as ``layout``.

    **Usage**::

        {% govbrds_form_errors form %}

    **Example**::

        {% govbrds_form_errors form layout='inline' %}
    """
    return render_form_errors(form, **kwargs)


@register.simple_tag
def govbrds_field(field, **kwargs):
    """
    Render a field.

    **Tag name**::

        govbrds_field

    **Parameters**::


        field
            The form field to be rendered

        layout
            If set to ``'horizontal'`` then the field and label will be rendered side-by-side.
            If set to ``'floating'`` then support widgets will use floating labels.
            Layout set in ``'govbrds_form'`` takes precedence over layout set in ``'govbrds_formset'``.
            Layout set in ``'govbrds_field'`` takes precedence over layout set in ``'govbrds_form'``.

        wrapper_class
            CSS class of the ``div`` that wraps the field and label.

            :default: ``'mb-3'``

        field_class
            CSS class of the ``div`` that wraps the field.

        label_class
            CSS class of the ``label`` element. Will always have ``control-label`` as the last CSS class.

        show_help
            Show the field's help text, if the field has help text.

            :default: ``True``

        show_label
            Whether the show the label of the field.

                * ``True``
                * ``False``/``'visually-hidden'``
                * ``'skip'``

            :default: ``True``

        exclude
            A list of field names that should not be rendered

        size
            Controls the size of the rendered ``div.row`` through the use of CSS classes.

            One of the following values:

                * ``'small'``
                * ``'medium'``
                * ``'large'``

        placeholder
            Sets the placeholder text of a textbox

        horizontal_label_class
            Class used on the label when the ``layout`` is set to ``horizontal``.

            :default: ``'col-md-3'``. Can be changed in :doc:`settings`

        horizontal_field_class
            Class used on the field when the ``layout`` is set to ``horizontal``.

            :default: ``'col-md-9'``. Can be changed in :doc:`settings`

        addon_before
            Text that should be prepended to the form field. Can also be an icon, e.g.
            ``'<span class="glyphicon glyphicon-calendar"></span>'``

            See the `govbrds docs <http://getgovbrds.com/components/#input-groups-basic>` for more examples.

        addon_after
            Text that should be appended to the form field. Can also be an icon, e.g.
            ``'<span class="glyphicon glyphicon-calendar"></span>'``

            See the `govbrds docs <http://getgovbrds.com/components/#input-groups-basic>` for more examples.

        addon_before_class
            Class used on the span when ``addon_before`` is used.

            One of the following values:

                * ``'input-group-text'``
                * ``None``

            Set to None to disable the span inside the addon. (for use with buttons)

            :default: ``input-group-text``

        addon_after_class
            Class used on the span when ``addon_after`` is used.

            One of the following values:

                * ``'input-group-text'``
                * ``None``

            Set to None to disable the span inside the addon. (for use with buttons)

            :default: ``input-group-text``

        error_css_class
            CSS class used when the field has an error

            :default: ``'has-error'``. Can be changed :doc:`settings`

        required_css_class
            CSS class used on the ``div.row`` to indicate a field is required

            :default: ``''``. Can be changed :doc:`settings`

        success_css_class
            CSS class used when the field has valid data

            :default: ``'has-success'``. Can be changed :doc:`settings`

    **Usage**::

        {% govbrds_field field %}

    **Example**::

        {% govbrds_field field show_label=False %}
    """
    return render_field(field, **kwargs)


@register.simple_tag
def govbrds_label(content, **kwargs):
    """
    Render a label.

    **Tag name**::

        govbrds_label

    **Parameters**::

        content
            The label's text

        label_for
            The value that will be in the ``for`` attribute of the rendered ``<label>``

        label_class
            The CSS class for the rendered ``<label>``

        label_title
            The value that will be in the ``title`` attribute of the rendered ``<label>``

    **Usage**::

        {% govbrds_label content %}

    **Example**::

        {% govbrds_label "Email address" label_for="exampleInputEmail1" %}
    """
    return render_label(content, **kwargs)


@register.simple_tag
def govbrds_button(content, **kwargs):
    """
    Render a button.

    **Tag name**::

        govbrds_button

    **Parameters**::

        content
            The text to be displayed in the button

        button_type
            Optional field defining what type of button this is.

            Accepts one of the following values:

                * ``'submit'``
                * ``'reset'``
                * ``'button'``
                * ``'link'``

        button_class
            The class of button to use. If none is given, btn-primary will be used.

        extra_classes
            Any extra CSS classes that should be added to the button.

        size
            Optional field to control the size of the button.

            Accepts one of the following values:

                * ``'sm'``
                * ``'md'`` (default)
                * ``'lg'``

        href
            Render the button as an ``<a>`` element. The ``href`` attribute is set with this value.
            If a ``button_type`` other than ``link`` is defined, specifying a ``href`` will throw a
            ``ValueError`` exception.

        name
            Value of the ``name`` attribute of the rendered element.

        value
            Value of the ``value`` attribute of the rendered element.

        **kwargs
            All other keywords arguments will be passed on as HTML attributes.

    **Usage**::

        {% govbrds_button content %}

    **Example**::

        {% govbrds_button "Save" button_type="submit" button_class="btn-primary" %}
    """
    return render_button(content, **kwargs)


@register.simple_tag
def govbrds_alert(content, **kwargs):
    """
    Render an alert.

    **Tag name**::

        govbrds_alert

    **Parameters**::

        content
            HTML content of alert

        alert_type
            * ``'info'``
            * ``'warning'``
            * ``'danger'``
            * ``'success'``

            :default: ``'info'``

        dismissible
            boolean, is alert dismissible

            :default: ``True``

        extra_classes
            string, extra CSS classes for alert

            :default: ""

    **Usage**::

        {% govbrds_alert content %}

    **Example**::

        {% govbrds_alert "Something went wrong" alert_type="error" %}
    """
    return render_alert(content, **kwargs)


@register.simple_tag(takes_context=True)
def govbrds_messages(context):
    """
    Show django.contrib.messages Messages in govbrds alert containers.

    Uses the template ``django_govbrds5/messages.html``.

    **Tag name**::

        govbrds_messages

    **Parameters**::

        None.

    **Usage**::

        {% govbrds_messages %}

    **Example**::

        {% govbrds_messages %}
    """
    if isinstance(context, Context):
        context = context.flatten()
    context.update({"message_constants": message_constants})
    return render_template_file("django_govbrds5/messages.html", context=context)


@register.inclusion_tag("django_govbrds5/pagination.html")
def govbrds_pagination(page, **kwargs):
    """
    Render pagination for a page.

    **Tag name**::

        govbrds_pagination

    **Parameters**::

        page
            The page of results to show.

        pages_to_show
            Number of pages in total

            :default: ``11``

        url
            URL to navigate to for pagination forward and pagination back.

            :default: ``None``

        size
            Controls the size of the pagination through CSS. Defaults to being normal sized.

            One of the following:

                * ``'small'``
                * ``'large'``

            :default: ``None``

        justify_content
            Controls the alignment of the pagination through CSS. Defaults to no alignment.

            One of the following:

                * ``'start'``
                * ``'center'``
                * ``'end'``

            :default: ``None``

        extra
            Any extra page parameters.

            :default: ``None``

        parameter_name
            Name of the paging URL parameter.

            :default: ``'page'``

    **Usage**::

        {% govbrds_pagination page %}

    **Example**::

        {% govbrds_pagination lines url="/pagination?page=1" size="large" %}
    """
    pagination_kwargs = kwargs.copy()
    pagination_kwargs["page"] = page
    return get_pagination_context(**pagination_kwargs)


@register.simple_tag
def govbrds_url_replace_param(url, name, value):
    return url_replace_param(url, name, value)


def get_pagination_context(
    page,
    *,
    pages_to_show=11,
    url=None,
    size=None,
    justify_content=None,
    extra=None,
    parameter_name="page",
):
    """Generate govbrds pagination context from a page object."""
    pages_to_show = int(pages_to_show)
    if pages_to_show < 1:
        raise ValueError(f"Pagination pages_to_show should be a positive integer, you specified {pages_to_show}.")

    num_pages = page.paginator.num_pages
    current_page = page.number

    delta_pages = int(floor(pages_to_show / 2))

    first_page = max(1, current_page - delta_pages)
    pages_back = max(1, first_page - delta_pages) if first_page > 1 else None

    last_page = first_page + pages_to_show - 1
    if pages_back is None:
        last_page += 1
    if last_page > num_pages:
        last_page = num_pages

    if last_page < num_pages:
        pages_forward = min(last_page + delta_pages, num_pages)
    else:
        pages_forward = None
        if first_page > 1:
            first_page -= 1
        if pages_back is not None and pages_back > 1:
            pages_back -= 1
        else:
            pages_back = None

    pages_shown = []
    for i in range(first_page, last_page + 1):
        pages_shown.append(i)

    parts = urlparse(url or "")
    params = parse_qs(parts.query)
    if extra:
        params.update(parse_qs(extra))
    url = urlunparse(
        [
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            urlencode(params, doseq=True),
            parts.fragment,
        ]
    )

    pagination_css_classes = ["pagination"]
    if size:
        pagination_size_class = get_size_class(size, prefix="pagination", skip="md")
        if pagination_size_class:
            pagination_css_classes.append(pagination_size_class)

    if justify_content:
        if justify_content in ["start", "center", "end"]:
            pagination_css_classes.append(f"justify-content-{justify_content}")
        else:
            raise ValueError(
                f"Invalid value '{justify_content}' for pagination justification."
                " Valid values are 'start', 'center', 'end'."
            )

    return {
        "govbrds_pagination_url": url,
        "num_pages": num_pages,
        "current_page": current_page,
        "first_page": first_page,
        "last_page": last_page,
        "pages_shown": pages_shown,
        "pages_back": pages_back,
        "pages_forward": pages_forward,
        "pagination_css_classes": " ".join(pagination_css_classes),
        "parameter_name": parameter_name,
    }
