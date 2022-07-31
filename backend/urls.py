from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("schema/", get_schema_view(
        title="That1Mango", description="API for That1Mango", version="1.0.0"),
        name="openapi-schema"
    ),
    path("docs/", include_docs_urls(title="That1Mango")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls", namespace="users")),
    path("api/titles/", include("title.urls", namespace="titles")),
    path("api/social/", include("social.urls", namespace="social"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
