from rest_framework import serializers
from . import models


class CartSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = models.Cart
        fields = "__all__"

    def get_user(self, obj):
        return obj.user.username

    def get_cart_items(self, obj):
        return CartItemSerializer(instance=obj.cart_items.all(), many=True).data


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = models.CartItem
        fields = "__all__"

    def get_product(self, obj):
        return obj.product.title

    def get_product_slug(self, obj):
        return obj.product.slug

    def get_color(self, obj):
        return obj.color.title


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = models.Order
        fields = "__all__"

    def get_order_items(self, obj):
        return OrderItemSerializer(instance=obj.order_items.all(), many=True).data

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderItem
        fields = "__all__"

    def get_product(self, obj):
        return obj.product.title

    def get_product_slug(self, obj):
        return obj.product.slug

    def get_color(self, obj):
        return obj.color.title

    def get_final_price(self, obj):
        return obj.final_price
