from django.urls import path
from .views import BlogCategoryAutocomplete, GuidPostDetailApiView, BlogCategoryViewSet, NotifViewSet
from rest_framework.routers import DefaultRouter

app_name = 'blog'
urlpatterns = [
    path(
        'category-autocomplete/',
        BlogCategoryAutocomplete.as_view(),
        name='category-autocomplete',
    ),
    # path('guid/list/<int:caterory>/', GuidPostDetailApiView.as_view(), name='guide.list'),
    path('guid/<slug:slug>/', GuidPostDetailApiView.as_view(), name='guid-detail'),
]

router = DefaultRouter()
router.register(r'category/list', BlogCategoryViewSet, basename='blogcategory')
router.register(r'notif', NotifViewSet, basename='notif')

urlpatterns += router.urls
