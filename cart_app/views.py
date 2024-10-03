from django.shortcuts import render
from rest_framework.views import APIView
from .models import Cart, CartItem, Order, OrderItem, Coupon
from product_app.models import Product
import random
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import OnlyPostMethod
from rest_framework.response import Response
from rest_framework import status
from . import serializers

# Create your views here.


def getCart(request, page_view=None):
    if page_view is True:
        session_id = (
            request.GET.get("session_id") or request.POST.get("session_id") or None
        )
        try:
            if session_id:
                cart = Cart.objects.get(session_id=session_id)
            else:
                cart = Cart.objects.get(user=request.user)

            return cart
        except Cart.DoesNotExist:
            return None

    session_id = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = (
            request.GET.get("session_id")
            or request.POST.get("session_id")
            or random.randint(1000000, 9999999)
        )
        print(session_id)
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return (cart, session_id) if session_id else (cart, None)


def getProduct(pk):
    try:
        return Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return None


class CartPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart = getCart(request, page_view=True)
        if cart:
            serializer = serializers.CartSerializer(instance=cart, many=False)
            return Response({"response": serializer.data}, status=status.HTTP_200_OK)
        return Response({"response": "Your cart is empty!"}, status=status.HTTP_200_OK)


class AddCartView(APIView):
    permission_classes = [AllowAny]

    def add_product_to_cart(self, cart, product, color, quantity):
        cartItem_product_checking = CartItem.objects.filter(
            cart=cart, product=product, color=color
        ).first()
        if cartItem_product_checking:
            cartItem_product_checking.quantity += quantity
            cartItem_product_checking.save()
        else:
            cart.cart_items.create(
                product=product,
                color=color,
                quantity=quantity,
                price=product.discounted_price(),
            )

    def get(self, request, pk):
        cart, session_id = getCart(request)
        product = getProduct(pk)

        if not product:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        product_color = product.product_color.filter(in_stock=True).first()

        try:
            quantity = int(request.GET.get("quantity", 1))
        except ValueError:
            return Response(
                {"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST
            )

        self.add_product_to_cart(cart, product, product_color.color, quantity)

        response = {
            "response": "Product added to your cart successfully",
            "session_id": session_id if session_id else None,
        }

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, pk):
        cart, session_id = getCart(request)
        product = getProduct(pk)

        if not product:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        color = request.POST.get("color")

        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            return Response(
                {"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not color:
            return Response(
                {"error": "Color is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        self.add_product_to_cart(cart, product, color, quantity)

        response = {
            "response": "Product added to your cart successfully",
            "session_id": session_id if session_id else None,
        }

        return Response(response, status=status.HTTP_200_OK)


class UpdateCardView(APIView):
    permission_classes = [OnlyPostMethod]

    def post(self, request, pk):
        quantity = request.POST.get("quantity")
        cart_item = CartItem.objects.get(id=pk)
        cart_item.quantity += quantity
        cart_item.save()
        return Response(
            {"response": "Product updated successfully"}, status=status.HTTP_200_OK
        )


class DeleteCartView(APIView):
    permission_classes = [AllowAny]

    def get(self, pk):
        cart_item = CartItem.objects.get(id=pk).delete()
        return Response(
            {"response": "Product deleted successfully!"}, status=status.HTTP_200_OK
        )


class DeleteWholeCart(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart, session_id = getCart(request)
        print(cart)
        print("session_id", session_id)
        cart.cart_items.all().delete()
        return Response(
            {"response": "Cart Items deleted successfully!"}, status=status.HTTP_200_OK
        )


class OrderPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order = Order.objects.get(user=request.user)
        serializer = serializers.OrderSerializer(instance=order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"response": "Your Order is created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class OrderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        serializer = serializers.OrderSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=order, validated_data=serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        Order.objects.get(id=pk).delete()
        return Response(
            {"response": "Your order deleted successfully!"}, status=status.HTTP_200_OK
        )


class OrderItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.OrderItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"response": "Your OrderItem is created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class OrderItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order_item = OrderItem.objects.get(id=pk)
        serializer = serializers.OrderItemSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=order_item, validated_data=serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        OrderItem.objects.get(id=pk).delete()
        return Response(
            {"response": "Your order item deleted successfully!"},
            status=status.HTTP_200_OK,
        )
