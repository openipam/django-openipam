from django import forms
from django.contrib.auth.models import Group, Permission
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.timezone import localtime, utc

from openipam.network.models import Address, AddressType, DhcpGroup, Network, NetworkRange
from openipam.dns.models import Domain
from openipam.hosts.validators import validate_hostname, validate_csv_file
from openipam.hosts.models import Host, ExpirationType, Attribute, StructuredAttributeValue, \
    FreeformAttributeToHost, StructuredAttributeToHost
from openipam.core.forms import BaseGroupObjectPermissionForm, BaseUserObjectPermissionForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import FormActions, Accordion, AccordionGroup, PrependedText, PrependedAppendedText

from netfields.forms import MACAddressFormField

from guardian.shortcuts import get_objects_for_user, assign_perm

from autocomplete_light import shortcuts as al
import operator

User = get_user_model()

NET_IP_CHOICES = (
    ('0', 'Network'),
    ('1', 'IP'),
)


class HostForm(forms.ModelForm):
    mac_address = MACAddressFormField()
    hostname = forms.CharField(
        validators=[validate_hostname],
        widget=forms.TextInput(attrs={'placeholder': 'Enter a FQDN for this host'})
    )
    expire_days = forms.ModelChoiceField(label='Expires', queryset=ExpirationType.objects.all())
    address_type = forms.ModelChoiceField(queryset=AddressType.objects.all())
    network_or_ip = forms.ChoiceField(required=False, choices=NET_IP_CHOICES,
        widget=forms.RadioSelect, label='Please select a network or enter in an IP address')
    network = forms.ModelChoiceField(required=False, queryset=Network.objects.all())
    ip_address = forms.CharField(label='IP Address', required=False)
    description = forms.CharField(required=False, widget=forms.Textarea())
    show_hide_dhcp_group = forms.BooleanField(label='Assign a DHCP Group', required=False)
    dhcp_group = al.ModelChoiceField(
        'DhcpGroupAutocomplete',
        help_text='Leave this alone unless directed by an IPAM administrator',
        label='DHCP Group',
        required=False
    )
    user_owners = al.ModelMultipleChoiceField('UserAutocomplete', required=False)
    group_owners = al.ModelMultipleChoiceField('GroupAutocomplete', required=False)

    def __init__(self, request, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)

        # Attach user to form and model
        self.user = request.user

        self.previous_form_data = request.session.get('host_form_add')

        #Populate some fields if we are editing the record
        self.primary_address_html = None
        self.secondary_address_html = None
        self.expire_date = None

        self.address_types_with_ranges_or_default = [
            address_type.pk for address_type in AddressType.objects.filter(Q(ranges__isnull=False) | Q(is_default=True)).distinct()
        ]

        # Networks user has permission to.
        self.user_nets = get_objects_for_user(
            self.user,
            ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
            any_perm=True
        )

        if not self.user.is_ipamadmin:
            # Remove 10950 days from expires as This is only for admins.
            self.fields['expire_days'].queryset = ExpirationType.objects.filter(min_permissions='00000000')

        if self.instance.pk:
            # Populate the mac for this record if in edit mode.
            self.fields['mac_address'].initial = self.instance.mac
            # Populate the address type if in edit mode.
            self.fields['address_type'].initial = self.instance.address_type

            # If DCHP group assigned, then do no show toggle
            if self.instance.dhcp_group:
                del self.fields['show_hide_dhcp_group']

        # Init IP Address(es) only if form is not bound
        self._init_ip_address()

        # Init Exipre Date
        self._init_expire_date()

        # Init owners and groups
        self._init_owners_groups()

        # Init attributes.
        self._init_attributes()

        # Init address types
        self._init_address_type()

        # Init network
        self._init_network()

        # Init the form layout
        self._init_form_layout()

    def _init_owners_groups(self):
        if self.instance.pk:
            # Get owners
            user_owners, group_owners = self.instance.owners

            self.fields['user_owners'].initial = user_owners
            self.fields['group_owners'].initial = group_owners

        elif self.previous_form_data:
            if 'user_owners' in self.previous_form_data:
                self.fields['user_owners'].initial = self.previous_form_data.get('user_owners')
            if 'group_owners' in self.previous_form_data:
                self.fields['group_owners'].initial = self.previous_form_data.get('group_owners')
        else:
            self.fields['user_owners'].initial = (self.user.pk,)

    def _init_address_type(self):
        # Customize address types for non super users
        if not self.user.is_ipamadmin and self.fields.get('address_type'):
            user_pools = get_objects_for_user(
                self.user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True,
                use_groups=True
            )
            if self.user_nets:
                n_list = [Q(range__net_contains_or_equals=net.network) for net in self.user_nets]
                user_networks = NetworkRange.objects.filter(reduce(operator.or_, n_list))

                if user_networks:
                    e_list = [Q(network__net_contained_or_equal=nr.range) for nr in user_networks]
                    other_networks = True if self.user_nets.exclude(reduce(operator.or_, e_list)) else False
                else:
                    other_networks = False
            else:
                user_networks = NetworkRange.objects.none()
                other_networks = False

            if self.instance.address_type:
                existing_address_type = self.instance.address_type.pk
            else:
                existing_address_type = None
            user_address_types = AddressType.objects.filter(
                Q(pool__in=user_pools) | Q(ranges__in=user_networks) | Q(pk=existing_address_type) | Q(is_default=True if other_networks else None)
            ).distinct()
            self.fields['address_type'].queryset = user_address_types

        if self.previous_form_data and 'address_type' in self.previous_form_data:
            self.fields['address_type'].initial = self.previous_form_data.get('address_type')

    def _init_network(self):
        # Set networks based on address type if form is bound
        if self.data.get('address_type'):
            self.fields['network'].queryset = (
                Network.objects.by_address_type(AddressType.objects.get(pk=self.data['address_type'])).filter(network__in=self.user_nets)
            )

        # Set networks based on address type if form is not bound
        elif self.instance.pk and not self.data:
            # Set address_type
            self.fields['network'].queryset = Network.objects.by_address_type(self.instance.address_type).filter(network__in=self.user_nets)

        else:
            self.fields['network'].queryset = (
                Network.objects.filter(network__in=self.user_nets)
            )

    def _init_attributes(self):
        attribute_fields = Attribute.objects.all()

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
            elif self.previous_form_data and attribute_field_key in self.previous_form_data:
                self.fields[attribute_field_key].initial = self.previous_form_data.get(attribute_field_key)


    def _init_ip_address(self):
        if self.instance.pk and self.instance.is_static:
            master_ip_address = str(self.instance.master_ip_address)

            self.fields['ip_address'].initial = master_ip_address
            self.fields['ip_address'].label = 'New IP Address'
            self.fields['network_or_ip'].initial = '1'

            addresses = list(self.instance.ip_addresses)

            if master_ip_address in addresses:
                addresses.pop(addresses.index(master_ip_address))

            html_primary_address = '''
                <p class="pull-left"><span class="label label-primary">%s</span></p>
                <a href="javascript:void(0);" id="ip-change" class="pull-left renew">Change Address</a>
            ''' % master_ip_address

            self.primary_address_html = HTML('''
                <div class="form-group">
                    <label class="col-sm-2 col-md-2 col-lg-2 control-label">Primary IP Address:</label>
                    <div class="controls col-sm-6 col-md-6 col-lg-6 form-label">
                            %s
                    </div>
                </div>
            ''' % ''.join(html_primary_address))

            html_secondary_addresses = []
            for address in addresses:
                html_secondary_addresses.append('<p class="pull-left"><span class="label label-primary">%s</span></p>' % address)
            if html_secondary_addresses:
                add_link = ''
                if self.user.is_ipamadmin:
                    add_link = ('<a href="%s" class="pull-left renew">Add/Delete Additional Addresses</a>'
                        % reverse('add_addresses_host', kwargs={'pk':self.instance.mac_stripped}))

                self.secondary_address_html = HTML('''
                    <div class="form-group">
                        <label class="col-sm-2 col-md-2 col-lg-2 control-label">Additional IP Addresses:</label>
                        <div class="controls col-sm-6 col-md-6 col-lg-6 form-label">
                                %s
                                %s
                        </div>
                    </div>
                ''' % (''.join(html_secondary_addresses), add_link))
        elif self.previous_form_data:
            if 'network_or_ip' in self.previous_form_data:
                self.fields['network_or_ip'].initial = self.previous_form_data.get('network_or_ip')
            if 'network' in self.previous_form_data:
                self.fields['network'].initial = self.previous_form_data.get('network')

    def _init_expire_date(self):
        if self.instance.pk:
            self.expire_date = HTML('''
                <div class="form-group">
                    <label class="col-md-2 col-lg-2 control-label">Expire Date:</label>
                    <div class="controls col-md-6 col-lg-6 form-label">
                        <p>
                            <span class="label label-primary">%s</span>
                            <a href="#" id="host-renew" class="renew">Renew Host</a>
                        </p>
                    </div>
                </div>
            ''' % localtime(self.instance.expires.replace(tzinfo=utc)).strftime('%b %d %Y'))
            self.fields['expire_days'].required = False

        elif self.previous_form_data and 'expire_days' in self.previous_form_data:
            self.fields['expire_days'].initial = self.previous_form_data.get('expire_days')

    def _init_form_layout(self):
        # Add Details section
        accordion_groups = [
            AccordionGroup(
                'Host Details',
                'mac_address',
                'hostname',
                self.primary_address_html,
                self.secondary_address_html,
                'address_type',
                'network_or_ip',
                'network',
                'ip_address',
                self.expire_date,
                'expire_days',
                'description',
                PrependedText('show_hide_dhcp_group', ''),
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
        accordion_groups.append(AccordionGroup(*self.attribute_field_keys))

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'col-sm-2 col-md-2 col-lg-2'
        self.helper.field_class = 'col-sm-6 col-md-6 col-lg-6'
        self.helper.layout = Layout(
            Accordion(*accordion_groups),
        )

    def save(self, *args, **kwargs):

        # Call manager function for adding and updating hosts.
        # All host creation should run through this function now.
        user_owners = self.cleaned_data['user_owners'] or None
        group_owners = self.cleaned_data['group_owners'] or None

        instance = Host.objects.add_or_update_host(
            user=self.user,
            user_owners=user_owners,
            group_owners=group_owners,
            instance=self.instance,
            full_clean=False
        )

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
        #assert False, self.data

        cleaned_data = super(HostForm, self).clean()

        self.instance.user = self.user

        if not cleaned_data['user_owners'] and not cleaned_data['group_owners']:
            raise ValidationError('No owner assigned. Please assign a user or group to this Host.')

        if cleaned_data.get('expire_days'):
            self.instance.set_expiration(cleaned_data['expire_days'].expiration)
        if cleaned_data.get('address_type'):
            self.instance.address_type = cleaned_data['address_type']
        if cleaned_data.get('mac_address'):
            self.instance.set_mac_address(cleaned_data['mac_address'])
        if cleaned_data.get('hostname'):
            self.instance.hostname = cleaned_data['hostname']
        if cleaned_data.get('ip_address'):
            self.instance.ip_address = cleaned_data['ip_address']
        if cleaned_data.get('network'):
            self.instance.network = cleaned_data['network']

        return cleaned_data

    def clean_mac_address(self):
        mac = self.cleaned_data.get('mac_address', '')

        host_exists = Host.objects.filter(mac=mac)
        if self.instance.pk:
            host_exists = host_exists.exclude(mac=self.instance.pk)

        if host_exists:
            if host_exists[0].is_expired:
                host_exists[0].delete()
            else:
                raise ValidationError(mark_safe('The mac address entered already exists for host: %s.' % host_exists[0].hostname))
        return mac

    def clean_hostname(self):
        hostname = self.cleaned_data.get('hostname', '')

        host_exists = Host.objects.filter(hostname=hostname.lower())
        if self.instance.pk:
            host_exists = host_exists.exclude(hostname=self.instance.hostname)

        if host_exists:
            if host_exists[0].is_expired:
                host_exists[0].delete()
            else:
                raise ValidationError('The hostname entered already exists for host %s.' % host_exists[0].mac)

        return hostname

    def clean_network_or_ip(self):
        network_or_ip = self.cleaned_data.get('network_or_ip', '')
        address_type = self.cleaned_data.get('address_type', '')

        if address_type:
            if address_type.pk in self.address_types_with_ranges_or_default and not network_or_ip:
                raise ValidationError('This field is required.')

        return network_or_ip

    def clean_network(self):
        network = self.cleaned_data.get('network', '')
        network_or_ip = self.cleaned_data.get('network_or_ip', '')
        address_type = self.cleaned_data.get('address_type', '')

        # If this is a dynamic address type, then bypass
        if address_type and address_type.pk not in self.address_types_with_ranges_or_default:
            return network

        if network_or_ip and network_or_ip == '0' and not network:
            raise ValidationError('This field is required.')
        elif network_or_ip and network_or_ip == '1':
            # Clear value
            network = ''

        if network:
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
            if not user_nets.filter(network=network.network):
                raise ValidationError(mark_safe('You do not have access to assign this host to the '
                                      'network specified: %s.<br />Please contact an IPAM Administrator.' % network))

            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True),
                Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()),
                network=network,
                host__isnull=True,
                reserved=False,
            ).order_by('address')

            if not address:
                raise ValidationError(mark_safe('There is no addresses available from the network specified: %s.<br />'
                                      'Please contact an IPAM Administrator.' % network))
        return network

    def clean_ip_address(self):
        ip_address = self.cleaned_data.get('ip_address', '')
        network_or_ip = self.cleaned_data.get('network_or_ip', '')
        address_type = self.cleaned_data.get('address_type', '')
        current_addresses = list(self.instance.ip_addresses)

        # If this is a dynamic address type, then bypass
        if address_type and address_type.pk not in self.address_types_with_ranges_or_default:
            return ip_address
            #return ip_addresses
        elif ip_address in current_addresses:
            return ip_address

        if network_or_ip and network_or_ip == '1':
            #if not ip_addresses:
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

                # Check address that are assigned and free to use
                addresses = [str(address) for address in Address.objects.filter(
                    Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                    Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()) | Q(leases__host=self.instance),
                    Q(host__isnull=True) | Q(host=self.instance),
                    address=ip_address,
                    reserved=False
                )]

                if ip_address not in addresses:
                    raise ValidationError("The IP Address '%s' is reserved, in use, or not allowed." % ip_address)
        else:
            # Clear values
            ip_address = ''

        return ip_address

    class Meta:
        model = Host
        exclude = ('mac', 'pools', 'address_type_id', 'expires', 'changed', 'changed_by',)


