import os
from celery import Celery
from django.utils.timezone import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcommerceApi.settings')

app = Celery('EcommerceApi')
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cleanup-unpaid-reserves-task': {
        'task': 'cart_app.tasks.cleanup_unpaid_reserves',
        'schedule': timedelta(minutes=1),  # Every 1 minute
    },
}
app.conf.result_expires = 60 # It deletes the tasks result which are stored in redis cache