from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib.admin.views.main import PAGE_VAR, ALL_VAR
from django.conf import settings
from django.template.loader import get_template

try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

from django.utils.http import urlunquote

from six import string_types

import re

register = template.Library()

CLASS_PATTERN = re.compile(r'\bclass="[\w\d]*"')
class_re = re.compile(r'(?<=class=["\'])(.*?)(?=["\'])')


@register.filter
def unquote_raw(value):
    return urlunquote(value)


@register.filter(is_safe=True)
def label_with_classes(field, arg):

    return field.label_tag(attrs={"class": arg})


@register.filter(is_safe=True)
def field_with_classes(value, arg):
    """
    Replace the attribute css class for Field 'value' with 'arg'.
    """
    attrs = value.field.widget.attrs
    orig = attrs["class"] if "class" in attrs else ""

    attrs["class"] = "%s %s" % (orig, arg)
    rendered = str(value)

    return rendered


@register.simple_tag
def atb_site_link():
    if hasattr(settings, "OPENIPAM_SITE_LINK"):
        return """
            <li><a href="%s"  class="top-icon" title="%s" rel="popover" data-placement="below"><i
                class="icon-home icon-white"></i></a></li>
                <li class="divider-vertical"></li>
            """ % (
            settings.OPENIPAM_SITE_LINK,
            _("Open site"),
        )
    else:
        return ""


@register.simple_tag
def atb_site_name():
    if hasattr(settings, "OPENIPAM_SITE_NAME"):
        return _(settings.OPENIPAM_SITE_NAME)
    else:
        return _("openIPAM")


@register.simple_tag
def bootstrap_page_url(cl, page_num):
    """
        generates page URL for given page_num, uses for prev and next links
        django numerates pages from 0
    """
    return escape(cl.get_query_string({PAGE_VAR: page_num - 1}))


DOT = "."


def bootstrap_paginator_number(cl, i, li_class=None):
    """
    Generates an individual page index link in a paginated list.
    """
    if i == DOT:
        return mark_safe("<li><a>...</a></li>")
    elif i == cl.page_num:
        return mark_safe('<li class="active"><a href="#">%d</a></li> ' % (i + 1))
    else:
        return mark_safe(
            '<li><a href="%s">%d</a></li>'
            % (escape(cl.get_query_string({PAGE_VAR: i})), i + 1)
        )


paginator_number = register.simple_tag(bootstrap_paginator_number)


def bootstrap_pagination(cl):
    """
    Generates the series of links to the pages in a paginated list.
    """
    paginator, page_num = cl.paginator, cl.page_num

    pagination_required = (not cl.show_all or not cl.can_show_all) and cl.multi_page
    if not pagination_required:
        page_range = []
    else:
        ON_EACH_SIDE = 3
        ON_ENDS = 2

        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if paginator.num_pages <= 10:
            page_range = list(range(paginator.num_pages))
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range.extend(list(range(0, ON_EACH_SIDE - 1)))
                page_range.append(DOT)
                page_range.extend(list(range(page_num - ON_EACH_SIDE, page_num + 1)))
            else:
                page_range.extend(list(range(0, page_num + 1)))
            if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(
                    list(range(page_num + 1, page_num + ON_EACH_SIDE + 1))
                )
                page_range.append(DOT)
                page_range.extend(
                    list(range(paginator.num_pages - ON_ENDS, paginator.num_pages))
                )
            else:
                page_range.extend(list(range(page_num + 1, paginator.num_pages)))

    need_show_all_link = cl.can_show_all and not cl.show_all and cl.multi_page
    return {
        "cl": cl,
        "pagination_required": pagination_required,
        "show_all_url": need_show_all_link and cl.get_query_string({ALL_VAR: ""}),
        "page_range": page_range,
        "ALL_VAR": ALL_VAR,
        "1": 1,
        "curr_page": cl.paginator.page(cl.page_num + 1),
    }


bootstrap_pagination = register.inclusion_tag("admin/pagination.html")(
    bootstrap_pagination
)


# breadcrumbs tag
class BreadcrumbsNode(template.Node):
    """
        renders bootstrap breadcrumbs list.
        usage::
            {% breadcrumbs %}
            url1|text1
            url2|text2
            text3
            {% endbreadcrumbs %}
        | is delimiter by default, you can use {% breadcrumbs delimiter_char %} to change it.
        lines without delimiters are interpreted as active breadcrumbs

    """

    def __init__(self, nodelist, delimiter):
        self.nodelist = nodelist
        self.delimiter = delimiter

    def render(self, context):
        data = self.nodelist.render(context).strip()

        if not data:
            return ""

        try:
            data.index('<div class="breadcrumbs">')
        except ValueError:
            lines = [
                x.strip().split(self.delimiter) for x in data.split("\n") if x.strip()
            ]
        else:
            # data is django-style breadcrumbs, parsing
            try:
                soup = BeautifulSoup(data)
                lines = [(a.get("href"), a.text) for a in soup.findAll("a")]
                lines.append([soup.find("div").text.split("&rsaquo;")[-1].strip()])
            except Exception as e:
                lines = [["Cannot parse breadcrumbs: %s" % str(e)]]

        out = '<ul class="breadcrumb">'
        curr = 0
        for d in lines:
            if len(d[0]) > 0:
                if d[0][0] == "*":
                    active = ' class="active"'
                    d[0] = d[0][1:]
                else:
                    active = ""

                curr += 1

                if len(d) == 2:
                    out += '<li%s><a href="%s">%s</a></li>' % (active, d[0], d[1])
                elif len(d) == 1:
                    out += "<li%s>%s</li>" % (active, d[0])
                else:
                    raise ValueError(
                        "Invalid breadcrumb line: %s" % self.delimiter.join(d)
                    )
        out += "</ul>"
        return out


@register.tag(name="breadcrumbs")
def do_breadcrumbs(parser, token):
    try:
        tag_name, delimiter = token.contents.split(None, 1)
    except ValueError:
        delimiter = "|"

    nodelist = parser.parse(("endbreadcrumbs",))
    parser.delete_first_token()

    return BreadcrumbsNode(nodelist, delimiter)


@register.simple_tag
def admin_select_filter(cl, spec):
    tpl = get_template(spec.template)
    query_string = cl.get_query_string(
        {}, [spec.parameter_name] if hasattr(spec, "parameter_name") else []
    )

    return tpl.render(
        {
            "title": spec.title,
            "choices": list(spec.choices(cl)),
            "query_string": query_string,
            "spec": spec,
        }
    )


@register.simple_tag
def admin_filter_selected(cl, spec):
    tpl = get_template("admin/filter_selected.html")
    value = None
    query_string_list = cl.get_query_string()[1:].split("&")
    href = None

    for index, choice in enumerate(spec.choices(cl)):
        if choice["selected"] is True and (
            index > 0 or isinstance(choice["display"], string_types)
        ):
            value = choice["display"]
            if hasattr(spec, "parameter_name"):
                param_name = spec.parameter_name
            elif hasattr(spec, "field_generic"):
                param_name = spec.field_generic
            else:
                param_name = spec.lookup_kwarg or None
            if param_name:
                href_list = list(query_string_list)
                for qs in href_list:
                    if qs.startswith(param_name):
                        query_string_list.remove(qs)
                href = "&".join(query_string_list)
            break

    return tpl.render({"title": spec.title.capitalize(), "value": value, "href": href})


@register.filter
def replace(string, args):
    search = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub(search, replace, string)
