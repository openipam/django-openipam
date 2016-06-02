from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, Permission as AuthPermission
from django.contrib.admin import SimpleListFilter, ListFilter
from django.utils.encoding import force_text
from django.conf.urls import patterns, url
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib import messages

from openipam.dns.models import Domain
from openipam.hosts.models import Host
from openipam.network.models import Network
from openipam.user.models import User, GroupSource, AuthSource
from openipam.user.forms import AuthUserCreateAdminForm, AuthUserChangeAdminForm, AuthGroupAdminForm, \
    UserObjectPermissionAdminForm, GroupObjectPermissionAdminForm

from guardian.models import UserObjectPermission, GroupObjectPermission

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin

from autocomplete_light import shortcuts as al

from datetime import date


class IPAMAdminFilter(SimpleListFilter):
    title = 'IPAM admin status'
    parameter_name = 'ipamadmin'

    def lookups(self, request, model_admin):

        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):

        if self.value():
            if self.value() == '1':
                queryset = queryset.filter(groups__name='ipam-admins')
            elif self.value() == '0':
                queryset = queryset.exclude(groups__name='ipam-admins')

        return queryset


class IPAMGroupFilter(ListFilter):
    title = 'groups'
    parameter_name = 'groups'
    template = 'admin/filter_autocomplete.html'
    autocomplete_url = '/api/web/GroupAutocomplete/'
    placeholder = 'Search Groups'

    def has_output(self):
        """
        Returns True if some choices would be output for this filter.
        """
        return True

    def choices(self, cl):
        """
        Returns choices ready to be output in the template.
        """
        if getattr(self, 'value', None):
            group = AuthGroup.objects.filter(pk=self.value).first()

            if group:
                return [{
                    'selected': True,
                    'query_string': cl.get_query_string({}, [self.parameter_name]),
                    'display': group.name,
                    'value': group.pk
                }]

        return []

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return [self.parameter_name]

    def queryset(self, request, queryset):
        value = request.GET.get(self.parameter_name, '')

        if value:
            self.value = value
            queryset = queryset.filter(**{'%s__pk' % self.parameter_name: value})
        return queryset


class IPAMObjGroupFilter(IPAMGroupFilter):
    parameter_name = 'group'


class IPAMUserFilter(ListFilter):
    title = 'users'
    parameter_name = 'users'
    template = 'admin/filter_autocomplete.html'
    autocomplete_url = '/api/web/UserAutocomplete/'
    placeholder = 'Search Users'

    def has_output(self):
        """
        Returns True if some choices would be output for this filter.
        """
        return True

    def choices(self, cl):
        """
        Returns choices ready to be output in the template.
        """
        if getattr(self, 'value', None):
            user = User.objects.filter(pk=self.value).first()

            if user:
                return [{
                    'selected': True,
                    'query_string': cl.get_query_string({}, [self.parameter_name]),
                    'display': user.username,
                    'value': user.username
                }]

        return []

    def expected_parameters(self):
        """
        Returns the list of parameter names that are expected from the
        request's query string and that will be used by this filter.
        """
        return [self.parameter_name]

    def queryset(self, request, queryset):
        value = request.GET.get(self.parameter_name, '')

        if value:
            self.value = value
            queryset = queryset.filter(**{'%s__pk' % self.parameter_name: value})
        return queryset


