from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import Token

from guardian.models import UserObjectPermission, GroupObjectPermission

from autocomplete_light import shortcuts as al

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
            self.error_messages["duplicate_username"], code="duplicate_username"
        )

    class Meta:
        model = User
        fields = ("username",)


class AuthUserChangeAdminForm(UserChangeForm):
    groups = al.ModelMultipleChoiceField("GroupFilterAutocomplete", required=False)
    user_permissions = al.ModelMultipleChoiceField(
        "PermissionAutocomplete", required=False
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        db_user = User.objects.filter(username__iexact=username)

        if "username" in self.changed_data and db_user and db_user[0] != self.instance:
            raise forms.ValidationError("Username already exists.")

        return username

    class Meta:
        model = User
        fields = ("username",)


class AuthGroupAdminForm(forms.ModelForm):
    permissions = al.ModelMultipleChoiceField("PermissionAutocomplete", required=False)
    # def clean_name(self):
    #     name = self.cleaned_data['name'].lower()

    #     if Group.objects.filter(name=name):
    #         raise forms.ValidationError('Group name already exists.')

    #     return name

    class Meta:
        model = Group
        fields = ("name",)


PERMISSION_FILTER = [
    Q(codename__startswith="add_records_to"),
    Q(codename__startswith="is_owner"),
]


class IPAMAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Please enter a correct %(username)s and password. "
        "Note that passwords are case-sensitive.",
        "inactive": "This account is inactive.",
    }


class PermissionModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.codename


class UserObjectPermissionAdminForm(forms.ModelForm):
    user = al.ModelChoiceField("UserAutocomplete")
    permission = PermissionModelChoiceField(
        queryset=Permission.objects.select_related("content_type").filter(
            reduce(operator.or_, PERMISSION_FILTER)
        ),
        label="Permission",
        empty_label="Select A Permssion",
    )
    object_id = forms.CharField(
        widget=al.ChoiceWidget("IPAMObjectsAutoComplete"), label="Object"
    )

    def __init__(self, *args, **kwargs):
        super(UserObjectPermissionAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["object_id"].initial = "%s-%s" % (
                self.instance.content_type.pk,
                self.instance.object_pk,
            )

    class Meta:
        model = UserObjectPermission
        exclude = ("content_type", "object_pk")


class GroupObjectPermissionAdminForm(forms.ModelForm):
    group = al.ModelChoiceField("GroupAutocomplete")
    permission = PermissionModelChoiceField(
        queryset=Permission.objects.select_related("content_type").filter(
            reduce(operator.or_, PERMISSION_FILTER)
        ),
        label="Permission",
        empty_label="Select A Permssion",
    )
    object_id = forms.CharField(
        widget=al.ChoiceWidget("IPAMObjectsAutoComplete"), label="Object"
    )

    def __init__(self, *args, **kwargs):
        super(GroupObjectPermissionAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["object_id"].initial = "%s-%s" % (
                self.instance.content_type.pk,
                self.instance.object_pk,
            )

    def clean(self):
        cleaned_data = super(GroupObjectPermissionAdminForm, self).clean()

        content_type_id = (
            cleaned_data["object_id"].split("-")[0]
            if cleaned_data.get("object_id")
            else None
        )
        object_pk = (
            cleaned_data["object_id"].split("-")[1]
            if cleaned_data.get("object_id")
            else None
        )
        group = cleaned_data["group"] if cleaned_data.get("group") else None
        permission = (
            cleaned_data["permission"] if cleaned_data.get("permission") else None
        )

        if content_type_id and object_pk and group and permission:
            try:
                GroupObjectPermission.objects.get(
                    group=group,
                    permission=permission,
                    content_type_id=content_type_id,
                    object_pk=object_pk,
                )
            except GroupObjectPermission.DoesNotExist:
                pass
            else:
                raise ValidationError(
                    "Group Permission with this Group, Permission, And Object already exist."
                )

    class Meta:
        model = GroupObjectPermission
        exclude = ("content_type", "object_pk")


class GroupForm(forms.Form):
    groups = al.ModelMultipleChoiceField("GroupAutocomplete")


class UserObjectPermissionForm(forms.ModelForm):
    permission = PermissionModelChoiceField(
        queryset=Permission.objects.select_related("content_type").filter(
            reduce(operator.or_, PERMISSION_FILTER)
        ),
        label="Permission",
        empty_label="Select A Permssion",
    )
    object_id = forms.CharField(
        widget=al.ChoiceWidget("IPAMObjectsAutoComplete"), label="Object"
    )

    class Meta:
        model = UserObjectPermission
        exclude = ("content_type", "object_pk", "user")


class TokenForm(forms.ModelForm):
    user = al.ModelChoiceField("UserAutocomplete")

    class Meta:
        model = Token
        fields = ("user",)
