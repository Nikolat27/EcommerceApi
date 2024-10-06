import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Reserve, ProductColor
from django.shortcuts import get_object_or_404
import redis

redis_client = redis.Redis(host="127.0.0.1", db=0)

# Celery worker command: celery -A EcommerceApi worker --loglevel=info --pool=solo
# Celery beat command: celery -A EcommerceApi beat --loglevel=info

logger = logging.getLogger(__name__)

@shared_task
def cleanup_unpaid_reserves(request):
    expiration_time = timezone.now() - timedelta(minutes=1)
    cache_key = f'user_reserves_{request.user.id}'
    reserves_cache = redis_client.get(cache_key)

    # Process cache and delete expired reserves
    for reserve in reserves_cache:
        # Add the quantity back to the product's stock
        product_color_key = f'product_color_{reserve.product.id}_{reserve.color.id}'
        product_color = redis_client.get(product_color_key)

        if not product_color:
            product_color = get_object_or_404(ProductColor, product=reserve.product, color=reserve.color)
            redis_client.set(product_color_key, product_color, timeout=300)

        product_color.quantity += reserve.quantity
        product_color.save()

    reserves_cache.delete()
    redis_client.delete(cache_key)
