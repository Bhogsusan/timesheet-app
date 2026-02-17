from django.contrib import admin
from django import forms
from .models import Company, Timesheet, TimesheetEntry, ExtraHours

class CompanyAdminForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            existing = Company.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f'A company with the name "{name}" already exists.')
        return name

class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    list_display = ['name', 'pattern_type', 'is_active', 'get_weekly_total']
    list_filter = ['pattern_type', 'is_active']
    search_fields = ['name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'pattern_type', 'biweekly_start_date', 'is_active')
        }),
        ('Weekly Pattern (Standard)', {
            'fields': ('mon_hours', 'tue_hours', 'wed_hours', 'thu_hours', 'fri_hours', 'sat_hours', 'sun_hours'),
            'description': 'Used for weekly pattern companies'
        }),
        ('Bi-Weekly Pattern - Week A', {
            'fields': ('mon_hours_week_a', 'tue_hours_week_a', 'wed_hours_week_a', 'thu_hours_week_a', 
                      'fri_hours_week_a', 'sat_hours_week_a', 'sun_hours_week_a'),
            'classes': ('collapse',),
            'description': 'First week of bi-weekly cycle'
        }),
        ('Bi-Weekly Pattern - Week B', {
            'fields': ('mon_hours_week_b', 'tue_hours_week_b', 'wed_hours_week_b', 'thu_hours_week_b',
                      'fri_hours_week_b', 'sat_hours_week_b', 'sun_hours_week_b'),
            'classes': ('collapse',),
            'description': 'Second week of bi-weekly cycle (alternating)'
        }),
    )
    
    def get_weekly_total(self, obj):
        if obj.pattern_type == 'weekly':
            total = (obj.mon_hours + obj.tue_hours + obj.wed_hours + 
                    obj.thu_hours + obj.fri_hours + obj.sat_hours + obj.sun_hours)
            return f"{total} hrs/week"
        else:
            total_a = (obj.mon_hours_week_a + obj.tue_hours_week_a + obj.wed_hours_week_a +
                      obj.thu_hours_week_a + obj.fri_hours_week_a + obj.sat_hours_week_a + obj.sun_hours_week_a)
            total_b = (obj.mon_hours_week_b + obj.tue_hours_week_b + obj.wed_hours_week_b +
                      obj.thu_hours_week_b + obj.fri_hours_week_b + obj.sat_hours_week_b + obj.sun_hours_week_b)
            return f"A: {total_a}, B: {total_b} hrs/week"
    get_weekly_total.short_description = 'Weekly Total'

class TimesheetEntryInline(admin.TabularInline):
    model = TimesheetEntry
    extra = 1

class ExtraHoursInline(admin.TabularInline):
    model = ExtraHours
    extra = 0

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ['cleaner_name', 'month', 'year', 'get_total_hours', 'created_at']
    list_filter = ['year', 'month']
    search_fields = ['cleaner_name']
    inlines = [TimesheetEntryInline, ExtraHoursInline]
    
    def get_total_hours(self, obj):
        return obj.get_total_hours()
    get_total_hours.short_description = 'Total Hours'

admin.site.register(Company, CompanyAdmin)