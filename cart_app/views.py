from django.shortcuts import render
from rest_framework.views import APIView
from .models import Cart, CartItem
from product_app.models import Product
import random
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


def getCart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.GET.get("session_id") or random.randint(1000000, 9999999)
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart

def getProduct(pk):
    try:
        return Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return None
    
class AddCartView(APIView):
    permission_classes = [AllowAny]

    def add_product_to_cart(cart, product, color, quantity):
        cart.cart_items.create(
            product=product,
            color=color,
            quantity=quantity,
            price=product.discounted_price(),
        )

    def get(self, request, pk):
        cart = getCart(request)
        product = getProduct(pk)

        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        product_color = product.product_color.filter(in_stock=True).first()
        
        try:
            quantity = int(request.GET.get("quantity", 1))
        except ValueError:
            return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        self.add_product_to_cart(cart, product, product_color.color, quantity)

        return Response({"response": "Product added to your cart successfully!"}, status=status.HTTP_200_OK)

    def post(self, request, pk):
        cart = getCart(request)
        product = getProduct(pk)

        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        color = request.POST.get("color")
        
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        if not color:
            return Response({"error": "Color is required."}, status=status.HTTP_400_BAD_REQUEST)

        self.add_product_to_cart(cart, product, color, quantity)

        return Response({"response": "Product added to your cart successfully!"}, status=status.HTTP_200_OK)
