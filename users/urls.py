from django.urls import path

from . import views

urlpatterns = [
    path('', views.UsersListView.as_view(), name='users'),
    path('liste-olustur/', views.CustomListCreateView.as_view(), name='custom_list_create'),
    path('<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    path('<str:username>/liste/<int:list_id>/', views.CustomListDetailView.as_view(), name='custom_list_detail'),
    path('<str:username>/lists/<int:list_id>/edit/', views.CustomListUpdateView.as_view(), name='custom_list_edit'),
    path('<str:username>/lists/<int:list_id>/delete/', views.CustomListDeleteView.as_view(), name='custom_list_delete'),
]