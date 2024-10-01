from . import views
from django.urls import path

app_name = "cart_app"
urlpatterns = [
    path("add_to_cart/<int:pk>", views.AddCartView.as_view(), name="add_to_cart")
]