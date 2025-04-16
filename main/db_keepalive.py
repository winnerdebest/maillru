import threading
import time
from django.db import connection
from datetime import datetime, timedelta

def keep_postgres_alive(daily=True, run_now=False):
    def ping():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
            print(f"[{datetime.now()}] DB keep-alive ping sent.")
        except Exception as e:
            print(f"[{datetime.now()}] DB ping failed: {e}")

    def ping_loop():
        if run_now:
            ping()

        while daily:
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            midnight = datetime.combine(tomorrow.date(), datetime.min.time())
            seconds_until_midnight = (midnight - now).total_seconds()

            time.sleep(seconds_until_midnight)
            ping()

    thread = threading.Thread(target=ping_loop, daemon=True)
    thread.start()
