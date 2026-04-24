from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('exam/<int:session_id>/', views.exam_view, name='exam_start'),
    path('done/', views.done_view, name='exam_done'),
    path('admin-results/', views.admin_results_view, name='admin_results'),
    path('admin-results/export/', views.export_excel_view, name='export_excel'),
]