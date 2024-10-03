from . import views
from django.urls import path

app_name = "cart_app"
urlpatterns = [
    path("cart_page", views.CartPageView.as_view(), name="cart_page"),
    path("add_to_cart/<int:pk>", views.AddCartView.as_view(), name="add_to_cart"),
    path("update_cart/<int:pk>", views.UpdateCardView.as_view(), name="update_cart"),
    path("delete_cart/<int:pk>", views.DeleteCartView.as_view(), name="delete_cart"),
    path("delete_whole_cartitems", views.DeleteWholeCart.as_view(), name="delete_whole_cartitems"),
    path("view_order", views.OrderPageView.as_view(), name="view_order_page"),
    path("create_order", views.OrderCreateView.as_view(), name="create_order_view"),
    path("update_order/<int:pk>", views.OrderUpdateView.as_view(), name="update_order_view"),
    path("delete_order/<int:pk>", views.OrderDeleteView.as_view(), name="delete_order_view"),
    path("create_order_item", views.OrderItemCreateView.as_view(), name="create_orderItem_view"),
    path("update_order_item/<int:pk>", views.OrderItemUpdateView.as_view(), name="update_orderItem_view"),
    path("delete_order_item/<int:pk>", views.OrderItemDeleteView.as_view(), name="delete_orderItem_view"),
]