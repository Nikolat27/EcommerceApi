import redis
from django.shortcuts import render
from rest_framework.views import APIView
from .models import Cart, CartItem, Order, OrderItem, Coupon, Reserve
from product_app.models import Product, ProductColor
import random
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.utils.timezone import timedelta
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError

# Create your views here.

redis_client = redis.Redis(host="127.0.0.1:6379", db=0)

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
        order = serializer.save()
        cart_items = CartItem.objects.filter(cart__user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                color=item.color,
                quantity=item.quantity,
                price=item.price,
            )

        cart_items.delete()
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

    # class OrderItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # serializer = serializers.OrderItemSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        data = request.POST
        order = data.get("order")
        product = data.get("product")
        color = data.get("color")
        quantity = data.get("quantity")
        price = data.get("price")
        OrderItem.objects.create(
            order_id=order,
            product_id=product,
            color_id=color,
            quantity=quantity,
            price=price,
        )
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


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def apply_coupon(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order.coupon_used:
        return Response(
            {"response": "This order has already used a coupon!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = request.POST.get("coupon_code")
    coupon = get_object_or_404(Coupon, code=code)

    if not (coupon.is_enable and coupon.max_usage <= coupon.used_by):
        return Response(
            {
                "response": "This coupon is either disabled or has reached the maximum usage."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not (coupon.active < timezone.now() < coupon.expire):
        return Response(
            {"response": "This coupon is not active."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not (coupon.min_price <= order.subtotal() <= coupon.max_price):
        return Response(
            {"response": "Your order's total price is not suitable for this coupon."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.coupon = coupon
    order.coupon_used = True

    coupon.used_times += 1
    coupon.save()

    order.save()
    return Response(
        {
            "response": f"Coupon with {coupon.discount_percentage} discount % applied successfully!"
        },
        status=status.HTTP_200_OK,
    )

def clean_expired_reserves(user):
    expiration_time = timezone.now() - timedelta(minutes=10)
    # Get all reserves older than 10 minutes
    expired_reserves = Reserve.objects.filter(user=user, created_at__lt=expiration_time)
    
    for reserve in expired_reserves:
        # Add the quantity back to the product's stock
        product_color = get_object_or_404(ProductColor, product=reserve.product, color=reserve.color)
        product_color.quantity += reserve.quantity
        product_color.save()
    
    # Delete the expired reserves
    expired_reserves.delete()

def make_reserve(request, order_items):
    clean_expired_reserves(request.user)
    with transaction.atomic():
        reserves = []
        product_colors = {} # Cache
        for item in order_items:
            reserves.append(Reserve(
                user=request.user,
                product=item.product,
                color=item.color,
                quantity=item.quantity,
                reserve_id=random.randint(10000, 99999),
            ))
            
            product_color_key = (item.product.id, item.color.id)
            if product_color_key not in product_colors:
                product_color = get_object_or_404(ProductColor, product=item.product,
                            color=item.color)
                product_colors[product_color_key] = product_color
            
            if not product_color.in_stock:
                error_message = f"{item.product.title} is currently unavailable"
               
               
            if product_color.quantity < item.quantity:
                error_message = f"{item.product.title} requested quantity exceeds available stock."

            product_color.quantity -= item.quantity
    
        Reserve.objects.bulk_create(reserves)
        for product_color in product_colors.values():
            product_color.save()


class CheckoutPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, all_orders=None, pk=None):
        clean_expired_reserves(request.user)
        try:
            subtotal = 0
            # First we have reservation
            if bool(all_orders) is True:
                orders = Order.objects.filter(user=request.user, is_paid=False)
                if not orders:
                    return Response(
                        {"response": "You dont have any order yet!"}, status=status.HTTP_400_BAD_REQUEST)
                
                for order in orders:
                    subtotal += order.subtotal()
                    error_message = make_reserve(request, order.order_items.all())
                    if error_message:
                        return Response({"response": error_message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                order = get_object_or_404(Order, id=pk)
                if order.is_paid is False:
                    error_message = make_reserve(request, order.order_items.all())
                    if error_message:
                        return Response({"response": error_message}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(
                        {"response": "This order has already been paid!"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Redirecting to Payment Gateway
            payment_request = payment_gateway(subtotal=subtotal)
            if payment_request is True:
                Reserve.objects.filter(user=request.user).delete()
                return Response({"response": "Your purchase completed successfully!"},
                        status=status.HTTP_200_OK,)
        except IntegrityError:
            return Response({"response": "An error occurred while processing your order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def payment_gateway(subtotal):
    # Simulated payment processing logic
    user_balance = 100000000  # USD
    user_balance - subtotal
    return True
