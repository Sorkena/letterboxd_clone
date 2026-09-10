from django.urls import path

from . import views

urlpatterns = [
    path('', views.MovieListView.as_view(), name='movies'),
    path('film/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
]