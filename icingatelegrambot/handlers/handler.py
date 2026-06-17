from telegram.ext import Application, CallbackContext

class Icinga2TelegramBotHandler(object):
    api_client = None  # type: Icinga2ApiClient
    security_manager = None  # type: SecurityManager

    def __init__(self, security_manager, api_client):
        self.security_manager = security_manager
        self.api_client = api_client
        # Per-instance list -- a shared class-level list would otherwise
        # accumulate across handlers and register them multiple times.
        self.handlers = []

    @staticmethod
    def registerHandlerAtApplication(icinga2telegrambothandler, application: Application):
        """

        :type icinga2telegrambothandler: Icinga2TelegramBotHandler
        """
        for handler in icinga2telegrambothandler.handlers:
            application.add_handler(handler)
