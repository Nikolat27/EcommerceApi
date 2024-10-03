from . import views
from django.urls import path

app_name = "cart_app"
urlpatterns = [
    path("cart_page", views.CartPageView.as_view(), name="cart_page"),
    path("add_to_cart/<int:pk>", views.AddCartView.as_view(), name="add_to_cart"),
    path("update_cart/<int:pk>", views.UpdateCardView.as_view(), name="update_cart"),
    path("delete_cart/<int:pk>", views.DeleteCartView.as_view(), name="delete_cart"),
    path("delete_whole_cartitems", views.DeleteWholeCart.as_view(), name="delete_whole_cartitems"),
]