from django import forms


class ResidentialBuildSetup(forms.Form):
    max_resident = forms.IntegerField(min_value=1, label='Ilość mieszkańców')