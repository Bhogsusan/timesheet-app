from django.db import models
from decimal import Decimal, ROUND_HALF_UP

class Company(models.Model):
    PATTERN_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
    ]
    
    name = models.CharField(max_length=200, unique = True)
    pattern_type = models.CharField(max_length=10, choices=PATTERN_CHOICES, default='weekly')
    
    # Weekly hours (0-7 days) - Changed to 2 decimal places
    mon_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tue_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    wed_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    thu_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fri_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sat_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sun_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Bi-weekly pattern (for alternating weeks) - Changed to 2 decimal places
    mon_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tue_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    wed_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    thu_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fri_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sat_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sun_hours_week_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    mon_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tue_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    wed_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    thu_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fri_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sat_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sun_hours_week_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    biweekly_start_date = models.DateField(null=True, blank=True, help_text="Date when Week A starts (for bi-weekly patterns)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_pattern_type_display()})"
    
    def get_weekly_hours(self):
        """Get standard weekly hours dict with Decimal"""
        return {
            0: self.mon_hours,
            1: self.tue_hours,
            2: self.wed_hours,
            3: self.thu_hours,
            4: self.fri_hours,
            5: self.sat_hours,
            6: self.sun_hours,
        }
    
    def get_biweekly_hours(self, is_week_a=True):
        """Get bi-weekly hours based on which week it is"""
        if is_week_a:
            return {
                0: self.mon_hours_week_a,
                1: self.tue_hours_week_a,
                2: self.wed_hours_week_a,
                3: self.thu_hours_week_a,
                4: self.fri_hours_week_a,
                5: self.sat_hours_week_a,
                6: self.sun_hours_week_a,
            }
        else:
            return {
                0: self.mon_hours_week_b,
                1: self.tue_hours_week_b,
                2: self.wed_hours_week_b,
                3: self.thu_hours_week_b,
                4: self.fri_hours_week_b,
                5: self.sat_hours_week_b,
                6: self.sun_hours_week_b,
            }


class Timesheet(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    cleaner_name = models.CharField(max_length=200)
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-month', 'cleaner_name']
    
    def __str__(self):
        return f"{self.cleaner_name} - {self.get_month_display()} {self.year}"
    
    def get_month_name(self):
        return self.get_month_display()
    
    def get_total_hours(self):
        from decimal import Decimal
        total = Decimal('0.00')
        for entry in self.entries.all():
            total += entry.get_total_hours()
        for eh in self.extra_hours.all():
            total += eh.hours
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class TimesheetEntry(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='entries')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Timesheet Entries"
    
    def __str__(self):
        return f"{self.timesheet} - {self.company.name}"
    
    def get_total_hours(self):
        """Calculate total hours for this entry based on company's pattern"""
        from calendar import monthrange
        from datetime import date
        from decimal import Decimal
        
        year = self.timesheet.year
        month = self.timesheet.month
        _, days_in_month = monthrange(year, month)
        
        total = Decimal('0.00')
        
        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            weekday = current_date.weekday()
            
            if self.company.pattern_type == 'weekly':
                hours = self.company.get_weekly_hours()[weekday]
                total += hours
            else:
                # Bi-weekly logic - repeats every 2 weeks
                if self.company.biweekly_start_date:
                    # Calculate days difference from start date
                    days_diff = (current_date - self.company.biweekly_start_date).days
                    
                    # If negative, we're before start date - use week A as default
                    if days_diff < 0:
                        is_week_a = True
                    else:
                        # Calculate which 2-week period we're in
                        # Week 0-6: Week A, Week 7-13: Week B, Week 14-20: Week A, etc.
                        two_week_period = days_diff // 7  # Which week number (0, 1, 2, 3...)
                        is_week_a = (two_week_period % 2) == 0  # Even weeks are A, odd are B
                    
                    hours = self.company.get_biweekly_hours(is_week_a)[weekday]
                    total += hours
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def get_daily_hours(self, day):
        """Get hours for a specific day"""
        from calendar import monthrange
        from datetime import date
        
        year = self.timesheet.year
        month = self.timesheet.month
        
        try:
            current_date = date(year, month, day)
        except ValueError:
            return Decimal('0.00')
        
        weekday = current_date.weekday()
        
        if self.company.pattern_type == 'weekly':
            return self.company.get_weekly_hours()[weekday]
        else:
            if self.company.biweekly_start_date:
                days_diff = (current_date - self.company.biweekly_start_date).days
                
                if days_diff < 0:
                    is_week_a = True
                else:
                    two_week_period = days_diff // 7
                    is_week_a = (two_week_period % 2) == 0
                
                return self.company.get_biweekly_hours(is_week_a)[weekday]
        return Decimal('0.00')


class ExtraHours(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='extra_hours')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)  # Made optional
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Changed to 2 decimal places
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Extra Hours"
        ordering = ['date']
    
    def __str__(self):
        date_str = self.date.strftime('%Y-%m-%d') if self.date else 'No date'
        return f"{date_str}: {self.hours} hrs - {self.description[:30]}"