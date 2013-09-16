from django import forms
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from openipam.network.models import AddressType, DhcpGroup, Network
from openipam.dns.models import Domain
from openipam.hosts.models import Host, ExpirationType, Attribute, StructuredAttributeValue
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import FormActions, InlineRadios, Accordion, AccordionGroup
import autocomplete_light


NET_IP_CHOICES = (
    (0, 'Network'),
    (1, 'IP'),
)


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

    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)

        #Populate some fields if we are editing the record
        current_address_html = None
        expire_date = None
        if self.instance.pk:

            #assert False, self.instance.address_type

            # Get owners
            owners = self.instance.owners
            self.fields['user_owners'].initial = owners[0]
            self.fields['group_owners'].initial = owners[1]

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
                self.fields['show_hide_dhcp_group'].initial = True

        attribute_fields = Attribute.objects.all()
        attribute_field_keys = ['Attributes']
        for attribute_field in attribute_fields:
            attribute_field_key = slugify(attribute_field.name)
            attribute_field_keys.append(attribute_field_key)
            if attribute_field.structured:
                attribute_choices_qs = StructuredAttributeValue.objects.filter(aid=attribute_field.id)
                self.fields[attribute_field_key] = forms.ModelChoiceField(queryset=attribute_choices_qs, required=False)
            else:
                self.fields[attribute_field_key] = forms.CharField(required=False)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Accordion(
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
                    #css_class='module aligned control-group'
                ),
                AccordionGroup(
                    'Owners',
                    'user_owners',
                    'group_owners',
                ),
                AccordionGroup(*attribute_field_keys),
            ),

            FormActions(
                Submit('save', 'Save changes'),
                Button('cancel', 'Cancel', onclick="javascript:location.href='%s';" % reverse('list_hosts')),
            )
        )

    class Meta:
        model = Host
        exclude = ('expires', 'changed', 'changed_by',)


class ChangeOwnerForm(forms.Form):
    user_owners = forms.ModelMultipleChoiceField(User.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('UserAutocomplete'),
        required=False)
    group_owners = forms.ModelMultipleChoiceField(Group.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('GroupAutocomplete'),
        required=False)


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
