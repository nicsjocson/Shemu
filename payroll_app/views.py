from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee, Payslip
from .forms import EmployeeForm, PayrollForm

def home(request):
    employees = Employee.objects.all()
    if request.method == 'POST':
        if 'add_overtime' in request.POST:
            emp_id = request.POST.get('emp_id')
            hours = float(request.POST.get('hours', 0))
            emp = get_object_or_404(Employee, id_number=emp_id)
            # Overtime = (Rate/160) x 1.5 x Overtime Hours
            added_ot = (emp.getRate() / 160) * 1.5 * hours
            emp.overtime_pay = emp.getOvertime() + added_ot
            emp.save()
            return redirect('home')
        elif 'delete_employee' in request.POST:
            emp_id = request.POST.get('emp_id')
            emp = get_object_or_404(Employee, id_number=emp_id)
            emp.delete()
            return redirect('home')

    return render(request, 'payroll_app/home.html', {'employees': employees})

def create_employee(request):
    form = EmployeeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'payroll_app/employee_form.html', {'form': form, 'action': 'Create'})

def update_employee(request, id_number):
    emp = get_object_or_404(Employee, id_number=id_number)
    form = EmployeeForm(request.POST or None, instance=emp)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'payroll_app/employee_form.html', {'form': form, 'action': 'Update'})

def payslips(request):
    payslips_list = Payslip.objects.all()
    form = PayrollForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        payroll_for = form.cleaned_data['payroll_for']
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        cycle = int(form.cleaned_data['cycle'])

        employees = Employee.objects.all() if payroll_for == 'All' else Employee.objects.filter(id_number=payroll_for)
        date_range = "1-15" if cycle == 1 else "16-End"

        for emp in employees:
            if Payslip.objects.filter(id_number=emp, month=month, year=year, pay_cycle=cycle).exists():
                messages.error(request, f"Error: Payslip already exists for {emp.getName()} ({month} {year}, Cycle {cycle}).")
                continue

            cycle_rate = emp.getRate() / 2
            allowance = emp.getAllowance()
            overtime = emp.getOvertime()
            gross_pay = cycle_rate + allowance + overtime

            tax = gross_pay * 0.20
            pag_ibig = 100.0 if cycle == 1 else 0.0
            health = emp.getRate() * 0.04 if cycle == 2 else 0.0
            sss = emp.getRate() * 0.045 if cycle == 2 else 0.0

            deductions = tax + pag_ibig + health + sss
            total_pay = gross_pay - deductions

            Payslip.objects.create(
                id_number=emp, month=month, date_range=date_range, year=year, pay_cycle=cycle,
                rate=emp.getRate(), earnings_allowance=allowance, deductions_tax=tax,
                deductions_health=health, pag_ibig=pag_ibig, sss=sss,
                overtime=overtime, total_pay=total_pay
            )
            emp.resetOvertime() # Reset OT to 0 after generation
        return redirect('payslips')

    return render(request, 'payroll_app/payslips.html', {'form': form, 'payslips': payslips_list})

def view_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    return render(request, 'payroll_app/view_payslip.html', {'payslip': payslip})