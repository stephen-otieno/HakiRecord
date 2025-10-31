from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='homepage'),
    path('statement/', views.record_statement, name='statement'),
    path('login/', views.login_fn, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cases/', views.view_cases, name='cases'),
    path('recent-actions/', views.recent_actions, name='recent_actions'),
    path('contact/', views.contact, name='contact'),
    path('evidence/', views.evidence_vault, name='evidence'),

    path('shift/', views.shift_allocation, name='shift'),
    path('login_success/', views.login_success, name='login_success'),
    path('crime-analysis/', views.crime_analysis, name='crime_analysis'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('cases/<int:pk>/pdf/', views.generate_case_pdf, name='generate_case_pdf'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)