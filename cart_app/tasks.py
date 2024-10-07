import logging
from django.shortcuts import get_object_or_404
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Reserve
from product_app.models import ProductColor

# Celery worker command: celery -A EcommerceApi worker --loglevel=info --pool=solo
# Celery beat command: celery -A EcommerceApi beat --loglevel=info
logger = logging.getLogger(__name__)

@shared_task
def cleanup_unpaid_reserves():
    expiration_time = timezone.now() - timedelta(minutes=1)
    expired_reserves = Reserve.objects.filter(is_paid=False, created_at__lt=expiration_time).delete()

    for reserve in expired_reserves:
        product = get_object_or_404(ProductColor, product=reserve.product, color=reserve.color)
        product.quantity += reserve.quantity
        product.quantity.save()
