from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('employee/delete/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('employee/add_overtime/<int:pk>/', views.add_overtime, name='add_overtime'),
    path('employee/create/', views.create_employee, name='create_employee'),
    path('employee/update/<int:pk>/', views.update_employee, name='update_employee'),
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/view/<int:pk>/', views.view_payslip, name='view_payslip'),
]