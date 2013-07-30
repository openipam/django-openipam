from django import forms
from openipam.network.models import AddressType, DhcpGroup, Network
from openipam.dns.models import Domain
from models import Host, ExpirationType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Button
from crispy_forms.bootstrap import FormActions, InlineRadios
import autocomplete_light


NET_IP_CHOICES = (
    (0, 'Network'),
    (1, 'IP'),
)


class HostForm(forms.ModelForm):
    expires = forms.ModelChoiceField(queryset=ExpirationType.objects.all())
    address_type = forms.ModelChoiceField(queryset=AddressType.objects.all())
    network_or_ip = forms.ChoiceField(choices=NET_IP_CHOICES,
        widget=forms.RadioSelect, label='Please select a network or enter in an IP address')
    network = forms.ModelChoiceField(queryset=Network.objects.all())
    ip_address = forms.CharField(required=False)
    show_hide_dhcp_group = forms.BooleanField(label='Click to assign a DHCP Group')
    dhcp_group = forms.ModelChoiceField(
        DhcpGroup.objects.all(),
        help_text='Leave this alone unless directed by an IPAM administrator',
        widget=autocomplete_light.ChoiceWidget('DhcpGroupAutocomplete'),
        label='DHCP Group',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Add Host',
                'mac',
                'hostname',
                'address_type',
                InlineRadios('network_or_ip'),
                'network',
                'ip_address',
                Field('expires', readonly=True),
                'description',
                'show_hide_dhcp_group',
                'dhcp_group',
                css_class='module aligned control-group'
            ),

            Submit('save', 'Save changes'),
            Button('cancel', 'Cancel')
        )

    class Meta:
        model = Host
        exclude = ('changed', 'changed_by',)


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
