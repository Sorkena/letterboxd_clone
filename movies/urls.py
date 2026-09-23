from django.urls import path
from . import views

urlpatterns = [
    path('', views.MovieViewSet.as_view({'get': 'list'}), name='movies'),
    path('film/<slug:slug>/', views.MovieViewSet.as_view({'get': 'retrieve'}), name='movie_detail'),
    path('film/<slug:slug>/watchlist/add/', views.MovieViewSet.as_view({'post': 'watchlist_add'}), name='watchlist_add'),
    path('film/<slug:slug>/watchlist/remove/', views.MovieViewSet.as_view({'post': 'watchlist_remove'}), name='watchlist_remove'),
    path('film/<slug:slug>/rating/update/', views.MovieViewSet.as_view({'post': 'update_rating'}), name='rating_update'),
    path('film/<slug:slug>/rating/delete/', views.MovieViewSet.as_view({'post': 'delete_rating'}), name='rating_delete'),
    path('film/<slug:slug>/review/add/', views.MovieViewSet.as_view({'post': 'add_review'}), name='review_add'),
    path('film/<slug:slug>/list/add/', views.MovieViewSet.as_view({'post': 'add_to_custom_list'}), name='add_to_custom_list'),
    path('film/<slug:slug>/review/<int:review_id>/edit/', views.ReviewViewSet.as_view({'get': 'edit'}), name='review_edit'),
    path('film/<slug:slug>/review/<int:review_id>/update/', views.ReviewViewSet.as_view({'post': 'update_review'}), name='review_update'),
    path('film/<slug:slug>/review/<int:review_id>/delete/', views.ReviewViewSet.as_view({'post': 'delete_review'}), name='review_delete'),
]