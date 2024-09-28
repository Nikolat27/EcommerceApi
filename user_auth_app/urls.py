from . import views
from django.urls import path

app_name = "user_auth_app"
urlpatterns = [
    path("register", views.UserRegisterView.as_view(), name="user_register"),
    path("login", views.UserLoginView.as_view(), name="user_login"),
    path("logout", views.UserLogoutView.as_view(), name="user_logout"),
]
