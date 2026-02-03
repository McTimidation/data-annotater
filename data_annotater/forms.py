from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV File',
        help_text='Accepted format: .csv',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        return file