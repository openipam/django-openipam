from django import forms
from django.contrib.auth.models import Group, Permission
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from openipam.network.models import Address, AddressType, DhcpGroup, Network, NetworkRange
from openipam.dns.models import Domain
from openipam.hosts.models import Host, ExpirationType, Attribute, StructuredAttributeValue, \
    FreeformAttributeToHost, StructuredAttributeToHost
from openipam.core.forms import BaseGroupObjectPermissionForm, BaseUserObjectPermissionForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import FormActions, Accordion, AccordionGroup

from guardian.shortcuts import get_objects_for_user, assign_perm

import autocomplete_light
import operator

User = get_user_model()

NET_IP_CHOICES = (
    (0, 'Network'),
    (1, 'IP'),
)

ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT = [
    address_type.pk for address_type in AddressType.objects.filter(Q(ranges__isnull=False) | Q(is_default=True))
]


class HostForm(forms.ModelForm):
    expire_days = forms.ModelChoiceField(label='Expires', queryset=ExpirationType.objects.all())
    address_type = forms.ModelChoiceField(queryset=AddressType.objects.all())
    network_or_ip = forms.ChoiceField(required=False, choices=NET_IP_CHOICES,
        widget=forms.RadioSelect, label='Please select a network or enter in an IP address')
    network = forms.ModelChoiceField(required=False, queryset=Network.objects.all())
    ip_address = forms.GenericIPAddressField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'style': 'width: 400px;'}))
    show_hide_dhcp_group = forms.BooleanField(label='Click to assign a DHCP Group', required=False)
    dhcp_group = forms.ModelChoiceField(
        DhcpGroup.objects.all(),
        help_text='Leave this alone unless directed by an IPAM administrator',
        widget=autocomplete_light.ChoiceWidget('DhcpGroupAutocomplete'),
        label='DHCP Group',
        required=False
    )
    user_owners = forms.ModelMultipleChoiceField(User.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('UserAutocomplete'),
        required=False)
    group_owners = forms.ModelMultipleChoiceField(Group.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('GroupAutocomplete'),
        required=False)

    def __init__(self, user, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)

        # Attach user to form and model
        self.user = user
        self.instance.user = user

        #Populate some fields if we are editing the record
        current_address_html = None
        expire_date = None

        if self.instance.pk:
            # Get owners
            user_owners, group_owners = self.instance.get_owners()

            self.fields['user_owners'].initial = user_owners
            self.fields['group_owners'].initial = group_owners

            # Set address_type
            self.fields['address_type'].initial = self.instance.get_address_type()

            # Get IP Address(es)
            html_addresses = []
            addresses = self.instance.addresses.all()
            for address in addresses:
                html_addresses.append('<span class="label label-important" style="margin: 5px 5px 0px 0px;">%s</span>' % address)
            if html_addresses:
                change_html = '<a href="#" id="ip-change" class="renew">Change IP Address</a>'
                current_address_html = HTML('''
                    <div class="control-group">
                        <label class="control-label">Current IP Address:</label>
                        <div class="controls" style="margin-top: 5px;">
                            %s
                            %s
                            %s
                        </div>
                    </div>
                ''' % ('<strong>Multiple IPs</strong><br />' if len(addresses) > 1 else '',
                       ''.join(html_addresses),
                       change_html if len(addresses) == 1 else ''))

                self.fields['address_type'].required = False
                self.fields['address_type'].initial = 0
                if len(addresses) > 1:
                    del self.fields['address_type']
                    del self.fields['network_or_ip']
                    del self.fields['network']
                    del self.fields['ip_address']

            # Get Exipre Date
            expire_date = HTML('''
                <div class="control-group">
                    <label class="control-label">Expire Date:</label>
                    <div class="controls" style="margin-top: 5px;">
                        <span class="label label-important">%s</span>
                        <a href="#" id="host-renew" class="renew">Renew Host</a>
                    </div>
                </div>
            ''' % self.instance.expires.strftime('%b %d %Y'))
            self.fields['expire_days'].required = False

            if self.instance.dhcp_group:
                del self.fields['show_hide_dhcp_group']

        # Setup attributes.
        attribute_fields = Attribute.objects.all()
        attribute_initials = []
        if self.instance.pk:
            attribute_initials += self.instance.structured_attributes.values_list('structured_attribute_value__attribute',
                                                                                  'structured_attribute_value')
            attribute_initials += self.instance.freeform_attributes.values_list('attribute', 'value')
        attribute_field_keys = ['Attributes']
        for attribute_field in attribute_fields:
            attribute_field_key = slugify(attribute_field.name)
            attribute_field_keys.append(attribute_field_key)
            if attribute_field.structured:
                attribute_choices_qs = StructuredAttributeValue.objects.filter(attribute=attribute_field.id)
                self.fields[attribute_field_key] = forms.ModelChoiceField(queryset=attribute_choices_qs, required=False)
            else:
                self.fields[attribute_field_key] = forms.CharField(required=False)
            initial = filter(lambda x: x[0] == attribute_field.id, attribute_initials)
            if initial:
                self.fields[attribute_field_key].initial = initial[0][1]

        accordion_groups = [
            AccordionGroup(
                'Host Details',
                'mac',
                'hostname',
                current_address_html,
                'address_type',
                'network_or_ip',
                'network',
                'ip_address',
                expire_date,
                'expire_days',
                'description',
                'show_hide_dhcp_group',
                'dhcp_group',
            )
        ]

        accordion_groups.append(
            AccordionGroup(
                'Owners',
                'user_owners',
                'group_owners',
            )
        )

        # Add owners and groups if super user or ipam admin
        if not user.is_ipamadmin and self.fields.get('address_type', None):
            # Customize address types for non super users
            user_pools = get_objects_for_user(
                user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )
            user_nets = get_objects_for_user(
                user,
                ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                any_perm=True
            )
            n_list = [Q(range__net_contains_or_equals=net.network) for net in user_nets]
            user_networks = NetworkRange.objects.filter(reduce(operator.or_, n_list))

            user_address_types = AddressType.objects.filter(Q(pool__in=user_pools) | Q(ranges__in=user_networks))
            self.fields['address_type'].queryset = user_address_types

        if not user.is_ipamadmin:
            # Remove 10950 days from expires as this is only for admins.
            self.fields['expire_days'].queryset = ExpirationType.objects.filter(min_permissions='00000000')

        # Add attributes
        accordion_groups.append(AccordionGroup(*attribute_field_keys))

        form_actions = [
            Submit('save', 'Save changes'),
            Button('cancel', 'Cancel', onclick="javascript:location.href='%s';" % reverse('list_hosts')),
        ]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Accordion(*accordion_groups),

            FormActions(*form_actions)
        )

    def save(self, *args, **kwargs):

        instance = super(HostForm, self).save(commit=False)
        if self.cleaned_data['expire_days']:
            instance.set_expiration(self.cleaned_data['expire_days'].expiration)
        instance.changed_by = self.user

        # Save
        instance.save()

        # Assign Pool or Network based on conditions
        instance.set_network_ip_or_pool

        # Remove all owners if there are any
        instance.remove_owners()

        # If not admin, assign as owner
        if not self.user.is_ipamadmin:
            instance.assign_owner(self.user)

        # Add Owners and Groups specified
        if self.cleaned_data['user_owners']:
            for user in self.cleaned_data['user_owners']:
                instance.assign_owner(user)
        if self.cleaned_data['group_owners']:
            for group in self.cleaned_data['group_owners']:
                instance.assign_owner(group)

        # Update all host attributes
        # Get all possible attributes
        attribute_fields = Attribute.objects.all()

        # Get all structure attribute values for performance
        structured_attributes = StructuredAttributeValue.objects.all()

        # Delete all attributes so we can start over.
        instance.freeform_attributes.all().delete()
        instance.structured_attributes.all().delete()


        # Loop through potential values and add them
        for attribute in attribute_fields:
            attribute_name = slugify(attribute.name)
            form_attribute = self.cleaned_data.get(attribute_name, '')
            if form_attribute:
                if attribute.structured:
                    attribute_value = filter(lambda x: x == form_attribute, structured_attributes)
                    if attribute_value:
                        StructuredAttributeToHost.objects.create(
                            host=instance,
                            structured_attribute_value=attribute_value[0],
                            changed_by=self.user
                        )
                else:
                    FreeformAttributeToHost.objects.create(
                        host=instance,
                        attribute=attribute,
                        value=form_attribute,
                        changed_by=self.user
                    )

        return instance

    def clean(self):
        cleaned_data = super(HostForm, self).clean()

        return cleaned_data

    def clean_network_or_ip(self):
        network_or_ip = self.cleaned_data['network_or_ip']
        address_type = self.cleaned_data.get('address_type', '')

        if address_type:
            if address_type.pk in ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT and not network_or_ip:
                raise ValidationError('This field is required.')

        return network_or_ip

    def clean_network(self):
        network = self.cleaned_data['network']
        network_or_ip = self.cleaned_data['network_or_ip']

        if network_or_ip and network_or_ip == '0' and not network:
            raise ValidationError('This field is required.')

        self.instance.network = network

        return network

    def clean_ip_address(self):
        ip_address = self.cleaned_data['ip_address']
        network_or_ip = self.cleaned_data['network_or_ip']

        if network_or_ip:
            if network_or_ip == '1' and not ip_address:
                raise ValidationError('This field is required.')

        if ip_address:
            user_pools = get_objects_for_user(
                self.user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )

            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True),
                address=ip_address,
                host__isnull=True,
                reserved=False
            )
            is_available = True if address else False

            if not is_available:
                raise ValidationError('The IP Address requested is reserved, in use, please try again.')
            else:
                self.instance.ip_address = ip_address
                self.instance.network = address.network

        return ip_address

    class Meta:
        model = Host
        exclude = ('expires', 'changed', 'changed_by',)


