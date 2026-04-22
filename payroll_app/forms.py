from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'id_number', 'rate', 'allowance']

MONTHS = [(m, m) for m in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]]

class PayrollForm(forms.Form):
    payroll_for = forms.ChoiceField(choices=[])
    month = forms.ChoiceField(choices=MONTHS)
    year = forms.CharField(max_length=4)
    cycle = forms.ChoiceField(choices=[(1, '1'), (2, '2')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically load employee choices
        employee_choices = [('All', 'All Employees')] + [(e.id_number, e.id_number) for e in Employee.objects.all()]
        self.fields['payroll_for'].choices = employee_choices