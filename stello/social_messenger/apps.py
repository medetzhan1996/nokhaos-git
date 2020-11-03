from django.apps import AppConfig


class SocialMessengerConfig(AppConfig):
    name = 'social_messenger'

    def ready(self):
        # import signal handlers
        import social_messenger.signals
