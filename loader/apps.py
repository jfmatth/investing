from django.apps import AppConfig
from django.dispatch import Signal


class LoaderConfig(AppConfig):
    name = 'loader'

    def ready(self) -> None:
        print("Loader app ready")
        
        import loader.signals
        print("Loader signals connected")

        return super().ready()
