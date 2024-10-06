import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Reserve

# Celery worker command: celery -A EcommerceApi worker --loglevel=info --pool=solo
# Celery beat command: celery -A EcommerceApi beat --loglevel=info
logger = logging.getLogger(__name__)

@shared_task
def cleanup_unpaid_reserves():
    expiration_time = timezone.now() - timedelta(minutes=1)
    Reserve.objects.filter(is_paid=False, created_at__lt=expiration_time).delete()
