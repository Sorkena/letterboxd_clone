from django.urls import path

from . import views

urlpatterns = [
    path('', views.MovieViewSet.as_view({'get': 'list'}), name='movies'),
    path('film/<slug:slug>/', views.MovieViewSet.as_view({'get': 'retrieve', 'post': 'detail_post'}), name='movie_detail'),
    path('film/<slug:slug>/review/<int:review_id>/edit/',views.ReviewViewSet.as_view({'get': 'edit', 'post': 'edit_post'}),name='review_edit'),
]