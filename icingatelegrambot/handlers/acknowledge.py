from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler
from icingatelegrambot.handlers.acknowledgeconversation import AcknowledgeConversationHandler
from icingatelegrambot.handlers.handler import Icinga2TelegramBotHandler
from icingatelegrambot.security import SecurityManager
from icingatelegrambot.tool.notification import NotificationParser
from icingatelegrambot.tool.results import ResultPrinter


class AcknowledgeHandler(Icinga2TelegramBotHandler):
    acknowledge_host_quick_handler = None  # type: CallbackQueryHandler
    acknowledge_host_remove_handler = None  # type: CallbackQueryHandler
    acknowledge_service_quick_handler = None  # type: CallbackQueryHandler
    acknowledge_service_remove_handler = None  # type: CallbackQueryHandler
    acknowledge_conversation_handler = None  # type: ConversationHandler

    MESSAGE_NO_HOSTNAME_FOUND = "Sorry, i couldn\'t find a hostname from your message."
    MESSAGE_NO_SERVICENAME_FOUND = "Sorry, i couldn\'t find a servicename from the message."

    def __init__(self, security_manager, api_client, ):
        Icinga2TelegramBotHandler.__init__(self, security_manager, api_client)

        self.acknowledge_host_quick_handler = CallbackQueryHandler(self.acknowledge_host_quick,
                                                                   pattern="^ack_host_quick$")
        self.acknowledge_host_remove_handler = CallbackQueryHandler(self.remove_host_acknowledge,
                                                                    pattern="^ack_host_remove$")
        self.acknowledge_service_quick_handler = CallbackQueryHandler(self.acknowledge_service_quick,
                                                                      pattern="^ack_service_quick$")
        self.acknowledge_service_remove_handler = CallbackQueryHandler(self.remove_service_acknowledge,
                                                                       pattern="^ack_service_remove$")

        self.acknowledge_conversation_handler = AcknowledgeConversationHandler(self.security_manager, self.api_client)

        self.handlers.append(self.acknowledge_host_quick_handler)
        self.handlers.append(self.acknowledge_host_remove_handler)
        self.handlers.append(self.acknowledge_service_quick_handler)
        self.handlers.append(self.acknowledge_service_remove_handler)
        self.handlers.append(self.acknowledge_conversation_handler)

    ''' 
    Host specific function
    '''
    @SecurityManager.check_message_permission
    def acknowledge_host_quick(self, update: Update, context: CallbackContext):
        ''' Handles the callback query for the quick acknowledge button sent from Icinga'''

        hostname = NotificationParser.findHostnameFromNotification(update.callback_query.message.text)

        if (hostname is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return


        author = update.effective_user.name if update.effective_user else "Unknown User"

        api_result = self.api_client.actions.acknowledge_problem("Host", 'host.name == "' + hostname + '"',
                                                                 author + " via Icinga Telegram Bot",
                                                                 "Quick Acknowledge", notify=True)

        context.bot.answer_callback_query(update.callback_query.id)
        update.callback_query.message.reply_text(ResultPrinter.printResultsFromResponse(api_result))

    @SecurityManager.check_message_permission
    def remove_host_acknowledge(self, update: Update, context: CallbackContext):
        ''' Handles the callback query for the remove acknowledge button sent from Icinga'''

        hostname = NotificationParser.findHostnameFromNotification(update.callback_query.message.text)

        if (hostname is None):
            return

        api_result = self.api_client.actions.remove_acknowledgement("Host", 'host.name == "' + hostname + '"')

        context.bot.answer_callback_query(update.callback_query.id)
        update.callback_query.message.reply_text(ResultPrinter.printResultsFromResponse(api_result))

    '''
    Service specific functions
    '''

    @SecurityManager.check_message_permission
    def acknowledge_service_quick(self, update: Update, context: CallbackContext):
        hostname, servicename = NotificationParser.findHostnameAndServicenameFromNotification(
            update.callback_query.message.text)

        if (servicename is None):
            context.bot.answer_callback_query(update.callback_query.id)
            update.callback_query.message.reply_text(self.MESSAGE_NO_SERVICENAME_FOUND)
            return

        if (hostname is None):
            context.bot.answer_callback_query(update.callback_query.id)
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return

        author = update.effective_user.name if update.effective_user else "Unknown User"

        api_result = self.api_client.actions.acknowledge_problem("Service",
                                                                 'host.name == "' + hostname + '" && service.name == "' + servicename + '"',
                                                                 author + " via Icinga Telegram Bot",
                                                                 "Quick Acknowledge", notify=True)

        context.bot.answer_callback_query(update.callback_query.id)
        update.callback_query.message.reply_text(ResultPrinter.printResultsFromResponse(api_result))

    @SecurityManager.check_message_permission
    def remove_service_acknowledge(self, update: Update, context: CallbackContext):
        hostname, servicename = NotificationParser.findHostnameAndServicenameFromNotification(
            update.callback_query.message.text)

        if (servicename is None):
            context.bot.answer_callback_query(update.callback_query.id)
            update.callback_query.message.reply_text(self.MESSAGE_NO_SERVICENAME_FOUND)
            return

        if (hostname is None):
            context.bot.answer_callback_query(update.callback_query.id)
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return

        api_result = self.api_client.actions.remove_acknowledgement("Service",
                                                                    'host.name == "' + hostname + '" && service.name == "' + servicename + '"')

        context.bot.answer_callback_query(update.callback_query.id)
        update.callback_query.message.reply_text(ResultPrinter.printResultsFromResponse(api_result))

