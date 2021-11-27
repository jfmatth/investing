from django.apps import AppConfig
from django.dispatch import Signal

# from loader.signals import receiverLoadSymbols


class LoaderConfig(AppConfig):
    name = 'loader'

    def ready(self) -> None:
        print("app ready")
        import loader.signals
        print("signal connected")

        return super().ready()
