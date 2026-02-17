from django import forms
from .models import Company, Timesheet, TimesheetEntry, ExtraHours
from django.forms import formset_factory, modelformset_factory

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'pattern_type', 'biweekly_start_date', 'is_active',
            # Weekly hours
            'mon_hours', 'tue_hours', 'wed_hours', 'thu_hours', 'fri_hours', 'sat_hours', 'sun_hours',
            # Bi-weekly Week A
            'mon_hours_week_a', 'tue_hours_week_a', 'wed_hours_week_a', 'thu_hours_week_a',
            'fri_hours_week_a', 'sat_hours_week_a', 'sun_hours_week_a',
            # Bi-weekly Week B
            'mon_hours_week_b', 'tue_hours_week_b', 'wed_hours_week_b', 'thu_hours_week_b',
            'fri_hours_week_b', 'sat_hours_week_b', 'sun_hours_week_b',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Company Name'}),
            'pattern_type': forms.Select(attrs={'class': 'pattern-select'}),
            'biweekly_start_date': forms.DateInput(attrs={'type': 'date'}),
            # Weekly hours - step 0.01 for 2 decimal places
            'mon_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'tue_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'wed_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'thu_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'fri_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'sat_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'sun_hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            # Week A
            'mon_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'tue_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'wed_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'thu_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'fri_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'sat_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'sun_hours_week_a': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            # Week B
            'mon_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'tue_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'wed_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'thu_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'fri_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'sat_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
            'sun_hours_week_b': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'hours-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check if company with this name already exists (case-insensitive)
            existing = Company.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f'A company with the name "{name}" already exists.')
        return name

    def clean(self):
        cleaned_data = super().clean()
        pattern_type = cleaned_data.get('pattern_type')
        biweekly_start_date = cleaned_data.get('biweekly_start_date')
        
        if pattern_type == 'biweekly' and not biweekly_start_date:
            self.add_error('biweekly_start_date', 'Start date is required for bi-weekly patterns')
        
        return cleaned_data


class CompanySelectForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        empty_label="Select a company...",
        widget=forms.Select(attrs={'class': 'company-select'})
    )

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['cleaner_name', 'month', 'year']
        widgets = {
            'cleaner_name': forms.TextInput(attrs={'placeholder': 'Enter cleaner name'}),
            'month': forms.Select(choices=Timesheet.MONTH_CHOICES),  # Use month choices
            'year': forms.NumberInput(attrs={'min': 2020, 'max': 2030}),
        }

class ExtraHoursForm(forms.ModelForm):
    class Meta:
        model = ExtraHours
        fields = ['company', 'date', 'hours', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'hours': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),  # 2 decimal places
            'description': forms.TextInput(attrs={'placeholder': 'e.g., Deep Cleaning by Kim'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        self.fields['company'].required = False
        self.fields['date'].required = False
        self.fields['hours'].required = False
        self.fields['description'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        # Only validate if any data is provided
        has_data = any([
            cleaned_data.get('date'),
            cleaned_data.get('hours') and cleaned_data.get('hours') > 0,
            cleaned_data.get('description')
        ])
        
        # If no data, return empty cleaned_data (will be filtered out later)
        if not has_data:
            cleaned_data['DELETE'] = True
        
        return cleaned_data

ExtraHoursFormSet = modelformset_factory(
    ExtraHours,
    form=ExtraHoursForm,
    extra=1,
    can_delete=True
)