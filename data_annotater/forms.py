from django import forms
import re

from .models import RetailRow

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV File',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    
class RetailRowAnnotateForm(forms.ModelForm):
    segment = forms.ChoiceField(
        choices=RetailRow.Segment.choices,
        required=True,
    )

    class Meta:
        model = RetailRow
        fields = ["retailer", "segment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["retailer"].required = True

        merchant = (self.instance.merchant or "").strip()
        retailer = (self.instance.retailer or "").strip()

        if not retailer and merchant:
            self.fields["retailer"].initial = self._suggest_retailer(merchant)

    def clean_retailer(self):
        retailer = (self.cleaned_data.get("retailer") or "").strip()
        if not retailer:
            return retailer
        return self._canonical_retailer(retailer)

    @staticmethod
    def _suggest_retailer(merchant: str) -> str:
        canonical = RetailRowAnnotateForm._canonical_retailer(merchant)
        if canonical != merchant.strip():
            return canonical

        # Fallback for unknown formats: "Name 1234" -> "Name"
        parts = merchant.split()
        trimmed = []
        for part in parts:
            if part.isdigit():
                break
            trimmed.append(part)
        return " ".join(trimmed) if trimmed else merchant

    @staticmethod
    def _canonical_retailer(value: str) -> str:
        normalized = re.sub(r"[^A-Z0-9]", "", value.upper())

        if normalized.startswith("TARGET"):
            return "Target"

        if normalized.startswith("STAPLES"):
            return "Staples"

        return value.strip()
