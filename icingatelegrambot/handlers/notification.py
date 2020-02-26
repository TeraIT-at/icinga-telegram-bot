from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from icingatelegrambot.handlers.handler import Icinga2TelegramBotHandler
from icingatelegrambot.security import SecurityManager


class NotificationHandler(Icinga2TelegramBotHandler):
    send_notification_handler = None  # type: CommandHandler

    MESSAGE_USAGE = "Usage: /send_notification <Host|Service>;<Hostname>[;Servicename];Text"
    MESSAGE_UNKNOWN_NOTIFICATION_TYPE = "Unknown Notification type: {notification_type}" \
                                        ""
    def __init__(self, security_manager, api_client, ):
        Icinga2TelegramBotHandler.__init__(self, security_manager, api_client)
        self.send_notification_handler = CommandHandler("send_notification", self.send_notification)

        self.handlers.append(self.send_notification_handler)

    @SecurityManager.check_message_permission
    def send_notification(self, update: Update, context: CallbackContext):
        ''' /send_notification <Host|Service>;<Hostname>;<Servicename>;Text'''
        def reply_usage(update:Update):
            update.message.reply_text(NotificationHandler.MESSAGE_USAGE)

        command = update.message.text.split(" ", 1)

        if(len(command) <= 1):
            reply_usage(update)
            return

        command_parameters = command[1].split(";")

        if(len(command_parameters)<3):
            reply_usage(update)
            return

        notification_type = command_parameters[0]

        if(notification_type != "Host" and notification_type != "Service"):
            update.message.reply_text(self.MESSAGE_UNKNOWN_NOTIFICATION_TYPE.format(notification_type=notification_type))
            reply_usage(update)
            return

        hostname = command_parameters[1]
        result = None

        if notification_type == "Service" and len(command_parameters) == 4:
            servicename = command_parameters[2]
            notification_text = command_parameters[3]
            result = self.api_client.actions.send_custom_notification("Service",
                                                                      'host.name == "' + hostname + '" && service.name == "' + servicename + '"',
                                                                      "Icinga Telegram Bot", notification_text)

        if notification_type == "Host":
            notification_text = command_parameters[2]
            result = self.api_client.actions.send_custom_notification("Host",
                                                                      'host.name == "' + hostname + '"',
                                                                      "Icinga Telegram Bot", notification_text)
