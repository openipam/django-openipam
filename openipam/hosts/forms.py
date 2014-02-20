from django import forms
from django.contrib.auth.models import Group, Permission
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.utils.safestring import mark_safe

from openipam.network.models import Address, AddressType, DhcpGroup, Network, NetworkRange
from openipam.dns.models import Domain
from openipam.hosts.validators import validate_hostname
from openipam.hosts.models import Host, ExpirationType, Attribute, StructuredAttributeValue, \
    FreeformAttributeToHost, StructuredAttributeToHost
from openipam.core.forms import BaseGroupObjectPermissionForm, BaseUserObjectPermissionForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import FormActions, Accordion, AccordionGroup

from netfields.forms import MACAddressFormField

from guardian.shortcuts import get_objects_for_user, assign_perm

import autocomplete_light
import operator

User = get_user_model()

NET_IP_CHOICES = (
    (0, 'Network'),
    (1, 'IP'),
)

ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT = [
    address_type.pk for address_type in AddressType.objects.filter(Q(ranges__isnull=False) | Q(is_default=True)).distinct()
]


class HostForm(forms.ModelForm):
    mac_address = MACAddressFormField()
    hostname = forms.CharField(validators=[validate_hostname])
    expire_days = forms.ModelChoiceField(label='Expires', queryset=ExpirationType.objects.all())
    address_type_id = forms.ModelChoiceField(label='Address Type', queryset=AddressType.objects.all())
    network_or_ip = forms.ChoiceField(required=False, choices=NET_IP_CHOICES,
        widget=forms.RadioSelect, label='Please select a network or enter in an IP address')
    network = forms.ModelChoiceField(required=False, queryset=Network.objects.all())
    ip_address = forms.CharField(label='IP Address', required=False)
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
        self.instance.user = self.user = user

        #Populate some fields if we are editing the record
        self.current_address_html = None
        self.expire_date = None

        # Set networks based on address type if form is bound
        if self.data.get('address_type_id'):
            self.fields['network'].queryset = (Network.objects.
                get_networks_from_address_type(AddressType.objects.get(pk=self.data['address_type_id'])))

        if not self.user.is_ipamadmin:
            # Remove 10950 days from expires as this is only for admins.
            self.fields['expire_days'].queryset = ExpirationType.objects.filter(min_permissions='00000000')

        if self.instance.pk:

            # Populate the hostname for this record if in edit mode.
            self.fields['hostname'].initial = self.instance.hostname
            # Populate the mac for this record if in edit mode.
            self.fields['mac_address'].initial = self.instance.mac

            # Init owners and groups
            self._init_owners_groups()

            # Init Exipre Date
            self._init_expire_date()

            # Set networks based on address type if form is not bound
            if not self.data:
                # Set address_type
                address_type = self.instance.address_type
                self.fields['network'].queryset = Network.objects.get_networks_from_address_type(address_type)

                # Init IP Address(es) only if form is not bound
                self._init_ip_address()

            # If DCHP group assigned, then do no show toggle
            if self.instance.dhcp_group:
                del self.fields['show_hide_dhcp_group']

        # Init attributes.
        self._init_attributes()

        # Init address types
        self._init_address_type()

        # Init the form layout
        self._init_form_layout()


    def _init_owners_groups(self):
        # Get owners
        user_owners, group_owners = self.instance.get_owners()

        self.fields['user_owners'].initial = user_owners
        self.fields['group_owners'].initial = group_owners

    def _init_address_type(self):
        # Customize address types for non super users
        if not self.user.is_ipamadmin and self.fields.get('address_type_id'):
            user_pools = get_objects_for_user(
                self.user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )
            user_nets = get_objects_for_user(
                self.user,
                ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                any_perm=True
            )
            if user_nets:
                n_list = [Q(range__net_contains_or_equals=net.network) for net in user_nets]
                user_networks = NetworkRange.objects.filter(reduce(operator.or_, n_list))
            else:
                user_networks = NetworkRange.objects.none()

            user_address_types = AddressType.objects.filter(Q(pool__in=user_pools) | Q(ranges__in=user_networks)).distinct()
            self.fields['address_type_id'].queryset = user_address_types

    def _init_attributes(self):

        attribute_fields = Attribute.objects.all()
        structured_attribute_values = StructuredAttributeValue.objects.all()

        attribute_initials = []
        if self.instance.pk:
            attribute_initials += self.instance.structured_attributes.values_list('structured_attribute_value__attribute',
                                                                                  'structured_attribute_value')
            attribute_initials += self.instance.freeform_attributes.values_list('attribute', 'value')
        self.attribute_field_keys = ['Attributes']
        for attribute_field in attribute_fields:
            attribute_field_key = slugify(attribute_field.name)
            self.attribute_field_keys.append(attribute_field_key)
            if attribute_field.structured:
                attribute_choices_qs = StructuredAttributeValue.objects.filter(attribute=attribute_field.id)
                self.fields[attribute_field_key] = forms.ModelChoiceField(queryset=attribute_choices_qs, required=False)
            else:
                self.fields[attribute_field_key] = forms.CharField(required=False)
            initial = filter(lambda x: x[0] == attribute_field.id, attribute_initials)
            if initial:
                self.fields[attribute_field_key].initial = initial[0][1]

    def _init_ip_address(self):

        html_addresses = []
        addresses = self.instance.addresses.all()
        for address in addresses:
            html_addresses.append('<span class="label label-important" style="margin: 5px 5px 0px 0px;">%s</span>' % address)
        if html_addresses:
            change_html = '<a href="#" id="ip-change" class="renew">Change IP Address</a>'
            self.current_address_html = HTML('''
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

            if len(addresses) > 1:
                del self.fields['address_type_id']
                del self.fields['network_or_ip']
                del self.fields['network']
                del self.fields['ip_address']
            else:
                self.fields['ip_address'].initial = addresses[0]
                self.fields['ip_address'].label = 'New IP Address'
                self.fields['network_or_ip'].initial = '1'

    def _init_expire_date(self):

        self.expire_date = HTML('''
            <div class="control-group">
                <label class="control-label">Expire Date:</label>
                <div class="controls" style="margin-top: 5px;">
                    <span class="label label-important">%s</span>
                    <a href="#" id="host-renew" class="renew">Renew Host</a>
                </div>
            </div>
        ''' % self.instance.expires.strftime('%b %d %Y'))
        self.fields['expire_days'].required = False

    def _init_form_layout(self):

        # Add Details section
        accordion_groups = [
            AccordionGroup(
                'Host Details',
                'mac_address',
                'hostname',
                self.current_address_html,
                'address_type_id',
                'network_or_ip',
                'network',
                'ip_address',
                self.expire_date,
                'expire_days',
                'description',
                'show_hide_dhcp_group',
                'dhcp_group',
            )
        ]

        # Add owners and groups section
        accordion_groups.append(
            AccordionGroup(
                'Owners',
                'user_owners',
                'group_owners',
            )
        )

        # Add attributes section
        #assert False, self.attribute_field_keys
        accordion_groups.append(AccordionGroup(*self.attribute_field_keys))

        # Create form actions
        form_actions = [
            Submit('save', 'Save changes'),
            Button('cancel', 'Cancel', onclick="javascript:location.href='%s';" % reverse('list_hosts')),
        ]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Accordion(*accordion_groups),
            #FormActions(*form_actions)
        )


    def save(self, *args, **kwargs):

        instance = super(HostForm, self).save(commit=False)

        if self.cleaned_data['expire_days']:
            instance.set_expiration(self.cleaned_data['expire_days'].expiration)
        instance.changed_by = self.user

        instance.hostname = self.cleaned_data['hostname']
        instance.set_mac_address(self.cleaned_data['mac_address'])

        # Save
        instance.save()

        # Assign Pool or Network based on conditions
        instance.set_network_ip_or_pool()

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

    def clean_mac_address(self):
        mac = self.cleaned_data.get('mac_address', '')

        if self.instance.pk:
            host_exists = Host.objects.exclude(mac=self.instance.pk).filter(mac=mac)
            if host_exists:
                raise ValidationError('The mac address entered already exists for host %s.' % host_exists.hostname)

        return mac

    def clean_hostname(self):
        hostname = self.cleaned_data.get('hostname', '')

        if self.instance.pk:
            hostname_exists = Host.objects.exclude(hostname=self.instance.hostname).filter(hostname=hostname)
            if hostname_exists:
                raise ValidationError('The hostname entered already exists for host %s.' % hostname_exists.hostname)

        return hostname

    def clean_network_or_ip(self):
        network_or_ip = self.cleaned_data.get('network_or_ip', '')
        address_type = self.cleaned_data.get('address_type_id', '')

        #assert False, (address_type.pk, ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT)
        #assert False, list(ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT)
        if address_type:
            if address_type.pk in ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT and not network_or_ip:
                raise ValidationError('This field is required.')

        return network_or_ip

    def clean_network(self):
        network = self.cleaned_data.get('network', '')
        network_or_ip = self.cleaned_data.get('network_or_ip', '')
        address_type = self.cleaned_data.get('address_type_id', '')

        self.instance.network = network

        # If this is a dynamic address type, then bypass
        if address_type and address_type.pk not in ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT:
            return network

        if network_or_ip and network_or_ip == '0' and not network:
            raise ValidationError('This field is required.')
        elif network_or_ip and network_or_ip == '1':
            # Clear value
            network = ''

        if network:
            user_pools = get_objects_for_user(
                self.instance.user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )

            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True),
                network=self.instance.network,
                host__isnull=True,
                reserved=False,
            ).order_by('address')

            if not address:
                raise ValidationError(mark_safe('There is no addresses available from this network.<br />'
                                      'Please contact an IPAM Administrator.'))
        return network

    def clean_ip_address(self):
        ip_address = self.cleaned_data.get('ip_address', '')
        network_or_ip = self.cleaned_data.get('network_or_ip', '')
        address_type = self.cleaned_data.get('address_type_id', '')
        current_addresses = [str(address) for address in self.instance.addresses.all()]

        # If this is a dynamic address type, then bypass
        if address_type and address_type.pk not in ADDRESS_TYPES_WITH_RANGES_OR_DEFAULT:
            return ip_address
        # If this host has this IP already then stop (meaning its not changing)
        elif ip_address in current_addresses:
            self.instance.ip_address = ip_address
            return ip_address

        if network_or_ip and network_or_ip == '1':
            if not ip_address:
                raise ValidationError('This field is required.')

            elif ip_address:
                # Make sure this is valid.
                validate_ipv46_address(ip_address)

                user_pools = get_objects_for_user(
                    self.user,
                    ['network.add_records_to_pool', 'network.change_pool'],
                    any_perm=True
                )
                user_nets = get_objects_for_user(
                    self.user,
                    ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                    any_perm=True
                )

                address = Address.objects.filter(
                    Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                    address=ip_address,
                    host__isnull=True,
                    reserved=False
                )
                is_available = True if address else False

                if not is_available:
                    raise ValidationError('The IP Address is reserved, in use, or not allowed.')
                else:
                    self.instance.ip_address = ip_address
        else:
            # Clear values
            ip_address = ''

        return ip_address

    class Meta:
        model = Host
        exclude = ('mac', 'hostname', 'expires', 'changed', 'changed_by',)


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
