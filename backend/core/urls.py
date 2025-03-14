# backend\core\urls.py:

"""
URL configuration for project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("user.urls")),
    path("api/", include("organization.urls")),
    path("api/", include("message.urls")),
    path("api/", include("chat.urls")),
    #
    path("spectacular-download/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "spectacular-swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("spectacular-redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path(
        "spectacular-rapidoc/",
        TemplateView.as_view(
            template_name="rapidoc.html", extra_context={"schema_url": "schema"}
        ),
        name="rapidoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
