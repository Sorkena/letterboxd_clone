from django.urls import path
from .views import HomeViewSet

urlpatterns = [
    path('', HomeViewSet.as_view({'get': 'home'}), name='home'),
    path('register/', HomeViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', HomeViewSet.as_view({'post': 'login'}), name='login'),
    path('onboarding/', HomeViewSet.as_view({'get': 'onboarding_get','post': 'onboarding_post'}), name='onboarding'),
]