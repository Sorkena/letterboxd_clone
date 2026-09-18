from django.urls import path
from . import views

urlpatterns = [
    path('', views.UsersViewSet.as_view({'get': 'list'}), name='users'),
    path('profile/<str:username>/', views.UserProfileViewSet.as_view({'get': 'profile'}), name='user_profile'),
    path('lists/create/', views.CustomListViewSet.as_view({'get': 'create_list', 'post': 'create_list'}), name='custom_list_create'),
    path('lists/<str:username>/<int:list_id>/', views.CustomListViewSet.as_view({'get': 'retrieve', 'post': 'retrieve'}), name='custom_list_detail'),
    path('lists/<str:username>/<int:list_id>/edit/', views.CustomListViewSet.as_view({'get': 'edit', 'post': 'edit'}), name='custom_list_edit'),
]