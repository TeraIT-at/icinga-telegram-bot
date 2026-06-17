import argparse
import logging
import traceback
from pprint import pprint

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from icinga2apic.client import Client as Icinga2ApiClient
from icinga2apic.exceptions import Icinga2ApiRequestException
from icingatelegrambot.handlers.acknowledge import AcknowledgeHandler
from icingatelegrambot.handlers.downtime import DowntimeHandler
from icingatelegrambot.handlers.handler import Icinga2TelegramBotHandler
from icingatelegrambot.handlers.notification import NotificationHandler
from icingatelegrambot.security import SecurityManager
from icingatelegrambot.tool import results
from icingatelegrambot.tool.config import ConfigFile

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Icinga2TelegramBot():
    api_client = None  # type: Icinga2ApiClient
    security_manager = None  # type: SecurityManager
    configfile = None  # type: ConfigFile

    MESSAGE_NOT_SUCCESSFULL = "Your command was NOT sucessfull. Maybe the host or service does not exist."
    MESSAGE_ERROR = "The bot encountered an error. Please inform the administrator to check."

    def __init__(self, args: argparse.Namespace):
        self.configfile = ConfigFile(args.config_file.name)
        self.security_manager = SecurityManager(self.configfile)

        self.api_client = Icinga2ApiClient(self.configfile.configuration.get("icinga", "api_url"),
                                           self.configfile.configuration.get("icinga", "api_user"),
                                           self.configfile.configuration.get("icinga", "api_pass"),
                                           ca_certificate=self.configfile.configuration.get("icinga", "api_ca"))

        application = Application.builder().token(
            self.configfile.configuration.get("telegram", "token")).build()

        # Add single Command handlers
        application.add_handler(CommandHandler("help", self.help))

        # Add external handlers
        Icinga2TelegramBotHandler.registerHandlerAtApplication(
            AcknowledgeHandler(self.security_manager, self.api_client), application)
        Icinga2TelegramBotHandler.registerHandlerAtApplication(
            NotificationHandler(self.security_manager, self.api_client), application)
        Icinga2TelegramBotHandler.registerHandlerAtApplication(
            DowntimeHandler(self.security_manager, self.api_client), application)

        application.add_error_handler(self.error)

        application.run_polling()

    async def help(self, update: Update, context: CallbackContext):
        """Send a message when the command /help is issued."""
        await update.message.reply_text('Help!')

    async def error(self, update: Update, context: CallbackContext):
        if type(context.error) is Icinga2ApiRequestException:
            response = results.ResultPrinter.printResultsFromResponse(context.error.response)
            if(response == ""):
                response = self.MESSAGE_NOT_SUCCESSFULL
            if (isinstance(update, Update) and update.message):
                await update.message.reply_text(response)
            if (isinstance(update, Update) and update.callback_query):
                await context.bot.answer_callback_query(update.callback_query.id, response)

            logger.warning('Update "%s" \ncaused error \n"%s"', update, context.error)
            logger.debug(traceback.print_tb(context.error.__traceback__))
            return
        else:
            response = self.MESSAGE_ERROR
            if (isinstance(update, Update) and update.message):
                await update.message.reply_text(response)

            if (isinstance(update, Update) and update.callback_query):
                await context.bot.answer_callback_query(update.callback_query.id, response)

            if (update and context.error):
                logger.warning('Update "%s" \ncaused error \n"%s"', update, context.error)
                logger.debug(traceback.print_tb(context.error.__traceback__))
