from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.utils.http import urlunquote
from django.utils import timezone
from django.contrib.auth.decorators import permission_required

from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.utils import DatabaseError

from openipam.core.views import BaseDatatableView
from openipam.conf.ipam_settings import CONFIG
from openipam.user.forms import GroupForm, UserObjectPermissionForm
from openipam.user import actions as user_actions

from braces.views import PermissionRequiredMixin

from guardian.models import UserObjectPermission, GroupObjectPermission

User = get_user_model()


class UserManagerJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = "user.view_user"

    order_columns = (
        "pk",
        "username",
        "last_name",
        "email",
        # 'groups__nmae',
        # 'permissions__name',
        "is_staff",
        "is_superuser",
        "is_ipamadmin",
        "source__name",
        "last_login",
    )

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 3000

    def get_initial_queryset(self):
        qs = User.objects.select_related("source").all()
        return qs

    def filter_queryset(self, qs):
        # use request parameters to filter queryset
        column_data = self.json_data.get("columns", [])

        try:
            username_search = column_data[1]["search"]["value"].strip()
            fullname_search = column_data[2]["search"]["value"].strip()
            email_search = column_data[3]["search"]["value"].strip()
            staff_search = column_data[4]["search"]["value"].strip()
            super_search = column_data[5]["search"]["value"].strip()
            ipam_admin_search = column_data[6]["search"]["value"].strip()
            source_search = column_data[7]["search"]["value"].strip()
            search = self.json_data.get("search_filter", "").strip()
            search_list = search.strip().split(",") if search else []

            for search_item in search_list:
                search_str = "".join(search_item.split(":")[1:])
                if search_item.startswith("user:") and search_str:
                    qs = qs.filter(username=search_item[5:])
                elif search_item.startswith("group:"):
                    qs = qs.filter(groups__name=search_item[6:])
                elif search_item.startswith("gperm:"):
                    qs = qs.filter(groups__groupobjectpermission__pk=search_item[6:])
                elif search_item.startswith("uperm:"):
                    qs = qs.filter(userobjectpermission__pk=search_item[6:])

            if username_search:
                qs = qs.filter(username__istartswith=username_search)
            if fullname_search:
                qs = qs.filter(
                    Q(first_name__icontains=fullname_search)
                    | Q(last_name__icontains=fullname_search)
                )
            if email_search:
                qs = qs.filter(email__icontains=email_search)
            if staff_search:
                qs = qs.filter(is_staff=True if staff_search == "1" else False)
            if super_search:
                qs = qs.filter(is_superuser=True if super_search == "1" else False)
            if ipam_admin_search:
                if ipam_admin_search == "1":
                    qs = qs.filter(
                        Q(is_superuser=True) | Q(groups__name=CONFIG.get("ADMIN_GROUP"))
                    ).distinct()
                else:
                    qs = qs.filter(is_superuser=False).exclude(
                        groups__name=CONFIG.get("ADMIN_GROUP")
                    )
            if source_search:
                qs = qs.filter(
                    source__name="INTERNAL" if source_search == "1" else "LDAP"
                )

        except (DatabaseError, ValidationError):
            pass

        return qs

    def raw_ordering(self):
        order_columns = ("hosts.mac", "hosts.hostname", "hosts.mac", "hosts.expires")

        # Number of columns that are used in sorting
        order_data = self.json_data.get("order", [])

        order = []
        for item in order_data:
            column = item["column"]
            column_dir = item["dir"]
            sdir = "DESC" if column_dir == "desc" else "ASC"
            sortcol = order_columns[column]
            order.append("%s %s" % (sortcol, sdir))

        if order:
            return ",".join(order)
        else:
            return "hosts.hostname"

    def prepare_results(self, qs):
        def boolean_img(_bool):
            if _bool:
                return '<img src="/static/admin/img/icon-yes.svg" alt="True">'
            else:
                return '<img src="/static/admin/img/icon-no.svg" alt="False">'

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for user in qs:
            json_data.append(
                [
                    '<input class="action-select" name="selected_users" type="checkbox" value="%s" />'
                    % user.pk
                    if self.request.user.is_superuser
                    else "",
                    '<a class="user-details" href="user/%s">%s</a>'
                    % (user.pk, user.username),
                    user.get_full_name() if user.first_name or user.last_name else "",
                    user.email,
                    # '<a href="#" class="group-href" rel="%s">Groups</a>' % user.pk,
                    # '<a href="#" class="perm-href" rel="%s">Permissions</a>' % user.pk,
                    boolean_img(user.is_staff),
                    boolean_img(user.is_superuser),
                    boolean_img(user.is_ipamadmin),
                    user.source.name if user.source else "",
                    timezone.localtime(user.last_login).strftime("%Y-%m-%d %I:%M %p")
                    if user.last_login
                    else None,
                    user.last_login,
                ]
            )
        return json_data


class UserManagerView(PermissionRequiredMixin, TemplateView):
    permission_required = "user.view_user"
    template_name = "admin/user/manager.html"

    def get_context_data(self, **kwargs):
        context = super(UserManagerView, self).get_context_data(**kwargs)
        search_filter = self.request.COOKIES.get("search_filter")
        search_filter = urlunquote(search_filter).split(",") if search_filter else []
        context["search_filter"] = search_filter
        context["group_form"] = GroupForm()
        context["user_permission_form"] = UserObjectPermissionForm()

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(UserManagerView, self).dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", None)
        selected_users = request.POST.getlist("selected_users", [])

        if selected_users:
            selected_users = User.objects.filter(pk__in=selected_users)

            if action:
                getattr(user_actions, "action_%s" % action)(request, selected_users)

        return redirect("core:users:user_manager")


@permission_required("user.view_user")
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    groups = user.groups.all()
    user_object_permissions = UserObjectPermission.objects.select_related(
        "permission", "content_type"
    ).filter(user=user)
    group_object_permissions = GroupObjectPermission.objects.select_related(
        "permission", "group", "content_type"
    ).filter(group__in=groups)

    context = {
        "user": user,
        "groups": groups,
        "user_object_permissions": user_object_permissions,
        "group_object_permissions": group_object_permissions,
        "img_yes": '<img src="/static/admin/img/icon-yes.svg" alt="True">',
        "img_no": '<img src="/static/admin/img/icon-no.svg" alt="False">',
    }

    return render(request, "admin/user/user_detail.html", context)


def user_permissions(request):
    pass


def user_groups(request):
    pass
