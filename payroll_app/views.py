from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Employee, Payslip

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('home')
            else:
                return redirect('payslips')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'payroll_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    if not request.user.is_staff:
        return redirect('payslips')
    employees = Employee.objects.all()
    return render(request, 'payroll_app/home.html', {'employees': employees})

@login_required(login_url='login')
def delete_employee(request, pk):
    if not request.user.is_staff:
        return redirect('payslips')
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('home')

@login_required(login_url='login')
def add_overtime(request, pk):  
    if not request.user.is_staff:
        return redirect('payslips')
    if request.method == 'POST':
        employee = get_object_or_404(Employee, pk=pk)
        hours_input = request.POST.get('overtime_hours', '').strip()
        if not hours_input:
            messages.error(request, 'Please enter overtime hours.')
            return redirect('home')
        hours = float(hours_input)
        if hours <= 0:
            messages.error(request, 'Overtime hours must be greater than 0.')
            return redirect('home')
        overtime = (employee.rate / 160) * 1.5 * hours
        if employee.overtime_pay is None: 
            employee.overtime_pay = 0
        employee.overtime_pay += overtime
        employee.save()
    return redirect('home')

@login_required(login_url='login')
def create_employee(request):
    if not request.user.is_staff:
        return redirect('payslips')
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name.replace(' ', '').isalpha():
            messages.error(request, 'Name must only contain letters and spaces.')
            return redirect('create_employee')

        id_number = request.POST.get('id_number')
        if not id_number.isdigit():
            messages.error(request, 'ID Number must contain numbers only and must be positive.')
            return redirect('create_employee')

        rate_input = float(request.POST.get('rate'))
        if rate_input <= 0:
            messages.error(request, 'Rate must be greater than 0.')
            return redirect('create_employee')

        allowance = request.POST.get('allowance') or None
        if allowance is not None:
            allowance = float(allowance)
            if allowance < 0:
                messages.error(request, 'Allowance must be 0 or greater.')
                return redirect('create_employee')

        if Employee.objects.filter(id_number=id_number).exists():
            messages.error(request, 'An employee with this ID number already exists.')
            return redirect('create_employee')

        # Auto-create a User account using ID number as username and password
        if User.objects.filter(username=id_number).exists():
            messages.error(request, 'A user account with this ID number already exists.')
            return redirect('create_employee')

        user = User.objects.create_user(username=id_number, password=id_number)

        Employee.objects.create(
            name=name,
            id_number=id_number,
            rate=rate_input,
            allowance=allowance,
            user=user
        )
        return redirect('home')
    return render(request, 'payroll_app/create_employee.html')

@login_required(login_url='login')
def update_employee(request, pk):
    if not request.user.is_staff:
        return redirect('payslips')
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name_input = request.POST.get('name')
        if not name_input.replace(' ', '').isalpha():
            messages.error(request, 'Name must only contain letters and spaces.')
            return render(request, 'payroll_app/update_employee.html', {'employee': employee})
        employee.name = name_input
        id_number = request.POST.get('id_number')
        if not id_number.isdigit():
            messages.error(request, 'ID Number must contain numbers only and must be positive.')
            return render(request, 'payroll_app/update_employee.html', {'employee': employee})
        if id_number != employee.id_number:
            if Employee.objects.filter(id_number=id_number).exists():
                messages.error(request, 'An employee with this ID number already exists.')
                return render(request, 'payroll_app/update_employee.html', {'employee': employee})
            if employee.payslip_set.exists():
                messages.error(request, 'Cannot change ID Number because this employee already has payslips.')
                return render(request, 'payroll_app/update_employee.html', {'employee': employee})
        employee.id_number = id_number
        rate_input = float(request.POST.get('rate'))
        if rate_input <= 0:
            messages.error(request, 'Rate must be greater than 0.')
            return render(request, 'payroll_app/update_employee.html', {'employee': employee})
        employee.rate = rate_input
        allowance = request.POST.get('allowance') or None
        if allowance is not None:
            allowance = float(allowance)
            if allowance < 0:
                messages.error(request, 'Allowance must be 0 or greater.')
                return render(request, 'payroll_app/update_employee.html', {'employee': employee})
        employee.allowance = allowance
        employee.save()
        return redirect('home')
    else:
        return render(request, 'payroll_app/update_employee.html', {'employee': employee})

