from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Sum, Count
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
import time
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from . import serializers
from rest_framework.response import Response
from product_app.models import (
    Product,
    Review,
    Comment,
    ProductLike,
    ReviewAction,
    CommentAction,
)
from .permissions import IsAuthenticatedOrReadOnly


# Create your views here.


class ProductViewSet(ViewSet, PageNumberPagination):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        products = Product.objects.all().order_by("-id")
        size = request.GET.get("size", 1)
        # filtering parameters
        categories = request.GET.getlist("category")
        brands = request.GET.getlist("brand")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        colors = request.GET.getlist("colors")
        sort_by = request.GET.get("sort_by")
        order_by = request.GET.get("order_by")

        if categories and len(categories) > 0:
            products = products.filter(category__title__in=categories)
        
        if brands and len(brands) > 0:
            products = products.filter(brand__title__in=brands)

        if min_price and max_price:
            products = products.filter(price__gte=min_price, price__lte=max_price)
        
        if colors and len(colors) > 0:
            products = products.filter(product_color__color__title__in=colors)

        if sort_by == "is_discounted":
            products = products.filter(enable_discount=True)
        elif sort_by == "available":
            products = products.filter(product_color__in_stock=True)

        if order_by == "new":
            products = products.order_by("-created_at")
        elif order_by == "old":
            products = products.order_by("created_at")
        elif order_by == "most_popular":
            products = products.annotate(rating=Avg("reviews__rating")).order_by("rating")
        elif order_by == "least_popular":
            products = products.annotate(rating=Avg("reviews__rating")).order_by("-rating")
        elif order_by == "asc": # lowest value to the highest value
            products = products.order_by("price")
        elif order_by == "dsc": # highest value to the lowest value
            products = products.order_by("-price")
        
        self.page_size = int(size)
        paginated_queryset = self.paginate_queryset(queryset=products.distinct(), request=request)
        serializer = serializers.ProductSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        product = get_object_or_404(Product, slug=pk)
        product_serializer = serializers.ProductSerializer(instance=product, many=False)
        related_products = Product.objects.filter(category__in=product.category.all())
        rp = {}
        for product in related_products:
            rp["title"] = product.title,
            rp["slug"] = product.slug,
            rp["thumbnail"] = product.thumbnail.path
            rp["discounted_price"] = product.discounted_price(),
        
        return Response(
            {
                "product": product_serializer.data,
                "related_products": rp,
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request):
        serializer = serializers.ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"data": "Product Created successfully!"}, status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = get_object_or_404(Product, id=pk)
        serializer = serializers.ProductSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=instance, validated_data=serializer.validated_data)
        return Response(
            {"response": "Your Course has been updated successfully"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk=None):
        Product.objects.get(id=pk).delete()
        return Response(
            {"data": "Product Deleted successfully!"}, status=status.HTTP_200_OK
        )


class ReviewProductView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk=None):
        reviews = Review.objects.filter(product_id=pk).order_by("-id")
        serializer = serializers.ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk=None):
        data = request.POST
        text = data.get("text")
        author = request.user
        rating = request.get("rating")
        Review.objects.create(author=author, product_id=pk, text=text, rating=rating)
        return Response(
            {"data": "Review added successfully"}, status=status.HTTP_201_CREATED
        )


class CommentProductView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, pk=None):
        comments = Comment.objects.filter(product_id=pk).order_by("-id")
        serializer = serializers.CommentSerializer(comments, many=True)
        serializer.is_valid(raise_exception=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk=None):
        data = request.POST
        author = request.user
        text = data.get("text")
        parent_id = data.get("parent_id")
        if not parent_id:
            Comment.objects.create(author=author, product_id=pk, text=text)
        else:
            Comment.objects.create(
                author=author, product_id=pk, text=text, parent_id=parent_id
            )
        return JsonResponse(
            {"data": "Comment Created successfully"}, status=status.HTTP_201_CREATED
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def product_like(request, pk):
    try:
        product = ProductLike.objects.get(product_id=pk, user=request.user)
        product.delete()
        return Response({"data": "Product Disliked!"}, status=status.HTTP_201_CREATED)
    except ProductLike.DoesNotExist:
        Product.objects.create(product_id=pk, user=request.user)
        return Response({"data": "Product Liked!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_action(request, pk, action):
    if action not in ["like", "dislike"]:
        return Response(
            {
                "response": "Invalid action! your action_type must be either 'like' or 'dislike'"
            }
        )
    review, created = ReviewAction.objects.get_or_create(
        review_id=pk, user=request.user, defaults={"action_type": action}
    )
    if not created:
        review.action_type = action
        review.save()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def comment_action(request, pk, action):
    if action not in ["like", "dislike"]:
        return Response(
            {
                "response": "Invalid action! your action_type must be either 'like' or 'dislike'"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    comment, created = CommentAction.objects.get_or_create(
        comment_id=pk, user=request.user, defaults={"action_type": action}
    )
    if not created:
        comment.action_type = action
        comment.save()

    return Response(
        {"response": "your action submitted successfully!"}, status=status.HTTP_200_OK
    )
