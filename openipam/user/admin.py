from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import Group as AuthGroup, Permission as AuthPermission
from django.contrib.admin import SimpleListFilter, ListFilter
from django.utils.encoding import force_text
from django.urls import path
from django.db.models import Q
from django.shortcuts import redirect, render, reverse
from django.contrib import messages
from django.forms import modelform_factory

from openipam.dns.models import Domain
from openipam.hosts.models import Host
from openipam.network.models import Network
from openipam.user.models import User, GroupSource, AuthSource
from openipam.user.forms import (
    AuthUserCreateAdminForm,
    AuthUserChangeAdminForm,
    AuthGroupAdminForm,
    UserObjectPermissionAdminForm,
    GroupObjectPermissionAdminForm,
)

from guardian.models import UserObjectPermission, GroupObjectPermission

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin

from dal import autocomplete


class IPAMAdminFilter(SimpleListFilter):
    title = "IPAM admin status"
    parameter_name = "ipamadmin"

    def lookups(self, request, model_admin):
        return (("1", "Yes"), ("0", "No"))

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == "1":
                queryset = queryset.filter(groups__name="ipam-admins")
            elif self.value() == "0":
                queryset = queryset.exclude(groups__name="ipam-admins")

        return queryset


class IPAMGroupFilter(ListFilter):
    title = "groups"
    parameter_name = "groups"
    template = "admin/filter_autocomplete.html"
    autocomplete_url = "/api/web/GroupAutocomplete/"
    placeholder = "Search Groups"

    def has_output(self):
        """
        Returns True if some choices would be output for this filter.
        """
        return True

    def choices(self, cl):
        """
        Returns choices ready to be output in the template.
        """
        if getattr(self, "value", None):
            group = AuthGroup.objects.filter(pk=self.value).first()

            if group:
                return [
                    {
                        "selected": True,
                        "query_string": cl.get_query_string({}, [self.parameter_name]),
                        "display": group.name,
                        "value": group.pk,
                    }
                ]

        return []

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return [self.parameter_name]

    def queryset(self, request, queryset):
        value = request.GET.get(self.parameter_name, "")

        if value:
            self.value = value
            queryset = queryset.filter(**{"%s__pk" % self.parameter_name: value})
        return queryset


class IPAMObjGroupFilter(IPAMGroupFilter):
    parameter_name = "group"


class IPAMUserFilter(ListFilter):
    title = "users"
    parameter_name = "users"
    template = "admin/filter_autocomplete.html"
    autocomplete_url = "/api/web/UserAutocomplete/"
    placeholder = "Search Users"

    def has_output(self):
        """
        Returns True if some choices would be output for this filter.
        """
        return True

    def choices(self, cl):
        """
        Returns choices ready to be output in the template.
        """
        if getattr(self, "value", None):
            user = User.objects.filter(pk=self.value).first()

            if user:
                return [
                    {
                        "selected": True,
                        "query_string": cl.get_query_string({}, [self.parameter_name]),
                        "display": user.username,
                        "value": user.username,
                    }
                ]

        return []

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return [self.parameter_name]

    def queryset(self, request, queryset):
        value = request.GET.get(self.parameter_name, "")

        if value:
            self.value = value
            queryset = queryset.filter(**{"%s__pk" % self.parameter_name: value})
        return queryset


class GroupSourceFilter(SimpleListFilter):
    title = "Group Source"
    parameter_name = "source"

    def lookups(self, request, model_admin):
        return [(source.pk, source.name) for source in AuthSource.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(
                source__source=AuthSource.objects.get(pk=self.value())
            )

        return queryset


class IPAMGroupHasPermissionsFilter(SimpleListFilter):
    title = "Has Permissions"
    parameter_name = "permissions"

    def lookups(self, request, model_admin):
        return (("1", "Yes"), ("2", "No"))

    def queryset(self, request, queryset):
        if self.value() == "1":
            queryset = queryset.filter(
                Q(permissions__isnull=False) | Q(groupobjectpermission__isnull=False)
            )

        return queryset

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == force_text(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, []
                ),
                "display": str(title),
            }


