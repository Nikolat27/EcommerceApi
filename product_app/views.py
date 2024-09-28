from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from . import serializers
from rest_framework.response import Response

from product_app.models import Product
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
        return self.paginate_queryset(serializer.data)

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
