from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify


# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=50)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="sub")

    def __str__(self):
        return self.title


class Brand(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Color(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100, unique=True)
    category = models.ManyToManyField(Category, related_name="categories")
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="media/products/thumbnails")
    brand = models.ForeignKey(Brand, related_name="brand", on_delete=models.CASCADE)
    price = models.FloatField()
    discount_percentage = models.FloatField()
    enable_discount = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, allow_unicode=True, unique=True)
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Title: {self.title} - Caption: {self.description:50} - Price: {self.price}"

    def discounted_price(self):
        if self.enable_discount and self.discount_percentage >= 0:
            return self.price - (self.price / 100 * self.discount_percentage)
        return self.price


@receiver(post_save, sender=Product)
def save_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.title)
    instance.save()


class ProductPriceChange(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_changes")
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.price}"


# Signal to track price changes
@receiver(pre_save, sender=Product)
def save_price_change(sender, instance, **kwargs):
    pk = instance.pk
    if pk:
        current_product = Product.objects.get(pk=pk)
        if current_product.price != instance.price:
            ProductPriceChange.objects.create(product_id=pk, price=current_product.price)


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_color")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="color")
    quantity = models.PositiveSmallIntegerField(default=1)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.title} - {self.color.title} - Available: {self.in_stock}"

    def save(self, *args, **kwargs):
        if not self.color:
            return

        if self.quantity <= 0:
            self.in_stock = False
        elif self.quantity >= 1:
            self.in_stock = True

        super(ProductColor, self).save(*args, **kwargs)


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    spec1 = models.CharField(max_length=20)
    spec2 = models.CharField(max_length=100)

    def __str__(self):
        return self.product.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="media/products/images")

    def __str__(self):
        return self.product.title
