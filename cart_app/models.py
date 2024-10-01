from django.db import models
from user_auth_app.models import User
from product_app.models import Product, Color
# Create your models here.


class Cart(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, verbose_name="ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.FloatField()

    def __str__(self) -> str:
        return f"{self.product.title} - {self.color.title} - {self.quantity}"

    def subtotal(self):
        return self.price * self.quantity



