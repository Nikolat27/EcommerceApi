import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Reserve

# Celery worker command: celery -A EcommerceApi worker --loglevel=info --pool=solo
# Celery beat command: celery -A EcommerceApi beat --loglevel=info
logger = logging.getLogger(__name__)

@shared_task
<<<<<<< HEAD
def cleanup_unpaid_reserves(request):
    # expiration_time = timezone.now() - timedelta(minutes=1)
    # cache_key = f'user_reserves_{request.user.id}'
    # reserves_cache = redis_client.get(cache_key)

    # # Process cache and delete expired reserves
    # for reserve in reserves_cache:
    #     # Add the quantity back to the product's stock
    #     product_color_key = f'product_color_{reserve.product.id}_{reserve.color.id}'
    #     product_color = redis_client.get(product_color_key)

    #     if not product_color:
    #         product_color = get_object_or_404(ProductColor, product=reserve.product, color=reserve.color)
    #         redis_client.set(product_color_key, product_color, timeout=300)

    #     product_color.quantity += reserve.quantity
    #     product_color.save()

    # reserves_cache.delete()
    # redis_client.delete(cache_key)
    
    expiration_time = timezone.now() - timedelta(minutes=10)
    # Get all reserves older than 10 minutes
    expired_reserves = Reserve.objects.filter(created_at__lt=expiration_time, is_paid=False)
    
    for reserve in expired_reserves:
        # Add the quantity back to the product's stock
        product_color = get_object_or_404(ProductColor, product=reserve.product, color=reserve.color)
        product_color.quantity += reserve.quantity
        product_color.save()
    
    # Delete the expired reserves
    expired_reserves.delete()
=======
def cleanup_unpaid_reserves():
    expiration_time = timezone.now() - timedelta(minutes=1)
    Reserve.objects.filter(is_paid=False, created_at__lt=expiration_time).delete()
>>>>>>> parent of 77f2c05 (I added caching with redis for making reserves)
