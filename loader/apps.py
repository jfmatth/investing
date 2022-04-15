from django.apps import AppConfig
from django.dispatch import Signal


class LoaderConfig(AppConfig):
    name = 'loader'

    def ready(self) -> None:
        import loader.signals

        return super().ready()
