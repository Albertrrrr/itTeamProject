import os
from celery import Celery

# Setting environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itTeamProject.settings')

# Instantiation, need to change to your own app name
app = Celery('itTeamProject')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
