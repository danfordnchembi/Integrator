from django import forms
from Core import models as core_models



class CPTCodeMappingImportForm(forms.Form):

    file = forms.FileField()


class CPTCodesMappingForm(forms.ModelForm):

    class Meta:
        model = core_models.CPTCode
        fields = '__all__'