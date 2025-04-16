from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from .db_keepalive import keep_postgres_alive
        keep_postgres_alive(daily=True, run_now=False)

