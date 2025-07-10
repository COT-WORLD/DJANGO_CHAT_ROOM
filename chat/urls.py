from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('room/<int:pk>/', views.room_view, name='room'),
    path("create-room/", views.CreateRoom.as_view(), name="create-room"),
    path("update-room/<str:pk>/", views.UpdateRoomView.as_view(), name="update-room"),
    path("delete-room/<int:pk>/", views.delete_room, name="delete-room"),

    path('delete-message/<int:pk>/', views.delete_message, name='delete-message'),

    path('profile/<int:pk>/', views.user_profile_view, name='user-profile'),
    path('update-user/', views.update_user, name='update-user'),

    path('topics/', views.topics_page, name='topics'),
    path('activity/', views.activity_page, name='activity'),

    path('logout/', views.logout_user, name='logout'),
]
