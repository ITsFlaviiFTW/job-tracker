"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from jobtracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobtracker.urls')),

    # reset password paths
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(
           template_name='jobtracker/password_reset_form.html'),
         name='password_reset'),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
           template_name='jobtracker/password_reset_done.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
           template_name='jobtracker/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
           template_name='jobtracker/password_reset_complete.html'),
         name='password_reset_complete'),


    path('job/<int:pk>/detail-json/',views.job_detail_json,  name='job_detail_json'),
    path('job/<int:pk>/update-ajax/',views.job_update_ajax,  name='job_update_ajax'),


    path('explore-jobs/', views.explore_jobs, name='explore_jobs'),
    path('save-remote-job/', views.save_remote_job, name='save_remote_job'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
