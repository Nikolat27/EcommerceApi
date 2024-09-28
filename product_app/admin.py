from django.contrib import admin
from . import models


# Register your models here.


class ProductColorInLine(admin.TabularInline):
    model = models.ProductColor


class ProductSpecificationsInLine(admin.TabularInline):
    model = models.Specification


class ProductImageInLine(admin.TabularInline):
    model = models.ProductImage


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    model = models.Category
    search_fields = ("title",)


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    model = models.Brand
    search_fields = ("title",)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    inlines = [ProductColorInLine, ProductSpecificationsInLine, ProductImageInLine]
    autocomplete_fields = ['category', "brand"]