class HostOwnerForm(forms.Form):
    user_owners = forms.ModelMultipleChoiceField(User.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('UserAutocomplete'),
        required=False)
    group_owners = forms.ModelMultipleChoiceField(Group.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('GroupAutocomplete'),
        required=False)


class HostRenewForm(forms.Form):
    expire_days = forms.ModelChoiceField(label='Expires', queryset=ExpirationType.objects.all())

    def __init__(self, user, *args, **kwargs):
        super(HostRenewForm, self).__init__(*args, **kwargs)

        # TODO: Change later
        if not user.is_ipamadmin:
            self.fields['expire_days'].queryset = ExpirationType.objects.filter(min_permissions='00000000')


class HostListForm(forms.Form):
    groups = forms.ModelChoiceField(Group.objects.all(),
        widget=autocomplete_light.ChoiceWidget('GroupFilterAutocomplete'))
    users = forms.ModelChoiceField(User.objects.all(),
        widget=autocomplete_light.ChoiceWidget('UserFilterAutocomplete'))


class HostGroupPermissionForm(BaseGroupObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='host'))


class HostUserPermissionForm(BaseUserObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='host'))
    content_object = forms.ModelChoiceField(Host.objects.all(), widget=autocomplete_light.ChoiceWidget('HostAutocomplete'))

# class EditHostForm(forms.ModelForm):
# hostname = forms.CharField(widget=autocomplete_light.TextWidget('DomainAutocomplete'))

#     def __init__(self, *args, **kwargs):
#         super(EditHostForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Fieldset(
#                 'Edit Host: {{ object.mac }}',
#                 'mac',
#                 'hostname',
#                 'address_type',
#                 Field('expires', readonly=True),
#                 'description',
#                 'dhcp_group',
#                 css_class='module aligned control-group'
#             ),

#             Submit('save', 'Save changes'),
#             Button('cancel', 'Cancel')
#         )

#     class Meta:
#         model = Host
#         fields = ('mac', 'hostname', 'address_type', 'expires',
#                   'description', 'dhcp_group')
