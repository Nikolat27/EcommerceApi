from . import views
from django.urls import path

app_name = "product_app"
urlpatterns = [
    path("reviews/<int:pk>", views.ReviewProductView.as_view(), name="reviews"),
    path("comments", views.CommentProductView.as_view(), name="comments")
]
