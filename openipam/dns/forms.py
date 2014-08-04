from django import forms
from django.contrib.auth.models import Permission, Group
from django.forms.models import BaseModelFormSet
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.contrib.auth import get_user_model
from django.db.models import Q

from openipam.dns.models import DnsRecord, DnsType
from openipam.hosts.models import Host
from openipam.core.forms import BaseGroupObjectPermissionForm, BaseUserObjectPermissionForm

from guardian.shortcuts import get_objects_for_user

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

import autocomplete_light

import copy

User = get_user_model()

DNSTYPE_CHOICES = [(type.pk, type.name) for type in DnsType.objects.exclude(min_permissions__name='NONE')]


class DNSSearchForm(forms.Form):
    search_string = forms.CharField(
        label='Search DNS Records',
        help_text='What DNS records would you like to see?',
        widget=forms.TextInput(attrs={'placeholder': 'Search DNS'})
    )


class DNSListForm(forms.Form):
    host = autocomplete_light.ModelChoiceField('HostFilterAutocomplete')
    groups = autocomplete_light.ModelChoiceField('GroupFilterAutocomplete')
    users = autocomplete_light.ModelChoiceField('UserFilterAutocomplete')


class BaseDNSUpdateFormset(BaseModelFormSet):

    @cached_property
    def forms(self):
        """
        Instantiate forms at first property access.
        """
        kwargs = {'dns_type_choices': self.dns_type_choices}

        # DoS protection is included in total_form_count()
        forms = [self._construct_form(i, **kwargs) for i in xrange(self.total_form_count())]
        return forms

    def __init__(self, user, *args, **kwargs):
        super(BaseDNSUpdateFormset, self).__init__(*args, **kwargs)
        self.dns_type_choices = [(type.pk, type.name) for type in DnsType.objects.filter(
            Q(group_permissions__group__in=user.groups.all()) |
            Q(user_permissions__user=user)
        )]

    # def _construct_form(self, i, **kwargs):
    #     kwargs['dns_type_queryset'] = self.dns_type_queryset
    #     return super(BaseDNSUpdateFormset, self)._construct_form(i, **kwargs)


class DNSUpdateForm(forms.ModelForm):
    dns_types = forms.ChoiceField(choices=(), required=True)
    #ttl = forms.IntegerField(initial='86400', widget=forms.HiddenInput)

    def __init__(self, dns_type_choices, *args, **kwargs):
        super(DNSUpdateForm, self).__init__(*args, **kwargs)

        self.fields['dns_types'].choices = dns_type_choices

        self.fields.keyOrder = [
            'name',
            'ttl',
            'dns_types',
            'text_content',
        ]

        if self.instance.pk:
            self.fields['dns_types'].initial = self.instance.dns_type.pk

    def clean(self, *args, **kwargs):

        #data = self.cleaned_data
        # if data['text_content'] and self.instance.ip_content:
        #     raise ValidationError('Content for DNS entry %s cannot be added because'
        #                           ' it has IP Content of %s' % (self.instance.name, self.instance.ip_content))

        return super(DNSUpdateForm, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Make the dns_type from the hacked form field.
        self.instance.dns_type_id = self.cleaned_data['dns_types']
        return super(DNSUpdateForm, self).save(*args, **kwargs)

        #assert False, dns_type_queryset
        # if dns_type_queryset:
        #     self.fields['dns_type'] = forms.ModelChoiceField(queryset=dns_type_queryset)

    class Meta:
        model = DnsRecord
        fields = ('name', 'ttl', 'text_content')


class DSNCreateFrom(forms.Form):
    name = forms.CharField(required=True)
    dns_type = forms.ModelChoiceField(queryset=DnsType.objects.all(), required=True)
    ttl = forms.IntegerField(label='TTL', required=True, initial=14400)
    content = forms.CharField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(DSNCreateFrom, self).__init__(*args, **kwargs)

        dns_user = copy.deepcopy(user)
        dns_user.is_superuser = False
        self.fields['dns_type'].queryset = get_objects_for_user(
            dns_user,
            ['dns.add_records_to_dnstype', 'dns.change_dnstype'],
            any_perm=True,
            use_groups=True
        )

        self.helper = FormHelper()
        self.helper.label_class = 'col-sm-2 col-md-2 col-lg-2'
        self.helper.field_class = 'col-sm-6 col-md-6 col-lg-6'


class DomainGroupPermissionForm(BaseGroupObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='domain'))


class DomainUserPermissionForm(BaseUserObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='domain'))


class DnsTypeGroupPermissionForm(BaseGroupObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='dnstype'))


class DnsTypeUserPermissionForm(BaseUserObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='dnstype'))

