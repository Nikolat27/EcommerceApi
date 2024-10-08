from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from user_auth_app.models import User


# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=50)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="sub", null=True, blank=True)

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
    slug = models.SlugField(max_length=100, allow_unicode=True, unique=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Title: {self.title} - Price: {self.price}"

    def save(self):
        if self.title:
            self.slug = slugify(self.title, allow_unicode=True)
        super(Product, self).save()

    def discounted_price(self):
        if self.enable_discount and self.discount_percentage >= 0:
            return self.price - (self.price / 100 * self.discount_percentage)
        return self.price

    def total_likes(self):
        return self.product_likes.count()


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


def time_difference(created_at):
    current_time = timezone.now()
    time_difference = current_time - created_at
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days >= 365:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif days >= 30:
        month = days // 30
        return f"{month} month{'s' if month > 1 else ''} ago"
    elif days >= 7:
        week = days // 7
        return f"{week} week{'s' if week > 1 else ''} ago"
    elif days >= 1:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours >= 1:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes >= 1:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{seconds} second{'s' if seconds > 1 else ''} ago"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    choices = [("1", "1/5"), ("2", "2/5"), ("3", "3/5"), ("4", "4/5"), ("5", "5/5")]
    text = models.TextField()
    rating = models.CharField(max_length=10, choices=choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.author.username} - {self.rating}"

    def time_difference(self):
        return time_difference(self.created_at)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.author.username} - {self.text:20}"

    def time_difference(self):
        return time_difference(self.created_at)


class ProductLike(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.user.username}"


ACTION_TYPES = (
    ("like", "Like"),
    ("dislike", "dislike"),
)


class ReviewAction(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="action")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_action")
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_type}"


class CommentAction(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="action")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_action")
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action_type}"
