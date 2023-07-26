from django import forms
from django.contrib.auth.models import Permission
from django.forms.models import BaseModelFormSet
from django.utils.functional import cached_property
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

from openipam.dns.models import DnsRecord, DnsType, DhcpDnsRecord, Domain
from openipam.hosts.models import Host
from openipam.core.forms import (
    BaseGroupObjectPermissionForm,
    BaseUserObjectPermissionForm,
)

from guardian.shortcuts import get_objects_for_user

from crispy_forms.helper import FormHelper

from dal import autocomplete


User = get_user_model()


class DNSSearchForm(forms.Form):
    search_string = forms.CharField(
        label="Search DNS Records",
        help_text="What DNS records would you like to see?",
        widget=forms.TextInput(attrs={"placeholder": "Search DNS"}),
    )


class DNSListForm(forms.Form):
    host = forms.ModelChoiceField(
        queryset=Host.objects.all(),
        widget=autocomplete.ModelSelect2(url="core:autocomplete:host_autocomplete"),
    )
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=autocomplete.ModelSelect2(url="core:autocomplete:group_autocomplete"),
    )
    users = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url="core:autocomplete:user_autocomplete"),
    )


class BaseDNSUpdateFormset(BaseModelFormSet):
    @cached_property
    def forms(self):
        """
        Instantiate forms at first property access.
        """
        kwargs = {"dns_type_choices": self.dns_type_choices}

        # DoS protection is included in total_form_count()
        forms = [
            self._construct_form(i, **kwargs) for i in range(self.total_form_count())
        ]
        return forms

    def __init__(self, user, *args, **kwargs):
        super(BaseDNSUpdateFormset, self).__init__(*args, **kwargs)
        self.dns_type_choices = [
            (type.pk, type.name)
            for type in DnsType.objects.filter(
                Q(group_permissions__group__in=user.groups.all())
                | Q(user_permissions__user=user)
            )
        ]

    # def _construct_form(self, i, **kwargs):
    #     kwargs['dns_type_queryset'] = self.dns_type_queryset
    #     return super(BaseDNSUpdateFormset, self)._construct_form(i, **kwargs)


class DNSUpdateForm(forms.ModelForm):
    dns_types = forms.ChoiceField(choices=(), required=True)
    # ttl = forms.IntegerField(initial='86400', widget=forms.HiddenInput)

    def __init__(self, dns_type_choices, *args, **kwargs):
        super(DNSUpdateForm, self).__init__(*args, **kwargs)

        self.fields["dns_types"].choices = dns_type_choices

        self.fields.keyOrder = ["name", "ttl", "dns_types", "text_content"]

        if self.instance.pk:
            self.fields["dns_types"].initial = self.instance.dns_type.pk

    def clean(self, *args, **kwargs):
        # data = self.cleaned_data
        # if data['text_content'] and self.instance.ip_content:
        #     raise ValidationError(
        #       'Content for DNS entry %s ''cannot be added because'
        #       ' it has IP Content of %s' %
        #       (self.instance.name, self.instance.ip_content))

        return super(DNSUpdateForm, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Make the dns_type from the hacked form field.
        self.instance.dns_type_id = self.cleaned_data["dns_types"]
        return super(DNSUpdateForm, self).save(*args, **kwargs)

    class Meta:
        model = DnsRecord
        fields = ("name", "ttl", "text_content")


class DSNCreateFrom(forms.Form):
    name = forms.CharField(required=True)
    dns_type = forms.ModelChoiceField(queryset=DnsType.objects.all(), required=True)
    ttl = forms.IntegerField(label="TTL", required=True, initial=14400)
    content = forms.CharField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(DSNCreateFrom, self).__init__(*args, **kwargs)

        self.fields["dns_type"].queryset = get_objects_for_user(
            user,
            ["dns.add_records_to_dnstype", "dns.change_dnstype"],
            any_perm=True,
            use_groups=True,
            with_superuser=False,
        )

        # Disabling dns_type edits per ekoyle
        if self.initial.get("dns_type"):
            self.fields["dns_type"].widget.attrs["readonly"] = True

        self.helper = FormHelper()
        self.helper.label_class = "col-sm-2 col-md-2 col-lg-2"
        self.helper.field_class = "col-sm-6 col-md-6 col-lg-6"

    def clean_dns_type(self):
        if self.initial.get("dns_type"):
            return self.initial.get("dns_type")
        else:
            return self.cleaned_data["dns_type"]


class DhcpDnsRecordForm(forms.ModelForm):
    domain = forms.ModelChoiceField(
        queryset=Domain.objects.all(),
        widget=autocomplete.ModelSelect2(url="core:autocomplete:domain_autocomplete"),
    )
    host = forms.CharField()

    class Meta:
        model = DhcpDnsRecord
        fields = ("host", "domain", "ttl")


class DomainGroupPermissionForm(BaseGroupObjectPermissionForm):
    permission = forms.ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="domain")
    )


class DomainUserPermissionForm(BaseUserObjectPermissionForm):
    permission = forms.ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="domain")
    )


class DnsTypeGroupPermissionForm(BaseGroupObjectPermissionForm):
    permission = forms.ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="dnstype")
    )


class DnsTypeUserPermissionForm(BaseUserObjectPermissionForm):
    permission = forms.ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="dnstype")
    )
