from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dramaclick.settings')

app = Celery('dramaclick')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

app.conf.beat_schedule = {

    'Get-All-Genres-Daily': {
        'task': 'get_all_genres_everyday',
        'schedule': crontab(hour=22, minute=30),
        'args': ()
    },
    'Get-All-Companies-Daily': {
        'task': 'get_all_company_everyday',
        'schedule': crontab(hour=23, minute=30),
        'args': ()
    },
    'Get-All-Person-Daily': {
        'task': 'get_new_person_everyday',
        'schedule':crontab(hour=23, minute=30),
        'args': ()
    },
    'Get-All-Kdrama-Daily': {
        'task': 'get_new_kdrama_everyday',
        'schedule': crontab(hour=1, minute=00),
        'args': ()
    },
    'Get-All-Movie-Daily': {
        'task': 'get_new_movie_everyday',
        'schedule': crontab(hour=2, minute=30),
        'args': ()
    },
    
        'Update-All-Drama-Daily': {
        'task': 'update_kdrama',
        'schedule': crontab(hour=4, minute=00),
        'args': () 
    },
        'Update-All-Movie-Daily': {
        'task': 'update_movie',
        'schedule': crontab(hour=6, minute=00),
        'args': () 
    },
    
}