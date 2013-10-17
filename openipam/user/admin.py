from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, Permission as AuthPermission
from django.contrib.admin import SimpleListFilter
from openipam.user.models import User, Group, Permission, UserToGroup
from openipam.user.forms import AuthUserCreateAdminForm, AuthUserChangeAdminForm, AuthGroupAdminForm, \
    UserObjectPermissionAdminForm, GroupObjectPermissionAdminForm
from guardian.models import UserObjectPermission, GroupObjectPermission


class AuthUserAdmin(UserAdmin):
    add_form = AuthUserCreateAdminForm
    form = AuthUserChangeAdminForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # def save_formset(self, request, form, formset, change):
    #     assert False, change


class AuthGroupAdmin(GroupAdmin):
    pass
    #form = AuthGroupAdminForm


class AuthPermissionAdmin(admin.ModelAdmin):
    list_filter = ('content_type__app_label',)
    list_select_related = True
    search_fields = ('name', 'content_type__name', 'content_type__app_label',)


class UserPermissionInline(admin.TabularInline):
    model = UserToGroup
    fk_name = 'uid'
    readonly_fields = ('changed_by', 'changed')
    #form = UserPermissionInlineForm

    def has_change_permission(self, request, obj=None):
        return False


class GroupPermissionInline(admin.TabularInline):
    model = UserToGroup
    fk_name = 'gid'


class UserAdmin(admin.ModelAdmin):
    search_fields = ('username',)


class GroupAdmin(admin.ModelAdmin):
    pass


class PermissionAdmin(admin.ModelAdmin):
    pass


class PermissionFilter(SimpleListFilter):
    title = 'permission'
    parameter_name = 'permission'

    def lookups(self, request, model_admin):
        permissions = AuthPermission.objects.select_related().all()
        permisssion_filters = [(permission.id, permission,) for permission in permissions]

        return tuple(permisssion_filters)

    def queryset(self, request, queryset):

        if self.value():
            permission = AuthPermission.objects.get(id=self.value())

            queryset = UserObjectPermission.objects.filter(permission=permission)

        return queryset


class UserObjectPermissionAdmin(admin.ModelAdmin):
    form = UserObjectPermissionAdminForm
    list_display = ('user', 'object_name', 'permission',)
    list_filter = (PermissionFilter,)
    search_fields = ('user__username',)

    def get_queryset(self, request):
        qs = super(UserObjectPermissionAdmin, self).queryset(request)
        qs = qs.prefetch_related('user', 'permission', 'content_object').all()
        return qs

    def save_model(self, request, obj, form, change):
        obj.content_type_id = form.cleaned_data['object_id'].split('-')[0]
        obj.object_pk = form.cleaned_data['object_id'].split('-')[1]
        obj.save()

    def object_name(self, obj):
        c_obj = obj.content_type.model_class().objects.get(pk=obj.object_pk)
        return '%s - %s' % (obj.content_type.model, c_obj)
    object_name.short_description = 'Object'


class GroupObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'object_name', 'permission')
    list_filter = (PermissionFilter,)
    form = GroupObjectPermissionAdminForm
    search_fields = ('group__name',)

    def save_model(self, request, obj, form, change):
        obj.content_type_id = form.cleaned_data['object_id'].split('-')[0]
        obj.object_pk = form.cleaned_data['object_id'].split('-')[1]
        obj.save()

    def object_name(self, obj):
        c_obj = obj.content_type.model_class().objects.get(pk=obj.object_pk)
        return '%s - %s' % (obj.content_type.model, c_obj)
    object_name.short_description = 'Object'


admin.site.register(User, AuthUserAdmin)
admin.site.unregister(AuthGroup)
admin.site.register(AuthGroup, AuthGroupAdmin)
admin.site.register(AuthPermission, AuthPermissionAdmin)

admin.site.register(Group, GroupAdmin)
admin.site.register(Permission, PermissionAdmin)

admin.site.register(UserObjectPermission, UserObjectPermissionAdmin)
admin.site.register(GroupObjectPermission, GroupObjectPermissionAdmin)