class IPAMObjUserFilter(IPAMUserFilter):
    parameter_name = "user"


class AuthUserChangeList(ChangeList):
    def get_queryset(self, request):
        qs = super(AuthUserChangeList, self).get_queryset(request)
        if not len(request.GET):
            qs = qs.filter(last_login__gte="1970-01-01")
        return qs


class AuthUserAdmin(UserAdmin):
    add_form = AuthUserCreateAdminForm
    form = AuthUserChangeAdminForm
    list_display = (
        "username",
        "full_name",
        "email",
        "permissions",
        "is_staff",
        "is_superuser",
        "is_ipamadmin",
        "last_login",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        IPAMAdminFilter,
        IPAMGroupFilter,
        "last_login",
    )
    ordering = ("-last_login",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined"), "classes": ("collapse",)},
        ),
    )

    def permissions(self, obj):
        return '<a href="%s">Permissions</a>' % reverse(
            "admin:user_perms_view", args=[obj.pk]
        )

    permissions.allow_tags = True

    def full_name(self, obj):
        first_name = "" if obj.first_name is None else obj.first_name
        last_name = "" if obj.last_name is None else obj.last_name
        return "%s %s" % (first_name, last_name)

    full_name.admin_order_field = "last_name"

    def is_ipamadmin(self, obj):
        return obj.is_ipamadmin

    is_ipamadmin.short_description = "IPAM Admin Status"
    is_ipamadmin.boolean = True

    # Hide Guardian User
    def get_queryset(self, request):
        return super(AuthUserAdmin, self).get_queryset(request).exclude(pk=-1)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        try:
            obj_id = int(object_id)
        except Exception:
            raise Http404

        user_add_form = UserObjectPermissionAdminForm(
            request.POST or None, initial={"user": obj_id}
        )

        if user_add_form.is_valid():
            instance = user_add_form.save(commit=False)
            content_object = user_add_form.cleaned_data["object_id"].split("-")
            instance.content_type_id = content_object[0]
            instance.object_pk = content_object[1]
            try:
                instance.save()
            except ValidationError as e:
                messages.error(request, "There was an error saving: %s" % e)

            return redirect("admin:user_user_change", object_id)

        user_object_permissions = UserObjectPermission.objects.prefetch_related(
            "permission"
        ).filter(user__pk=object_id)
        host_permissions = user_object_permissions.filter(content_type__model="host")
        domain_permissions = user_object_permissions.filter(
            content_type__model="domain"
        )
        # Prefetch related doesn't seem to work here.
        network_permissions = UserObjectPermission.objects.filter(
            user__pk=object_id, content_type__model="network"
        )

        extra_context = {
            "group_object_permissions": user_object_permissions,
            "host_permissions": host_permissions,
            "domain_permissions": domain_permissions,
            "network_permissions": network_permissions,
            "user_add_form": user_add_form,
        }
        return super(AuthUserAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def get_urls(self):
        urls = super(AuthUserAdmin, self).get_urls()
        new_urls = [
            path(
                "perm_delete/<int:user>/$",
                self.admin_site.admin_view(self.delete_perm_view),
                name="user_perm_delete",
            ),
            path(
                "permissions/<int:user>/$",
                self.admin_site.admin_view(self.user_perms_view),
                name="user_perms_view",
            ),
        ]
        return new_urls + urls

    def delete_perm_view(self, request, permid):
        next = request.GET.get("next")
        UserObjectPermission.objects.get(pk=permid).delete()
        return redirect(next)

    def user_perms_view(self, request, userid):
        user = User.objects.get(pk=userid)
        groups = user.groups.all()

        context = {
            "user": user,
            "groups": groups,
            "user_permissions": UserObjectPermission.objects.prefetch_related(
                "permission", "content_type", "content_object"
            ).filter(user__pk=userid),
            "group_permission": GroupObjectPermission.objects.filter(group__in=groups),
        }
        return render(request, "admin/user/user/permissions.html", context)


class TokenAdmin(TokenAdmin):
    form = modelform_factory(
        Token,
        fields=("user",),
        widgets={
            "user": autocomplete.ModelSelect2(url="core:autocomplete:user_autocomplete")
        },
    )


class AuthGroupSourceInline(admin.StackedInline):
    model = GroupSource


class AuthGroupAdmin(GroupAdmin):
    list_display = ("name", "authsources")
    list_filter = (IPAMObjUserFilter, GroupSourceFilter, IPAMGroupHasPermissionsFilter)
    form = AuthGroupAdminForm
    list_select_related = True
    inlines = [AuthGroupSourceInline]
    actions = ["change_source_internal", "change_source_ldap"]
    ordering = ("source__source", "name")

    def get_queryset(self, request):
        qs = super(AuthGroupAdmin, self).get_queryset(request)
        return qs.select_related("source__source").distinct()

    def changelist_view(self, request, extra_context=None):
        permission_param = request.GET.get("permissions", "")
        q = request.GET.get("q", "")
        if not q and not permission_param:
            return redirect(reverse("admin:auth_group_changelist") + "?permissions=1")

        return super(AuthGroupAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        group_object_permissions = GroupObjectPermission.objects.filter(
            group__pk=object_id
        )
        host_permissions = group_object_permissions.filter(content_type__model="host")
        domain_permissions = group_object_permissions.filter(
            content_type__model="domain"
        )
        # Prefetch related doesn't seem to work here.
        network_permissions = GroupObjectPermission.objects.filter(
            group__pk=object_id, content_type__model="network"
        )

        extra_context = {
            "group_object_permissions": group_object_permissions,
            "host_permissions": host_permissions,
            "domain_permissions": domain_permissions,
            "network_permissions": network_permissions,
        }
        return super(AuthGroupAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def get_urls(self):
        urls = super(AuthGroupAdmin, self).get_urls()
        new_urls = [
            path(
                "perm_delete/<int:group>/$",
                self.admin_site.admin_view(self.delete_perm_view),
                name="auth_group_perm_delete",
            )
        ]
        return new_urls + urls

    def delete_perm_view(self, request, permid):
        next = request.GET.get("next")
        GroupObjectPermission.objects.get(pk=permid).delete()
        return redirect(next)

    def authsources(self, obj):
        return "%s" % (obj.source)

    authsources.short_description = "Source"
    authsources.admin_order_field = "source__source"

    def change_source_internal(self, request, queryset):
        source = AuthSource.objects.get(name="INTERNAL")
        for group in queryset:
            group.source.source = source
            group.source.save()

    change_source_internal.description = "Change Group Source to INTERNAL"

    def change_source_ldap(self, request, queryset):
        source = AuthSource.objects.get(name="LDAP")
        for group in queryset:
            group.source.source = source
            group.source.save()

    change_source_ldap.description = "Change Group Source to LDAP"


class AuthPermissionAdmin(admin.ModelAdmin):
    list_filter = ("content_type__app_label", "codename", "content_type__model")
    list_select_related = True
    search_fields = ("name", "codename")


class ObjectPermissionFilter(SimpleListFilter):
    title = "permission"
    parameter_name = "permission"

    def lookups(self, request, model_admin):
        permissions = AuthPermission.objects.select_related().filter(
            Q(codename__icontains="is_owner") | Q(codename__icontains="add_records_to")
        )
        permisssion_filters = [
            (permission.id, permission.codename) for permission in permissions
        ]

        return tuple(permisssion_filters)

    def queryset(self, request, queryset):
        if self.value():
            permission = AuthPermission.objects.get(id=self.value())
            queryset = queryset.filter(permission=permission)

        return queryset


class ObjectPermissionSearchChangeList(ChangeList):
    "Changelist to do advanced object perms search"

    def get_query_set(self, request):
        search_qs = request.GET.get("q", "")
        term = search_qs.split(":")[-1]
        if search_qs.startswith("domain:") and term:
            domains = [
                domain.pk for domain in Domain.objects.filter(name__istartswith=term)
            ]
            qs = self.root_queryset.filter(
                object_pk__in=domains, content_type__name="domain"
            )
        elif search_qs.startswith("host:") and term:
            hosts = [
                host.pk for host in Host.objects.filter(hostname__istartswith=term)
            ]
            qs = self.root_queryset.filter(
                object_pk__in=hosts, content_type__name="host"
            )
        elif search_qs.startswith("network:") and term:
            networks = [
                network.pk
                for network in Network.objects.filter(network__istartswith=term)
            ]
            qs = self.root_queryset.filter(
                object_pk__in=networks, content_type__name="network"
            )
        else:
            qs = super(ObjectPermissionSearchChangeList, self).get_query_set(request)

        return qs


class UserObjectPermissionAdmin(admin.ModelAdmin):
    form = UserObjectPermissionAdminForm
    list_display = ("user", "content_type", "content_object", "permission_name")
    list_filter = (ObjectPermissionFilter, IPAMObjUserFilter)
    search_fields = ("user__username", "^object_pk")
    list_select_related = True
    actions = ["delete_selected"]

    def get_changelist(self, request, **kwargs):
        return ObjectPermissionSearchChangeList

    def get_queryset(self, request):
        qs = super(UserObjectPermissionAdmin, self).get_queryset(request)
        # qs = qs.prefetch_related('user', 'permission', 'content_object').all()
        qs = qs.distinct()
        return qs

    def save_model(self, request, obj, form, change):
        obj.content_type_id = form.cleaned_data["object_id"].split("-")[0]
        obj.object_pk = form.cleaned_data["object_id"].split("-")[1]
        try:
            obj.save()
        except ValidationError as e:
            messages.error(request, "There was an error saving: %s" % e)

    def permission_name(self, obj):
        return obj.permission.codename

    permission_name.short_description = "Permission"

    def object_name(self, obj):
        if obj.content_type.model == "domain":
            return "%s - %s" % (obj.content_type.model, obj.content_object)
        else:
            return "%s - %s" % (obj.content_type.model, obj.object_pk)

    object_name.short_description = "Object"


class GroupObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ("group", "object_name", "permission_name")
    list_filter = (ObjectPermissionFilter, IPAMObjGroupFilter)
    form = GroupObjectPermissionAdminForm
    search_fields = ("group__name", "^object_pk")
    actions = ["delete_selected"]

    def get_changelist(self, request, **kwargs):
        return ObjectPermissionSearchChangeList

    def get_queryset(self, request):
        qs = super(GroupObjectPermissionAdmin, self).get_queryset(request)
        qs = qs.distinct()
        return qs

    def save_model(self, request, obj, form, change):
        obj.content_type_id = form.cleaned_data["object_id"].split("-")[0]
        obj.object_pk = form.cleaned_data["object_id"].split("-")[1]
        try:
            obj.save()
        except ValidationError as e:
            messages.error(request, "There was an error saving: %s" % e)

    def permission_name(self, obj):
        return obj.permission.codename

    permission_name.short_description = "Permission"

    def object_name(self, obj):
        if obj.content_type.model == "domain":
            return "%s - %s" % (obj.content_type.model, obj.content_object)
        else:
            return "%s - %s" % (obj.content_type.model, obj.object_pk)

    object_name.short_description = "Object"


admin.site.register(User, AuthUserAdmin)
admin.site.unregister(AuthGroup)
admin.site.register(AuthGroup, AuthGroupAdmin)
admin.site.register(AuthPermission, AuthPermissionAdmin)
admin.site.unregister(Token)
admin.site.register(Token, TokenAdmin)


admin.site.register(UserObjectPermission, UserObjectPermissionAdmin)
admin.site.register(GroupObjectPermission, GroupObjectPermissionAdmin)
