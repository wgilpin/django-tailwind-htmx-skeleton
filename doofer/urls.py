"""
URL configuration for doofer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from doofer.doofer.views import views as core_views
from doofer.doofer.views import auth_views

urlpatterns = [
    path("", core_views.index, name="index"),
    path("login/", auth_views.login_user, name="login"),
    path("logout/", auth_views.logout_user, name="logout"),
    path("register/", auth_views.register_user, name="logout"),
    path("profile/", auth_views.profile, name="profile"),
    path("note/<int:id_>/edit", core_views.note_edit, name="note_edit"),
    path("note/<int:id_>/", core_views.note_details, name="note_details"),
    path("search/", core_views.search, name="search"),
    path("admin/", admin.site.urls),
    path("api/", include("doofer.api.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    # auth urls for dj-rest-auth, including login, logout, password reset, etc.
    path("auth/", include("dj_rest_auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
