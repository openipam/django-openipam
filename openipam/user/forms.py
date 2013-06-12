from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from guardian.models import UserObjectPermission, GroupObjectPermission
import autocomplete_light


class AuthUserCreateAdminForm(UserCreationForm):
    def clean_username(self):
        username = self.cleaned_data['username'].lower()

        if User.objects.filter(username=username):
            raise forms.ValidationError('Username already exists.')

        super(self, AuthUserCreateAdminForm).clean_username()


class AuthUserChangeAdminForm(UserChangeForm):
    test = forms.CharField()


    def clean_username(self):
        #assert False, self.instance.username
        username = self.cleaned_data['username']
        db_user = User.objects.filter(username=username.lower())

        if 'username' in self.changed_data and db_user and db_user[0] != self.instance:
            raise forms.ValidationError('Username already exists.')

        return username

class AuthGroupAdminForm(forms.ModelForm):

    def clean_name(self):
        name = self.cleaned_data['name'].lower()

        if Group.objects.filter(name=name):
            raise forms.ValidationError('Group name already exists.')

    class Meta:
        model = Group



class UserObjectPermissionAdminForm(forms.ModelForm):
    # user = forms.ModelChoiceField(User.objects.all(),
    #     widget=autocomplete_light.ChoiceWidget('UserAutocomplete'))
    permission = forms.ModelChoiceField(Permission.objects.filter(content_type__app_label__in=settings.IPAM_APPS),
        widget=autocomplete_light.ChoiceWidget('PermissionAutocomplete'), label='Permission')
    object_id = forms.CharField(widget=autocomplete_light.ChoiceWidget('IPAMObjectsAutoComplete'), label='Object')

    # def __init__(self, *args, **kwargs):
    #     super(UserObjectPermissionAdminForm, self).__init__(*args, **kwargs)

    #     if self.instance:
    #        self.fields['object_id'].initial = '%s-%s' % (self.instance.content_type.pk, self.instance.object_pk)


    class Meta:
        model = UserObjectPermission
        exclude = ('content_type', 'object_pk',)
