from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePageListView.as_view(), name="home"),
    path("room/<str:pk>", views.RoomPageView.as_view(), name="room"),
    path("create-room", views.CreateRoom.as_view(), name="create-room"),
    path("update-room/<str:pk>/", views.UpdateRoomView.as_view(), name="update-room"),
    path("delete-room/<str:pk>/", views.DeleteRoomView.as_view(), name="delete-room"),
    path("delete-message/<str:pk>/",
         views.DeleteMessageView.as_view(), name="delete-message"),
    path("user-profile/<str:pk>/",
         views.UserProfileListView.as_view(), name="user-profile"),
    path("update-user/", views.UpdateUser.as_view(), name="update-user"),
    path("topics/", views.TopicsPage.as_view(), name="topics"),
    path("activity/", views.ActivityPage.as_view(), name="activity"),
    path("logout/", views.LogoutUser.as_view(), name="logout"),
]
