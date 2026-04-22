from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('employee/create/', views.create_employee, name='create_employee'),
    path('employee/update/<str:id_number>/', views.update_employee, name='update_employee'),
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/<int:pk>/', views.view_payslip, name='view_payslip'),
]