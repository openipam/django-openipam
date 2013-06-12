from django import forms
from openipam.network.models import AddressType
from openipam.dns.models import Domain
from models import Host, ExpirationType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field, Button
from crispy_forms.bootstrap import FormActions
import autocomplete_light



class AddHostForm(forms.ModelForm):
    expires = forms.ModelChoiceField(queryset=ExpirationType.objects.all())
    address_type = forms.ModelChoiceField(queryset=AddressType.objects.all())

    class Meta:
        model = Host
        exclude = ('changed', 'changed_by',)


class EditHostForm(forms.ModelForm):
    #hostname = forms.CharField(widget=autocomplete_light.TextWidget('DomainAutocomplete'))

    def __init__(self, *args, **kwargs):
        super(EditHostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Edit Host: {{ object.mac }}',
                'mac',
                'hostname',
                'address_type',
                Field('expires', readonly=True),
                'description',
                'dhcp_group',
                css_class='module aligned control-group'
            ),

            Submit('save', 'Save changes'),
            Button('cancel', 'Cancel')
        )

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'address_type', 'expires',
                  'description', 'dhcp_group')
