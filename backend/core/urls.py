# backend\core\urls.py:

"""
URL configuration for project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Backend Project API",
        default_version="v1",
        description="API documentation for backend project",
        # terms_of_service="https://www.DaITBackend.com/backend/policies/terms/",
        contact=openapi.Contact(email="djamalov.aziz.mansurovich@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            [
                path("", include("management.urls")),
                path("", include("organization.urls")),
                path("", include("message.urls")),
            ]
        ),
    ),
    # path(
    #     "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"
    # ),
    # path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
    # re_path(
    #     r"^swagger(?P<format>\.json|\.yaml)$",
    #     schema_view.without_ui(cache_timeout=0),
    #     name="schema-json",
    # ),
]