@login_required(login_url='login')
def payslips(request):
    employees = Employee.objects.all()
    error_messages = []
    cycle_filter = request.GET.get('cycle_filter', 'all')
    employee_filter = request.GET.get('employee_filter', 'all')

    # ✅ Employee user - only see their own payslips
    if not request.user.is_staff:
        try:
            linked_employee = Employee.objects.get(user=request.user)
            payslips = Payslip.objects.filter(id_number=linked_employee)
        except Employee.DoesNotExist:
            payslips = Payslip.objects.none()
        return render(request, 'payroll_app/payslips.html', {
            'employees': employees,
            'payslips': payslips,
            'error_messages': error_messages,
            'cycle_filter': cycle_filter,
            'employee_filter': employee_filter,
            'is_employee': True
        })

    payslips = Payslip.objects.all()
    if cycle_filter == '1':
        payslips = payslips.filter(pay_cycle=1)
    elif cycle_filter == '2':
        payslips = payslips.filter(pay_cycle=2)
    if employee_filter != 'all':
        payslips = payslips.filter(id_number__id_number=employee_filter)

    if request.method == 'POST':
        payroll_for = request.POST.get('payroll_for')
        if not payroll_for:
            messages.error(request, 'Please select an Employee or All Employees.')
            return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips, 'error_messages': error_messages, 'cycle_filter': cycle_filter, 'employee_filter': employee_filter})
        month = request.POST.get('month')
        if not month:
            messages.error(request, 'Please select a month.')
            return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips, 'error_messages': error_messages, 'cycle_filter': cycle_filter, 'employee_filter': employee_filter})
        year = request.POST.get('year')
        if not year:
            messages.error(request, 'Please enter a year.')
            return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips, 'error_messages': error_messages, 'cycle_filter': cycle_filter, 'employee_filter': employee_filter})
        if not year.isdigit() or len(year) != 4:
            messages.error(request, 'Please enter a valid 4-digit year.')
            return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips, 'error_messages': error_messages, 'cycle_filter': cycle_filter, 'employee_filter': employee_filter})
        year_input = int(year)
        cycle = request.POST.get('cycle')
        if not cycle:
            messages.error(request, 'Please select a cycle.')
            return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips, 'error_messages': error_messages, 'cycle_filter': cycle_filter, 'employee_filter': employee_filter})
        cycle = int(cycle)
        if cycle == 1:
            date_range = '1-15'
        else:
            date_range = '16-30'
        if payroll_for == 'all':
            selected_employees = Employee.objects.all()
        else:
            selected_employees = Employee.objects.filter(id_number=payroll_for)
        for employee in selected_employees:
            existing = Payslip.objects.filter(id_number=employee, month=month, year=year, pay_cycle=cycle).exists()
            if existing:
                error_messages.append('Payslip for {} ({} {} Cycle {}) already exists.'.format(employee.id_number, month, year, cycle))
                continue
            rate = employee.rate
            allowance = employee.allowance or 0
            overtime = employee.overtime_pay or 0
            if cycle == 1:
                pag_ibig = 100
                philhealth = 0
                sss = 0
                tax = ((rate / 2) + allowance + overtime - pag_ibig) * 0.2
                total_pay = ((rate / 2) + allowance + overtime - pag_ibig) - tax
            else:
                pag_ibig = 0
                philhealth = rate * 0.04
                sss = rate * 0.045
                tax = ((rate / 2) + allowance + overtime - philhealth - sss) * 0.2
                total_pay = ((rate / 2) + allowance + overtime - philhealth - sss) - tax
            Payslip.objects.create(id_number=employee, month=month, date_range=date_range, year=year, pay_cycle=cycle, rate=rate,
                               earnings_allowance=allowance, deductions_tax=tax, deductions_health=philhealth, pag_ibig=pag_ibig,
                               sss=sss, overtime=overtime, total_pay=total_pay)
            employee.resetOvertime()
        payslips = Payslip.objects.all()
        if cycle_filter == '1':
            payslips = payslips.filter(pay_cycle=1)
        elif cycle_filter == '2':
            payslips = payslips.filter(pay_cycle=2)
        if employee_filter != 'all':
            payslips = payslips.filter(id_number__id_number=employee_filter)

    return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips, 'error_messages': error_messages, 'cycle_filter': cycle_filter, 'employee_filter': employee_filter})

@login_required(login_url='login')
def view_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    if not request.user.is_staff:
        try:
            linked_employee = Employee.objects.get(user=request.user)
            if payslip.id_number != linked_employee:
                return redirect('payslips')
        except Employee.DoesNotExist:
            return redirect('payslips')
    return render(request, 'payroll_app/view_payslip.html', {'payslip': payslip})