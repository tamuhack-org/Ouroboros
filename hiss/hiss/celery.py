from __future__ import absolute_import, unicode_literals
import os
import ssl
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hiss.settings.dev')

app = Celery('hiss',
            broker_use_ssl={
                'ssl_cert_reqs': ssl.CERT_NONE,
            },
            redis_backend_use_ssl = {
                'ssl_cert_reqs': ssl.CERT_NONE,
            }
        )

# Using a string here so the worker doesn't have to serialize the object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery configuration for Redis as the broker and result backend
app.conf.broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')  
app.conf.result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0') 
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
