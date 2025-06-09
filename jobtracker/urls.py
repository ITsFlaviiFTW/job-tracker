from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.job_list, name='job_list'),
    path('add/', views.job_create, name='job_create'),
    path('edit/<int:pk>/', views.job_update, name='job_update'),
]