class HostOwnerForm(forms.Form):
    user_owners = al.ModelMultipleChoiceField('UserAutocomplete', required=False)
    group_owners = al.ModelMultipleChoiceField('GroupAutocomplete', required=False)

    def clean(self):
        cleaned_data = super(HostOwnerForm, self).clean()

        if not cleaned_data['user_owners'] and not cleaned_data['group_owners']:
            raise ValidationError('No owner assigned. Please assign a user or group.')

        return cleaned_data


class HostRenewForm(forms.Form):
    expire_days = forms.ModelChoiceField(label='Expires', queryset=ExpirationType.objects.all(),
        error_messages={'required': 'Expire Days is required.'})

    def __init__(self, user, *args, **kwargs):
        super(HostRenewForm, self).__init__(*args, **kwargs)

        # TODO: Change later
        if not user.is_ipamadmin:
            self.fields['expire_days'].queryset = ExpirationType.objects.filter(min_permissions='00000000')


class HostBulkCreateForm(forms.Form):
    csv_file = forms.FileField(validators=[validate_csv_file])


class HostListForm(forms.Form):
    groups = al.ModelChoiceField('GroupFilterAutocomplete')
    users = al.ModelChoiceField('UserFilterAutocomplete')


class HostGroupPermissionForm(BaseGroupObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='host'))


class HostUserPermissionForm(BaseUserObjectPermissionForm):
    permission = forms.ModelChoiceField(queryset=Permission.objects.filter(content_type__model='host'))
    content_object = al.ModelChoiceField('HostAutocomplete')


class ExpirationTypeAdminForm(forms.ModelForm):
    expiration = forms.CharField()

    class Meta:
        model = ExpirationType
        fields = ('expiration',)


class HostAttributesCreateForm(forms.Form):
    add_attribute = forms.ModelChoiceField(queryset=Attribute.objects.all())
    text_value = forms.CharField(label='Value', required=False)
    choice_value = forms.ModelChoiceField(label='Value', required=False, queryset=StructuredAttributeValue.objects.all())


class HostAttributesDeleteForm(forms.Form):
    del_attribute = forms.ModelChoiceField(queryset=Attribute.objects.all())
