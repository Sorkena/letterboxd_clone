from django.urls import path
from . import views

urlpatterns = [
    path('', views.UsersViewSet.as_view({'get': 'list'}), name='users'),
    path('profile/<str:username>/', views.UserProfileViewSet.as_view({'get': 'profile'}), name='user_profile'),
    path('lists/create/', views.CustomListViewSet.as_view({'get': 'create_list'}), name='custom_list_create'),
    path('lists/create/save/', views.CustomListViewSet.as_view({'post': 'save_list'}), name='custom_list_save'),
    path('lists/<str:username>/<int:list_id>/', views.CustomListViewSet.as_view({'get': 'retrieve'}), name='custom_list_detail'),
    path('lists/<str:username>/<int:list_id>/remove-movie/', views.CustomListViewSet.as_view({'post': 'remove_movie'}), name='remove_movie'),
    path('lists/<str:username>/<int:list_id>/edit/', views.CustomListViewSet.as_view({'get': 'edit'}), name='custom_list_edit'),
    path('lists/<str:username>/<int:list_id>/update/', views.CustomListViewSet.as_view({'post': 'update_list'}), name='custom_list_update'),
    path('lists/<str:username>/<int:list_id>/delete/', views.CustomListViewSet.as_view({'post': 'delete_list'}), name='custom_list_delete'),
    path('profile/<str:username>/follow/', views.FollowViewSet.as_view({'post': 'follow'}), name='follow_user'),
    path('profile/<str:username>/unfollow/', views.FollowViewSet.as_view({'post': 'unfollow'}), name='unfollow_user'),
    path('profile/<str:username>/followers/', views.FollowViewSet.as_view({'get': 'followers'}), name='user_followers'),
    path('profile/<str:username>/following/', views.FollowViewSet.as_view({'get': 'following'}), name='user_following'),
    path('profile/<str:username>/watched/',views.UserProfileViewSet.as_view({'get': 'watched'}),name='user_watched'),
    path(
    'profile/<str:username>/watched/',views.UserProfileViewSet.as_view({'get': 'watched'}),name='user_watched'),
    path('profile/<str:username>/watchlist/',views.UserProfileViewSet.as_view({'get': 'watchlist'}),name='user_watchlist'),
    path('profile/<str:username>/reviews/',views.UserProfileViewSet.as_view({'get': 'reviews'}),name='user_reviews'),
    path('profile/<str:username>/lists/',views.CustomListViewSet.as_view({'get': 'all_lists'}),name='user_custom_lists'
),
]