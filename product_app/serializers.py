from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = "__all__"


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    price_changes = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = "__all__"

    def get_discounted_price(self, obj):
        return obj.discounted_price()

    def get_categories(self, obj):
        return [category.title for category in obj.category.all()]

    def get_brand(self, obj):
        return obj.brand.title

    def get_specifications(self, obj):
        return {spec.spec1: spec.spec2 for spec in obj.specifications.all()}

    def get_images(self, obj):
        return [image.image.path for image in obj.images.all()]

    def get_colors(self, obj):
        return {x.color.title: x.quantity for x in obj.product_color.all() if x.in_stock is True}

    def get_price_changes(self, obj):
        return {change.price: change.created_at.date for change in obj.price_changes.all()}


class ProductPriceChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductPriceChange
        fields = "__all__"


class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductColor
        fields = "__all__"
