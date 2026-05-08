from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('update_employee/<int:pk>/', views.update_employee, name='update_employee'),
    path('delete_employee/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('add_overtime/<int:pk>/', views.add_overtime, name='add_overtime'),
    path('payslips/', views.payslips, name='payslips'),
    path('view_payslip/<int:pk>/', views.view_payslip, name='view_payslip'),
]