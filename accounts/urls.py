from django.urls import path
from .views import login_view, logout_view, register_view, profile, change_password, edit_profile

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path("profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("profile/edit/", edit_profile, name="edit_profile"),
]
