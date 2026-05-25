from django.urls import path, include
from .views import RootHomeView, HomeView

urlpatterns = [
    path('', RootHomeView.as_view(), name='root_home'),
    path('home/', HomeView.as_view(), name='home'),
]
