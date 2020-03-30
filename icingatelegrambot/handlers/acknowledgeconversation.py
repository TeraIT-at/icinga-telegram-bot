import logging
from enum import Enum

from icinga2apic.exceptions import Icinga2ApiRequestException
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, CallbackQueryHandler, \
    Filters

from icingatelegrambot.handlers.handler import Icinga2TelegramBotHandler
from icingatelegrambot.security import SecurityManager
from icingatelegrambot.tool import results
from icingatelegrambot.tool.notification import NotificationParser
from icingatelegrambot.tool.results import ResultPrinter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class AcknowledgeConversationHandler(Icinga2TelegramBotHandler, ConversationHandler):
    class Stages(Enum):
        HOST_INPUT_COMMENT = 10
        SERVICE_INPUT_COMMENT = 20

    MESSAGE_NO_HOSTNAME_FOUND = "Sorry, i couldn\'t find a hostname from your message."
    MESSAGE_NO_SERVICENAME_FOUND = "Sorry, i couldn\'t find a servicename from the message."
    MESSAGE_ACKNOWLEDGE_HOST_RESPONSE = 'You are about to acknowledge the host problem on \nHost: {hostname} \nPlease reply with your comment:\n'
    MESSAGE_ACKNOWLEDGE_HOST_SERVICE_RESPONSE = 'You are about to acknowledge the service problem of\nService: {servicename}\non \nHost: {hostname}\nPlease reply with your comment:\n'
    MESSAGE_ALREADY_FINISHED = "This was already acknowledged!"
    MESSAGE_FALLBACK = "Sorry, this acknowledgement is no longer valid or already finished."

    def __init__(self, security_manager, api_client):
        Icinga2TelegramBotHandler.__init__(self, security_manager, api_client)
        ConversationHandler.__init__(self,
            entry_points=[CallbackQueryHandler(self.acknowledge_host_start, pattern="^ack_host$"),
                          CallbackQueryHandler(self.acknowledge_service_start, pattern="^ack_service$")],

            states={
                self.Stages.HOST_INPUT_COMMENT: [MessageHandler(Filters.text, self.acknowledge_host_finish)
                                                 ],
                self.Stages.SERVICE_INPUT_COMMENT: [MessageHandler(Filters.text, self.acknowledge_service_finish)
                                                    ],
            },

            fallbacks=[MessageHandler(Filters.text, self.fallback)]
        )

    @SecurityManager.check_message_permission
    def acknowledge_host_start(self, update: Update, context: CallbackContext):
        hostname = NotificationParser.findHostnameFromNotification(update.callback_query.message.text)

        if (hostname is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return

        context.bot.answer_callback_query(update.callback_query.id)
        update.callback_query.message.reply_text(self.MESSAGE_ACKNOWLEDGE_HOST_RESPONSE.format(hostname=hostname))
        context.user_data["ackknowledge_hostname"] = hostname

        return self.Stages.HOST_INPUT_COMMENT

    @SecurityManager.check_message_permission
    def acknowledge_host_finish(self, update: Update, context: CallbackContext):
        if update.message.reply_to_message is not None:
            hostname = NotificationParser.findHostnameFromNotification(update.message.reply_to_message.text)
        else:
            hostname = context.user_data["ackknowledge_hostname"]

        if (hostname is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return

        api_result = self.api_client.actions.acknowledge_problem("Host", 'host.name == "' + hostname + '"',
                                                                 "Icinga Telegram Bot",
                                                                 update.message.text, notify=True)

        update.message.reply_text(ResultPrinter.printResultsFromResponse(api_result))
        context.user_data["ackknowledge_hostname"] = None
        context.user_data["ackknowledge_servicename"] = None
        return ConversationHandler.END

    @SecurityManager.check_message_permission
    def acknowledge_service_start(self, update: Update, context: CallbackContext):
        hostname, servicename = NotificationParser.findHostnameAndServicenameFromNotification(
            update.callback_query.message.text)

        if (servicename is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_SERVICENAME_FOUND)
            return

        if (hostname is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return

        context.bot.answer_callback_query(update.callback_query.id)
        update.callback_query.message.reply_text(self.MESSAGE_ACKNOWLEDGE_HOST_SERVICE_RESPONSE.format(hostname=hostname,servicename=servicename))
        context.user_data["ackknowledge_in_progress"] = True
        context.user_data["ackknowledge_hostname"] = hostname
        context.user_data["ackknowledge_servicename"] = servicename

        return self.Stages.SERVICE_INPUT_COMMENT

    @SecurityManager.check_message_permission
    def acknowledge_service_finish(self, update: Update, context: CallbackContext):
        if update.message.reply_to_message is not None:
            hostname, servicename = NotificationParser.findHostnameAndServicenameFromNotification(
                update.message.reply_to_message.text)
        else:
            hostname = context.user_data["ackknowledge_hostname"]
            servicename = context.user_data["ackknowledge_servicename"]

        if (servicename is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_SERVICENAME_FOUND)
            return

        if (hostname is None):
            update.callback_query.message.reply_text(self.MESSAGE_NO_HOSTNAME_FOUND)
            return

        api_result = self.api_client.actions.acknowledge_problem("Service",
                                                                 'host.name == "' + hostname + '" && service.name == "' + servicename + '"',
                                                                 "Icinga Telegram Bot",
                                                                 update.message.text, notify=True)

        update.message.reply_text(ResultPrinter.printResultsFromResponse(api_result))
        context.user_data["ackknowledge_hostname"] = None
        context.user_data["ackknowledge_servicename"] = None
        return ConversationHandler.END

    def fallback(self, update: Update, context: CallbackContext):
        if(update.message.reply_to_message is None):
            context.bot.send_message(update.effective_chat.id,self.MESSAGE_FALLBACK)
        else:
            update.message.reply_text(self.MESSAGE_FALLBACK)
