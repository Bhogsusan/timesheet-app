# timesheet/urls.py (updated)
from django.urls import path
from . import views

urlpatterns = [
    # Timesheet URLs
    path('', views.TimesheetListView.as_view(), name='timesheet_list'),
    path('create/', views.create_timesheet, name='create_timesheet'),
    path('timesheet/<int:pk>/', views.timesheet_detail, name='timesheet_detail'),
    path('timesheet/<int:pk>/excel/', views.generate_excel, name='generate_excel'),
    path('timesheet/<int:pk>/delete/', views.delete_timesheet, name='delete_timesheet'),
    
    # Company Management URLs (Website)
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/add/', views.CompanyCreateView.as_view(), name='company_add'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    
    # API
    path('api/company-preview/', views.get_company_preview, name='company_preview'),
]