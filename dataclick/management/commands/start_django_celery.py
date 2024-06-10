# start_django_celery.py

from django.core.management.base import BaseCommand
from subprocess import Popen
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Start Django server, Celery worker, and Celery Beat'

    def handle(self, *args, **options):

        # create folder
        directory_name = os.path.join(settings.BASE_DIR,'logs')
        if os.path.isdir(directory_name):
            print("Exists")
        else:
            os.makedirs(directory_name)
            print("Created")

        worker_log_path = settings.CELERY_WORKER_LOG_PATH
        beat_log_path = settings.CELERY_BEAT_LOG_PATH

        # Start Celery worker
        worker_process = Popen(['celery', '-A', 'dramaclick', 'worker', '-l', 'info'],
                               stdout=open(worker_log_path, 'w'), stderr=open(worker_log_path, 'a'))

        # Start Celery Beat
        beat_process = Popen(['celery', '-A', 'dramaclick', 'beat', '-l', 'info'], stdout=open(beat_log_path, 'w'),
                             stderr=open(beat_log_path, 'a'))

        # Start Django server
        django_process = Popen(['python', 'manage.py', 'runserver'])

        # Wait for processes to complete
        worker_process.wait()
        beat_process.wait()
        django_process.wait()
