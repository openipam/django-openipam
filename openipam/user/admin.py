from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, Permission as AuthPermission
from openipam.user.models import User, Group, Permission, UserToGroup
from openipam.user.forms import AuthUserCreateAdminForm, AuthUserChangeAdminForm, AuthGroupAdminForm, \
    UserObjectPermissionAdminForm
from guardian.models import UserObjectPermission, GroupObjectPermission


class UserObjectPermissionInline(admin.TabularInline):
    model = UserObjectPermission
    form = UserObjectPermissionAdminForm


class AuthUserAdmin(UserAdmin):
    add_form = AuthUserCreateAdminForm
    form = AuthUserChangeAdminForm
    inlines = [UserObjectPermissionInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions', 'test')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def save_formset(self, request, form, formset, change):
        assert False, change


class AuthGroupAdmin(GroupAdmin):
    form = AuthGroupAdminForm


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


class UserObjectPermissionAdmin(admin.ModelAdmin):
    form = UserObjectPermissionAdminForm
    list_display = ('user', 'permission')
    list_filter = ('permission',)
    list_select_related = True
    search_fields = ('user',)


admin.site.unregister(AuthUser)
admin.site.register(AuthUser, AuthUserAdmin)
admin.site.unregister(AuthGroup)
admin.site.register(AuthGroup, AuthGroupAdmin)
admin.site.register(AuthPermission, AuthPermissionAdmin)

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Permission, PermissionAdmin)

admin.site.register(UserObjectPermission, UserObjectPermissionAdmin)
admin.site.register(GroupObjectPermission)
