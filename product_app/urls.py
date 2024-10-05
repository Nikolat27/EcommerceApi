from . import views
from django.urls import path

app_name = "product_app"
urlpatterns = [
    path("reviews/<int:pk>", views.ReviewProductView.as_view(), name="reviews"),
    path("comments", views.CommentProductView.as_view(), name="comments"),
    path("product_like/<int:pk>", views.product_like, name="product_like"),
    path("review_action/<int:pk>/<str:action>", views.review_action, name="review_action"),
    path("comment_action/<int:pk>/<str:action>", views.comment_action, name="comment_action"),
    path("clear_filters", views.clear_filters, name="clear_filters"),
]