class GroupSourceFilter(SimpleListFilter):
    title = 'Group Source'
    parameter_name = 'source'

    def lookups(self, request, model_admin):
        return [(source.pk, source.name) for source in AuthSource.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(source__source=AuthSource.objects.get(pk=self.value()))
        else:
            internal_source = AuthSource.objects.get(name='INTERNAL')
            queryset = queryset.filter(
                Q(source__source=internal_source) |
                Q(permissions__isnull=False) |
                Q(groupobjectpermission__isnull=False)
            ).distinct()

        return queryset


class IPAMObjUserFilter(IPAMUserFilter):
    parameter_name = 'user'


class AuthUserChangeList(ChangeList):
    def get_queryset(self, request):
        qs = super(AuthUserChangeList, self).get_queryset(request)
        if not len(request.GET):
            qs = qs.filter(last_login__gte='1970-01-01')
        return qs


class AuthUserAdmin(UserAdmin):
    add_form = AuthUserCreateAdminForm
    form = AuthUserChangeAdminForm
    list_display = ('username', 'full_name', 'email', 'permissions', 'is_staff', 'is_superuser', 'is_ipamadmin', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', IPAMAdminFilter, IPAMGroupFilter, 'last_login')
    ordering = ('-last_login',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions',), 'classes': ('collapse',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )

    def permissions(self, obj):
        return '<a href="%s">Permissions</a>' % reverse('admin:user_perms_view', args=[obj.pk])
    permissions.allow_tags = True

    def full_name(self, obj):
        first_name = '' if obj.first_name is None else obj.first_name
        last_name = '' if obj.last_name is None else obj.last_name
        return '%s %s' % (first_name, last_name)
    full_name.admin_order_field = 'last_name'

    def is_ipamadmin(self, obj):
        return obj.is_ipamadmin
    is_ipamadmin.short_description = 'IPAM Admin Status'
    is_ipamadmin.boolean = True

    # Hide Guardian User
    def get_queryset(self, request):
        return super(AuthUserAdmin, self).get_queryset(request).exclude(pk=-1)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            obj_id = int(object_id)
        except:
            raise Http404

        user_add_form = UserObjectPermissionAdminForm(request.POST or None, initial={'user': obj_id})

        if user_add_form.is_valid():
            instance = user_add_form.save(commit=False)
            content_object = user_add_form.cleaned_data['object_id'].split('-')
            instance.content_type_id = content_object[0]
            instance.object_pk = content_object[1]
            instance.save()

            return redirect('admin:user_user_change', object_id)

        user_object_permissions = UserObjectPermission.objects.prefetch_related('content_object', 'permission', 'permission__content_type').filter(user__pk=object_id)
        host_permissions = user_object_permissions.filter(content_type__model='host')
        domain_permissions = user_object_permissions.filter(content_type__model='domain')
        # Prefetch related doesn't seem to work here.
        network_permissions = UserObjectPermission.objects.filter(user__pk=object_id, content_type__model='network')

        extra_context = {
            'group_object_permissions': user_object_permissions,
            'host_permissions': host_permissions,
            'domain_permissions': domain_permissions,
            'network_permissions': network_permissions,
            'user_add_form': user_add_form
        }
        return super(AuthUserAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super(AuthUserAdmin, self).get_urls()
        new_urls = [
            url(r'^perm_delete/(\d+)/$', self.admin_site.admin_view(self.delete_perm_view),
                name='user_perm_delete'),
            url(r'^permissions/(\d+)/$', self.admin_site.admin_view(self.user_perms_view),
                name='user_perms_view'),
        ]
        return new_urls + urls

    def delete_perm_view(self, request, permid):
        next = request.GET.get('next')
        UserObjectPermission.objects.get(pk=permid).delete()
        return redirect(next)

    def user_perms_view(self, request, userid):
        user = User.objects.get(pk=userid)
        groups = user.groups.all()

        context = {
            'user': user,
            'groups': groups,
            'user_permissions': UserObjectPermission.objects.prefetch_related('permission', 'content_type', 'content_object').filter(user__pk=userid),
            'group_permission': GroupObjectPermission.objects.filter(group__in=groups)
        }
        return render(request, 'admin/user/user/permissions.html', context)


class TokenAdmin(TokenAdmin):
    form = al.modelform_factory(Token, fields=('user',))


class AuthGroupSourceInline(admin.StackedInline):
    model = GroupSource


class AuthGroupAdmin(GroupAdmin):
    list_display = ('name', 'authsources')
    list_filter = (IPAMObjUserFilter, GroupSourceFilter)
    form = AuthGroupAdminForm
    list_select_related = True
    inlines = [AuthGroupSourceInline]
    actions = ['change_source_internal', 'change_source_ldap']

    def get_queryset(self, request):
        qs = super(AuthGroupAdmin, self).get_queryset(request)
        return qs.select_related('source__source').extra(where=[
            'auth_group.id in (select group_id from guardian_groupobjectpermission) OR '
            'auth_group.id IN (SELECT group_id FROM user_groupsource where group_id = auth_group.id)'
        ])

    def change_view(self, request, object_id, form_url='', extra_context=None):
        group_add_form = GroupObjectPermissionAdminForm(request.POST or None, initial={'group': object_id})

        if group_add_form.is_valid():
            instance = group_add_form.save(commit=False)
            content_object = group_add_form.cleaned_data['object_id'].split('-')
            instance.content_type_id = content_object[0]
            instance.object_pk = content_object[1]
            instance.save()

            return redirect('admin:auth_group_change', object_id)

        group_object_permissions = GroupObjectPermission.objects.prefetch_related('content_object').filter(group__pk=object_id)
        host_permissions = group_object_permissions.filter(content_type__model='host')
        domain_permissions = group_object_permissions.filter(content_type__model='domain')
        # Prefetch related doesn't seem to work here.
        network_permissions = GroupObjectPermission.objects.filter(group__pk=object_id, content_type__model='network')

        extra_context = {
            'group_object_permissions': group_object_permissions,
            'host_permissions': host_permissions,
            'domain_permissions': domain_permissions,
            'network_permissions': network_permissions,
            'group_add_form': group_add_form
        }
        return super(AuthGroupAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super(AuthGroupAdmin, self).get_urls()
        new_urls = [
            url(r'^perm_delete/(\d+)/$', self.admin_site.admin_view(self.delete_perm_view),
                name='auth_group_perm_delete'),
        ]
        return new_urls + urls

    def delete_perm_view(self, request, permid):
        next = request.GET.get('next')
        GroupObjectPermission.objects.get(pk=permid).delete()
        return redirect(next)

    def authsources(self, obj):
        return '%s' % (obj.source)
    authsources.short_description = 'Source'
    authsources.admin_order_field = 'source__source'

    def change_source_internal(self, request, queryset):
        source = AuthSource.objects.get(name='INTERNAL')
        for group in queryset:
            group.source.source = source
            group.source.save()
    change_source_internal.description = 'Change Group Source to INTERNAL'

    def change_source_ldap(self, request, queryset):
        source = AuthSource.objects.get(name='LDAP')
        for group in queryset:
            group.source.source = source
            group.source.save()
    change_source_ldap.description = 'Change Group Source to LDAP'


class AuthPermissionAdmin(admin.ModelAdmin):
    list_filter = ('content_type__app_label', 'codename', 'content_type__model')
    list_select_related = True
    search_fields = ('name', 'codename')


# class UserPermissionInline(admin.TabularInline):
#     model = UserToGroup
#     fk_name = 'uid'
#     readonly_fields = ('changed_by', 'changed')
#     #form = UserPermissionInlineForm

#     def has_change_permission(self, request, obj=None):
#         return False


# class GroupPermissionInline(admin.TabularInline):
#     model = UserToGroup
#     fk_name = 'gid'


# class UserAdmin(admin.ModelAdmin):
#     search_fields = ('username',)


# class GroupTypeFilter(admin.SimpleListFilter):
#     title = 'group type'

#     parameter_name = 'type'

#     def lookups(self, request, model_admin):
#         return (
#             ('group', 'Groups'),
#             ('user', 'Users'),
#         )

#     def queryset(self, request, queryset):
#         if self.value() == 'user':
#             return queryset.filter(name__istartswith='user_')
#         if self.value() == 'group':
#             return queryset.exclude(name__istartswith='user_')

#     def choices(self, cl):
#         # yield {
#         #     'selected': self.value() is None,
#         #     'query_string': cl.get_query_string({}, [self.parameter_name]),
#         #     'display': _('All'),
#         # }
#         for lookup, title in self.lookup_choices:
#             yield {
#                 'selected': self.value() == force_text(lookup),
#                 'query_string': cl.get_query_string({
#                     self.parameter_name: lookup,
#                 }, []),
#                 'display': title,
#             }


# class GroupAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'permissions', 'lhosts', 'ldomains', 'lnetworks', 'lpools', 'users')
#     list_filter = (GroupTypeFilter,)
#     search_fields = ('name',)
#     form = al.modelform_factory(Group, fields=('name',))
#     list_per_page = 200

#     def get_queryset(self, request):
#         qs = super(GroupAdmin, self).get_queryset(request)

#         if not request.GET.get('type', None):
#             return qs.prefetch_related('domains', 'hosts', 'networks', 'pools', 'user_groups').exclude(name__istartswith='user_')

#         return qs

#     def ldomains(self, obj):
#         return '<a href="../domaintogroup/?group=%s">%s</a>' % (obj.pk, obj.domains.count())
#     ldomains.short_description = 'Domains'
#     ldomains.allow_tags = True

#     def lhosts(self, obj):
#         return '<a href="../hosttogroup/?group=%s">%s</a>' % (obj.pk, obj.hosts.count())
#     lhosts.short_description = 'Hosts'
#     lhosts.allow_tags = True

#     def lnetworks(self, obj):
#         return '<a href="../networktogroup/?group=%s">%s</a>' % (obj.pk, obj.networks.count())
#     lnetworks.short_description = 'Networks'
#     lnetworks.allow_tags = True

#     def lpools(self, obj):
#         return '<a href="../pooltogroup/?group=%s">%s</a>' % (obj.pk, obj.pools.count())
#     lpools.short_description = 'Pools'
#     lpools.allow_tags = True

#     def permissions(self, obj):
#         perms = set([ug.permissions.name for ug in obj.user_groups.all()])
#         return ','.join(perms)

#     def host_permissions(self, obj):
#         perms = set([ug.host_permissions.name for ug in obj.user_groups.all()])
#         return ','.join(perms)

#     def users(self, obj):
#         return '<a href="../user/?group=%s">%s</a>' % (obj.pk, obj.user_groups.count())
#     users.allow_tags = True


# class PermissionAdmin(admin.ModelAdmin):
#     pass


# class UserObjectPermissionFilter(SimpleListFilter):
#     title = 'permission'
#     parameter_name = 'permission'

#     def lookups(self, request, model_admin):
#         permissions = AuthPermission.objects.select_related().filter(
#             Q(codename__icontains='is_owner') | Q(codename__icontains='add_records_to')
#         )
#         permisssion_filters = [(permission.id, permission,) for permission in permissions]

#         return tuple(permisssion_filters)

#     def queryset(self, request, queryset):

#         if self.value():
#             permission = AuthPermission.objects.get(id=self.value())

#             queryset = UserObjectPermission.objects.filter(permission=permission)

#         return queryset


class ObjectPermissionFilter(SimpleListFilter):
    title = 'permission'
    parameter_name = 'permission'

    def lookups(self, request, model_admin):
        permissions = AuthPermission.objects.select_related().filter(
            Q(codename__icontains='is_owner') | Q(codename__icontains='add_records_to')
        )
        permisssion_filters = [(permission.id, permission.codename,) for permission in permissions]

        return tuple(permisssion_filters)

    def queryset(self, request, queryset):

        if self.value():
            permission = AuthPermission.objects.get(id=self.value())
            queryset = queryset.filter(permission=permission)

        return queryset


class ObjectPermissionSearchChangeList(ChangeList):
    "Changelist to do advanced object perms search"

    def get_query_set(self, request):
        search_qs = request.GET.get('q', '')
        term = search_qs.split(':')[-1]
        if search_qs.startswith('domain:') and term:
            domains = [domain.pk for domain in Domain.objects.filter(name__istartswith=term)]
            qs = self.root_queryset.filter(object_pk__in=domains, content_type__name='domain')
        elif search_qs.startswith('host:') and term:
            hosts = [host.pk for host in Host.objects.filter(hostname__istartswith=term)]
            qs = self.root_queryset.filter(object_pk__in=hosts, content_type__name='host')
        elif search_qs.startswith('network:') and term:
            networks = [network.pk for network in Network.objects.filter(network__istartswith=term)]
            qs = self.root_queryset.filter(object_pk__in=networks, content_type__name='network')
        else:
            qs = super(ObjectPermissionSearchChangeList, self).get_query_set(request)

        return qs

# class ObjectFilter(admin.SimpleListFilter):
#     title = 'object'
#     parameter_name = 'object'

#     def lookups(self, request, model_admin):
#         groups = Group.objects.exclude(name__istartswith='user_')
#         group_vals = [(group.pk, group.name) for group in groups]

#         return tuple(group_vals)

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(group__pk=self.value())

#     def choices(self, cl):
#         yield {
#             'selected': self.value() is None,
#             'query_string': cl.get_query_string({}, [self.parameter_name]),
#             'display': _('All'),
#         }
#         for lookup, title in self.lookup_choices:
#             yield {
#                 'selected': self.value() == force_text(lookup),
#                 'query_string': cl.get_query_string({
#                     self.parameter_name: lookup,
#                 }, []),
#                 'display': title,
#             }


class UserObjectPermissionAdmin(admin.ModelAdmin):
    form = UserObjectPermissionAdminForm
    list_display = ('user', 'content_type', 'content_object', 'permission_name',)
    list_filter = (ObjectPermissionFilter, IPAMObjUserFilter)
    search_fields = ('user__username', '^object_pk')
    list_select_related = True
    actions = ['delete_selected']

    def get_changelist(self, request, **kwargs):
        return ObjectPermissionSearchChangeList

    # def change_view(self, request, object_id, extra_context=None):
    #     extra_context = extra_context or {}
    #     extra_context['readonly'] = True
    #     return super(UserObjectPermissionAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super(UserObjectPermissionAdmin, self).get_queryset(request)
        qs = qs.prefetch_related('user', 'permission', 'content_object').all()
        return qs

    def save_model(self, request, obj, form, change):
        obj.content_type_id = form.cleaned_data['object_id'].split('-')[0]
        obj.object_pk = form.cleaned_data['object_id'].split('-')[1]
        obj.save()

    def permission_name(self, obj):
        return obj.permission.codename
    permission_name.short_description = 'Permission'

    def object_name(self, obj):
        #c_obj = obj.content_type.model_class().objects.get(pk=obj.object_pk)
        return '%s - %s' % (obj.content_type.model, obj.content_object)
    object_name.short_description = 'Object'


class GroupObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'object_name', 'permission_name',)
    list_filter = (ObjectPermissionFilter, IPAMObjGroupFilter)
    form = GroupObjectPermissionAdminForm
    search_fields = ('group__name', '^object_pk',)
    actions = ['delete_selected']

    def get_changelist(self, request, **kwargs):
        return ObjectPermissionSearchChangeList

    def get_queryset(self, request):
        qs = super(GroupObjectPermissionAdmin, self).get_queryset(request)
        qs = qs.prefetch_related('permission', 'content_object').distinct()
        return qs

    def save_model(self, request, obj, form, change):
        obj.content_type_id = form.cleaned_data['object_id'].split('-')[0]
        obj.object_pk = form.cleaned_data['object_id'].split('-')[1]
        obj.save()

    def permission_name(self, obj):
        return obj.permission.codename
    permission_name.short_description = 'Permission'

    def object_name(self, obj):
        if obj.content_type.model == 'network':
            return '%s - %s' % (obj.content_type.model, obj.object_pk)
        else:
            return '%s - %s' % (obj.content_type.model, obj.content_object)
        #return obj.content_object
    object_name.short_description = 'Object'


class UserGroupTypeFilter(admin.SimpleListFilter):
    title = 'group'

    parameter_name = 'group'

    def lookups(self, request, model_admin):
        groups = Group.objects.exclude(name__istartswith='user_')
        group_vals = [(group.pk, group.name) for group in groups]

        return tuple(group_vals)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group__pk=self.value())

    def choices(self, cl):
        yield {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('All'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


# class UserToGroupAdmin(admin.ModelAdmin):
#     list_display = ('user', 'group', 'permissions', 'host_permissions')
#     list_filter = (UserGroupTypeFilter,)
#     form = al.modelform_factory(UserToGroup, fields=('user', 'group', 'permissions', 'host_permissions', 'changed_by',))


# class HostToGroupAdmin(admin.ModelAdmin):
#     list_display = ('host', 'group')
#     form = al.modelform_factory(HostToGroup, fields=('host', 'group', 'changed_by',))


# class DomainToGroupAdmin(admin.ModelAdmin):
#     list_display = ('domain', 'group')
#     list_filter = (UserGroupTypeFilter,)
#     form = al.modelform_factory(DomainToGroup,  fields=('domain', 'group', 'changed_by',))


# class NetworkToGroupAdmin(admin.ModelAdmin):
#     list_display = ('network', 'group')
#     form = al.modelform_factory(NetworkToGroup,  fields=('network', 'group', 'changed_by',))


# class PoolToGroupAdmin(admin.ModelAdmin):
#     list_display = ('pool', 'group')
#     form = al.modelform_factory(PoolToGroup,  fields=('pool', 'group',))


admin.site.register(User, AuthUserAdmin)
admin.site.unregister(AuthGroup)
admin.site.register(AuthGroup, AuthGroupAdmin)
admin.site.register(AuthPermission, AuthPermissionAdmin)
admin.site.unregister(Token)
admin.site.register(Token, TokenAdmin)

# admin.site.register(Group, GroupAdmin)
# admin.site.register(Permission, PermissionAdmin)

# admin.site.register(UserToGroup, UserToGroupAdmin)
# admin.site.register(HostToGroup, HostToGroupAdmin)
# admin.site.register(DomainToGroup, DomainToGroupAdmin)
# admin.site.register(NetworkToGroup, NetworkToGroupAdmin)
# admin.site.register(PoolToGroup, PoolToGroupAdmin)

admin.site.register(UserObjectPermission, UserObjectPermissionAdmin)
admin.site.register(GroupObjectPermission, GroupObjectPermissionAdmin)
