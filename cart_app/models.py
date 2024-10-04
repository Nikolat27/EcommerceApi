from django.db import models
from user_auth_app.models import User
from product_app.models import Product, Color
from django.utils import timezone

# Create your models here.


class Cart(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name="ID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True
    )
    session_id = models.CharField(max_length=60, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username if self.user else self.session_id

    def subtotal(self):
        total = 0
        for item in self.cart_items.all():
            total += item.subtotal()
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.FloatField()

    def __str__(self) -> str:
        return f"{self.product.title} - {self.color.title} - {self.quantity}"

    def subtotal(self):
        return self.price * self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=16, unique=True)
    min_price = models.FloatField()
    max_price = models.FloatField()
    discount_percentage = models.FloatField()
    active = models.DateField()
    expire = models.DateField()
    max_usage = models.PositiveSmallIntegerField(default=1)
    used_by = models.ManyToManyField(User, related_name="coupon_used")
    is_enable = models.FloatField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.code} - Enable: {self.is_enable} - Discount %: {self.discount_percentage}"

    def used_times(self):
        return self.used_by.count()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    coupon_used = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="coupon", null=True, blank=True)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=11)
    email = models.EmailField()
    postal_code = models.CharField(max_length=12)
    address = models.TextField()
    cart_number = models.CharField(max_length=16)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.country}"

    def subtotal(self):
        total = sum(item.final_price() for item in self.order_items.all())

        # Coupon validation
        if self.coupon_used is False:
            return total

        if not (self.coupon.is_enable and self.coupon.max_usage <= self.coupon.used_by):
            return total

        if not (self.coupon.active < timezone.now() < self.coupon.expire):
            return total

        if not (self.coupon.min_price <= total <= self.coupon.max_price):
            return total

        discount_amount = (total / 100) * self.coupon.discount_percentage
        return total - discount_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.FloatField()

    def final_price(self):
        return self.quantity * self.price


