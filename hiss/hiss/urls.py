"""hiss URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/

Examples
--------
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
from django import http
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView


def healthcheck(request):
    return http.HttpResponse("")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("customauth.urls")),
    path("application/", include("application.urls", namespace="application")),
    path("healthy/", healthcheck),
    url(r"^$", RedirectView.as_view(pattern_name="customauth:login")),
    path("status/", include("status.urls")),
    path("team/", include("team.urls")),
    path("api/volunteer/", include("volunteer.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
