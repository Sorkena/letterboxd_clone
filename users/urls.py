from django.urls import path

from . import views

urlpatterns = [
    path('', views.users, name='users'),
    path('<str:username>/', views.user_profile, name='user_profile'),
]