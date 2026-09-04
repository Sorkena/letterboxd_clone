from django.urls import path

from . import views

urlpatterns = [
    path('', views.movies, name="movies"),
    path('film/<slug:slug>/', views.movie_detail, name='movie_detail'),
]