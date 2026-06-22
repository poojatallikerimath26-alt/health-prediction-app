from datetime import date

from django import forms

from .models import PatientRecord


class PatientRecordForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = PatientRecord
        fields = ["full_name", "date_of_birth", "email", "glucose", "haemoglobin", "cholesterol"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Pooja Tallikerimath"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
            "glucose": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "placeholder": "mg/dL"}),
            "haemoglobin": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "placeholder": "g/dL"}),
            "cholesterol": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "placeholder": "mg/dL"}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data["date_of_birth"]
        if dob > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean_glucose(self):
        value = self.cleaned_data["glucose"]
        if value <= 0:
            raise forms.ValidationError("Glucose must be a positive number.")
        return value

    def clean_haemoglobin(self):
        value = self.cleaned_data["haemoglobin"]
        if value <= 0:
            raise forms.ValidationError("Haemoglobin must be a positive number.")
        return value

    def clean_cholesterol(self):
        value = self.cleaned_data["cholesterol"]
        if value <= 0:
            raise forms.ValidationError("Cholesterol must be a positive number.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        full_name = cleaned_data.get("full_name")
        dob = cleaned_data.get("date_of_birth")
        email = cleaned_data.get("email")

        if full_name and dob and email:
            if PatientRecord.objects.filter(
                full_name=full_name, date_of_birth=dob, email=email
            ).exists():
                raise forms.ValidationError(
                    "A record with this name, date of birth, and email already exists."
                )
        return cleaned_data