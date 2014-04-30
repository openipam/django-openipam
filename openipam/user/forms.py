from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.db.models import Q
from django.contrib.auth import get_user_model

from guardian.models import UserObjectPermission, GroupObjectPermission

import autocomplete_light

import operator

User = get_user_model()


class AuthUserCreateAdminForm(UserCreationForm):
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    class Meta:
        model = User


class AuthUserChangeAdminForm(UserChangeForm):
    groups = forms.ModelMultipleChoiceField(Group.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('GroupFilterAutocomplete'), required=False)
    user_permissions = forms.ModelMultipleChoiceField(Permission.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PermissionAutocomplete'), required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        db_user = User.objects.filter(username__iexact=username)

        if 'username' in self.changed_data and db_user and db_user[0] != self.instance:
            raise forms.ValidationError('Username already exists.')

        return username

    class Meta:
        model = User


class AuthGroupAdminForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(Permission.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('PermissionAutocomplete'), required=False)

    # def clean_name(self):
    #     name = self.cleaned_data['name'].lower()

    #     if Group.objects.filter(name=name):
    #         raise forms.ValidationError('Group name already exists.')

    #     return name

    class Meta:
        model = Group


PERMISSION_FILTER = [
    Q(codename__startswith='add_records_to'),
    Q(codename__startswith='is_owner'),
]


class IPAMAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Please enter a correct %(username)s and password. "
                           "Note that passwords are case-sensitive.",
        'inactive': "This account is inactive.",
    }


class UserObjectPermissionAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), widget=autocomplete_light.ChoiceWidget('UserAutocomplete'))
    permission = forms.ModelChoiceField(Permission.objects.select_related('content_type').filter(reduce(operator.or_, PERMISSION_FILTER)), label='Permission')
    # permission = forms.ModelChoiceField(Permission.objects.filter(content_type__app_label__in=settings.IPAM_APPS),
    #     widget=autocomplete_light.ChoiceWidget('PermissionAutocomplete'), label='Permission')
    object_id = forms.CharField(widget=autocomplete_light.ChoiceWidget('IPAMObjectsAutoComplete'), label='Object')

    # def __init__(self, *args, **kwargs):
    #     super(UserObjectPermissionAdminForm, self).__init__(*args, **kwargs)

    #     if self.instance:
    #        self.fields['object_id'].initial = '%s-%s' % (self.instance.content_type.pk, self.instance.object_pk)

    class Meta:
        model = UserObjectPermission
        exclude = ('content_type', 'object_pk',)


class GroupObjectPermissionAdminForm(forms.ModelForm):
    group = forms.ModelChoiceField(Group.objects.all(), widget=autocomplete_light.ChoiceWidget('GroupAutocomplete'))
    permission = forms.ModelChoiceField(Permission.objects.filter(reduce(operator.or_, PERMISSION_FILTER)), label='Permission')
    object_id = forms.CharField(widget=autocomplete_light.ChoiceWidget('IPAMObjectsAutoComplete'), label='Object')

    # def __init__(self, *args, **kwargs):
    #     super(UserObjectPermissionAdminForm, self).__init__(*args, **kwargs)

    #     if self.instance:
    #        self.fields['object_id'].initial = '%s-%s' % (self.instance.content_type.pk, self.instance.object_pk)

    class Meta:
        model = GroupObjectPermission
        exclude = ('content_type', 'object_pk')
