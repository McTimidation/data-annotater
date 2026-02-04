from django import forms
from .models import RetailRow

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV File',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    
class RetailRowAnnotateForm(forms.ModelForm):
    class Meta:
        model = RetailRow
        fields = ["retailer", "segment"]