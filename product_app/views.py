from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from . import serializers
from rest_framework.response import Response

from product_app.models import Product, Review, Comment
from .permissions import IsAuthenticatedOrReadOnly


# Create your views here.


class ProductViewSet(ViewSet, PageNumberPagination):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        queryset = Product.objects.all().order_by("-id")
        size = request.GET.get("size", 1)
        self.page_size = int(size)
        paginated_queryset = self.paginate_queryset(queryset=queryset, request=request)
        serializer = serializers.ProductSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        product = get_object_or_404(Product, slug=pk)
        serializer = serializers.ProductSerializer(instance=product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = serializers.ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": "Product Created successfully!"}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        instance = get_object_or_404(Product, id=pk)
        serializer = serializers.ProductSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=instance, validated_data=serializer.validated_data)
        return Response({"response": "Your Course has been updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        Product.objects.get(id=pk).delete()
        return Response({"data": "Product Deleted successfully!"}, status=status.HTTP_200_OK)


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
        return Response({"data": "Review added successfully"}, status=status.HTTP_201_CREATED)


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
            Comment.objects.create(author=author, product_id=pk, text=text, parent_id=parent_id)
        return JsonResponse({"data": "Comment Created successfully"}, status=status.HTTP_201_CREATED)
