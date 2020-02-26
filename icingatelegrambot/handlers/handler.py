import telegram
from telegram.ext import CallbackContext

class Icinga2TelegramBotHandler(object):
    api_client = None  # type: Icinga2ApiClient
    security_manager = None  # type: SecurityManager

    handlers = []

    def __init__(self, security_manager, api_client):
        self.security_manager = security_manager
        self.api_client = api_client

    @staticmethod
    def registerHandlerAtDispatcher(icinga2telegrambothandler, dispatcher: telegram.ext.Dispatcher):
        """

        :type icinga2telegrambothandler: Icinga2TelegramBotHandler
        """
        for handler in icinga2telegrambothandler.handlers:
            dispatcher.add_handler(handler)
