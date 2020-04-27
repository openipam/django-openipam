"""
Menu template tags, the following menu tags are available:

 * ``{% render_menu %}``
 * ``{% render_menu_item %}``
 * ``{% render_menu_css %}``

To load the menu tags in your templates: ``{% load admin_tools_menu_tags %}``.
"""

from django import template
from django.urls import reverse

from openipam.core.utils.menu_utils import get_admin_site_name, get_admin_menu
from openipam.core.models import Bookmark

register = template.Library()


@register.inclusion_tag("core/menu/bookmark.html", takes_context=True)
def render_bookmarks(context):
    bookmark = None
    url = context["request"].get_full_path()
    try:
        bookmark = Bookmark.objects.filter(user=context["request"].user, url=url)[0]
    except Exception:
        pass
    context.update({"bookmark": bookmark})
    return context


@register.inclusion_tag("core/menu/dummy.html", takes_context=True)
def render_menu(context, menu=None):
    """
    Template tag that renders the menu, it takes an optional ``Menu`` instance
    as unique argument, if not given, the menu will be retrieved with the
    ``get_admin_menu`` function.
    """
    if menu is None:
        menu = get_admin_menu(context)

    menu.init_with_context(context)
    context.update(
        {
            "template": menu.template,
            "menu": menu,
            "admin_url": reverse("%s:index" % get_admin_site_name(context)),
        }
    )
    return context


@register.inclusion_tag("core/menu/dummy.html", takes_context=True)
def render_menu_item(context, item, index=None):
    """
    Template tag that renders a given menu item, it takes a ``MenuItem``
    instance as unique parameter.
    """
    item.init_with_context(context)

    context.update(
        {
            "template": item.template,
            "item": item,
            "index": index,
            "selected": item.is_selected(context["request"]),
            "admin_url": reverse("%s:index" % get_admin_site_name(context)),
        }
    )
    return context


@register.inclusion_tag("core/menu/dummy.html", takes_context=True)
def render_menu_css(context, menu=None):
    """
    Template tag that renders the menu css files,, it takes an optional
    ``Menu`` instance as unique argument, if not given, the menu will be
    retrieved with the ``get_admin_menu`` function.
    """
    if menu is None:
        menu = get_admin_menu(context)

    context.update({"template": "core/menu/css.html", "css_files": menu.Media.css})
    return context
