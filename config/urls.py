from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    # path("blog/", include("blog.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),

    path('api/v1/', include([
        path('auth/', include(('aaa.urls.auth_urls', 'auth'), namespace='auth')),
        path('pcb/', include(('pcb.urls', 'pcb'), namespace='pcb')),
        path("blog/", include("blog.urls")),
    ])),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)