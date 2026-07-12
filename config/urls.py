from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    # path("blog/", include("blog.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),

    path('api/v1/', include([
        path('auth/', include(('aaa.urls.auth_urls', 'aaa'), namespace='aaa')),
        path('pcb/', include(('pcb.urls', 'pcb'), namespace='pcb')),
        path('sls/', include(('sls.urls', 'sls'), namespace='sls')),
        # path('accounting/', include(('accounting.urls', 'accounting'), namespace='accounting')),
        # path('wh/', include(('wh.urls', 'wh'), namespace='wh')),
        path("blog/", include("blog.urls")),
        path('support/', include(('support.urls', 'support'), namespace='support')),
    ])),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)