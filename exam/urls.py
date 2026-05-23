from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
    path('mock/register/', views.register_mock_view, name='register_mock'),
    
    # English Session uchun yangi yo'l
    path('english/register/', views.register_english_view, name='register_english'),
    
    path('final/access/', views.final_access_view, name='final_access'),
    path('final/register/', views.register_final_view, name='register_final'),
    
    # Imtihon topshirish oynasi
    path('exam/<int:session_id>/', views.exam_view, name='exam_start'),
    path('done/', views.done_view, name='exam_done'),
    
    # --- CHEATING'GA QARSHI YANGI URL YO'LLARI ---
    path('exam/<int:session_id>/block/', views.block_session_view, name='block_session'),
    path('exam/<int:session_id>/restricted/', views.restricted_view, name='restricted_view'),
    
    # Yangi maxsus O'qituvchi login sahifasi yo'li
    path('teacher/login/', views.teacher_login_view, name='teacher_login'),
    
    # Admin va Excel yo'llari
    path('results/', views.admin_results_view, name='admin_results'),
    path('export/', views.export_excel_view, name='export_excel'),
]