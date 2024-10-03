from django.contrib import admin
from . import models

# Register your models here.


class CartItemTabularInLine(admin.TabularInline):
    model = models.CartItem


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    model = models.Cart
    inlines = [CartItemTabularInLine]

class OrderItemTabularInLine(admin.TabularInline):
    model = models.OrderItem

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    model = models.Order
    inlines = [OrderItemTabularInLine]

admin.site.register(models.Coupon)
