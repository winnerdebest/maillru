from django.core.management.base import BaseCommand
from django.db import connection
from datetime import datetime

class Command(BaseCommand):
    help = 'Ping PostgreSQL to keep it alive.'

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
            self.stdout.write(self.style.SUCCESS(f"[{datetime.now()}] DB keep-alive pinged successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[{datetime.now()}] DB ping failed: {e}"))
