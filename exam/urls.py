from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
    path('mock/register/', views.register_mock_view, name='register_mock'),
    path('final/access/', views.final_access_view, name='final_access'),
    path('final/register/', views.register_final_view, name='register_final'),
    path('exam/<int:session_id>/', views.exam_view, name='exam_start'),
    path('done/', views.done_view, name='exam_done'),
    
    # Admin va Excel yo'llari
    path('results/', views.admin_results_view, name='admin_results'),
    path('export/', views.export_excel_view, name='export_excel'),
]