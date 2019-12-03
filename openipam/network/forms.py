from django.core.exceptions import ValidationError
from django import forms

from openipam.network.models import (
    AddressType,
    DhcpOptionToDhcpGroup,
    Address,
    Vlan,
    Building,
    BuildingToVlan,
    Network,
    DhcpGroup,
    SharedNetwork,
)

from django_select2.forms import (
    ModelSelect2Widget,
    Select2MultipleWidget,
    Select2TagMixin,
)

from taggit.models import Tag

# from dal import autocomplete
from autocomplete_light import shortcuts as al
from autocomplete_light.contrib.taggit_field import TaggitField, TaggitWidget

from crispy_forms.helper import FormHelper

import binascii


class AddressAdminForm(forms.ModelForm):
    # host = forms.ModelChoiceField(
    #     queryset=Host.objects.all(),
    #     required=False,
    #     widget=autocomplete.ModelSelect2(url="host_autocomplete"),
    # )
    host = al.ModelChoiceField("HostAutocomplete", required=False)

    class Meta:
        model = Address
        exclude = ("changed_by",)


class LeaseAdminForm(forms.ModelForm):
    host = forms.CharField(label="Host Mac")
    address = forms.ModelChoiceField(
        queryset=Address.objects.all(), widget=forms.TextInput
    )

    class Meta:
        model = Address
        exclude = ("host",)


class AddressTypeAdminForm(forms.ModelForm):
    def clean(self):
        ranges = self.cleaned_data.get("ranges", [])
        pool = self.cleaned_data.get("pool", "")

        if pool and ranges:
            raise ValidationError("Address Types cannot have both a pool and a range.")
        if not pool and not ranges:
            raise ValidationError("Address Types must have atleast a pool or a range.")

        return self.cleaned_data

    class Meta:
        model = AddressType
        fields = ("name", "description", "ranges", "pool", "is_default")


class BuildingAssignForm(forms.Form):
    buildings = al.ModelMultipleChoiceField("BuildingAutocomplete", required=False)

    def __init__(self, *args, **kwargs):
        super(BuildingAssignForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


class DhcpOptionToDhcpGroupAdminForm(forms.ModelForm):
    readable_value = forms.CharField(label="Value")

    def __init__(self, *args, **kwargs):
        super(DhcpOptionToDhcpGroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields["readable_value"].initial = self.instance.value_foredit
            self.original_value = self.fields["readable_value"].initial

    def clean_readable_value(self):
        value = self.cleaned_data["readable_value"]
        if value[:2] == "0x":
            self.instance.value = binascii.unhexlify(value[2:])
        else:
            self.instance.value = value.encode()

        return value

    class Meta:
        model = DhcpOptionToDhcpGroup
        exclude = ("value",)


class NetworkTagWidget(Select2TagMixin, Select2MultipleWidget):
    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        values_list = getter(name)
        return ",".join(values_list)


class NetworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NetworkForm, self).__init__(*args, **kwargs)

        choices = [(tag.name, tag.name) for tag in Tag.objects.all()]
        self.fields["tags"].widget.choices = choices

    class Meta:
        model = Network
        fields = "__all__"
        exclude = ("changed",)
        widgets = {
            "dhcp_group": ModelSelect2Widget(
                model=DhcpGroup,
                search_fields=["name__icontains"],
                attrs={"data-minimum-input-length": 0},
            ),
            "shared_network": ModelSelect2Widget(
                model=SharedNetwork,
                search_fields=["name__icontains"],
                attrs={"data-minimum-input-length": 0},
            ),
            "tags": NetworkTagWidget(attrs={"data-minimum-input-length": 0}),
        }


class NetworkTagForm(forms.Form):
    # tags = forms.CharField(widget=autocomplete.TaggitSelect2("tag_autocomplete"))
    tags = TaggitField(widget=TaggitWidget("TagAutocomplete"))

    def __init__(self, *args, **kwargs):
        super(NetworkTagForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


class NetworkReziseForm(forms.Form):
    network = forms.CharField(label="New Network Size", max_length=255)

    def __init__(self, *args, **kwargs):
        super(NetworkReziseForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


class VlanForm(forms.ModelForm):
    building_ids = forms.ModelMultipleChoiceField(
        label="Buildings", queryset=Building.objects.all(), required=False
    )

    def __init__(self, *args, **kwargs):
        super(VlanForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields["building_ids"].initial = [
                bv.building_id
                for bv in BuildingToVlan.objects.filter(vlan=self.instance)
            ]

    class Meta:
        model = Vlan
        fields = ("vlan_id", "name", "description", "building_ids", "changed_by")
