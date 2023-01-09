import logging

import dateparser as dateparser
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from icingatelegrambot.handlers.handler import Icinga2TelegramBotHandler
from icingatelegrambot.security import SecurityManager
from icingatelegrambot.tool.results import ResultPrinter
from icingatelegrambot.tool.util import Util

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class DowntimeHandler(Icinga2TelegramBotHandler):
    schedule_downtime_handler = None  # type: CommandHandler

    MESSAGE_USAGE = "Usage: /schedule_downtime (Host|Service);(Hostname);(Servicename);(Comment);(Start time);(End time);(Fixed);(Duration);(All services);(Trigger name);(Child options)"
    MESSAGE_COMMENT_MISSING = "You need to specify a comment."
    MESSAGE_START_TIME_MISSING = "Your start time is missing."
    MESSAGE_END_TIME_MISSING = "Your end time is missing."
    MESSAGE_START_TIME_INVALID = "Your start time could not be parsed"
    MESSAGE_END_TIME_INVALID = "Your end time could not be parsed"
    MESSAGE_TIME_SWAPPED = "Your start time is after your end time."
    MESSAGE_DURATION_MANDATORY_FOR_FLEXIBLE = "You need to specifiy a duration for flexible downtimes."
    #MESSAGE_UNKNOWN_NOTIFICATION_TYPE = "Unknown Notification type: {notification_type}" \
    #                                    ""
    def __init__(self, security_manager, api_client, ):
        Icinga2TelegramBotHandler.__init__(self, security_manager, api_client)

        self.schedule_downtime_handler = CommandHandler("schedule_downtime", self.handle_schedule_downtime_command)

        self.handlers.append(self.schedule_downtime_handler)

    def usage(self,additional="",update: Update=None):
        text = additional+"\n"+DowntimeHandler.MESSAGE_USAGE if additional else DowntimeHandler.MESSAGE_USAGE
        if(update):
            update.message.reply_text(text)
        return text

    @SecurityManager.check_message_permission
    def handle_schedule_downtime_command(self, update: Update, context: CallbackContext):
        self.handle_schedule_downtime(update,context)

    def handle_schedule_downtime(self, update: Update, context: CallbackContext):
        ''' /schedule_downtime (Host|Service);(Hostname);(Servicename);(Comment);(Start time);(End time);(Fixed);
                        (Duration);(All services);(Trigger name);(Child options)'''

        command = update.message.text.split(" ", 1)

        if (len(command) <= 1):
            return self.usage(update=update)

        command_parameters = command[1].split(";")
        host_service = Util.safe_list_access(command_parameters, 0)
        hostname = Util.safe_list_access(command_parameters, 1)
        servicename = Util.safe_list_access(command_parameters, 2)
        comment = Util.safe_list_access(command_parameters, 3)
        start_time = Util.safe_list_access(command_parameters, 4)
        end_time = Util.safe_list_access(command_parameters, 5)
        fixed = Util.safe_list_access(command_parameters, 6)
        duration = Util.safe_list_access(command_parameters, 7)
        all_services = Util.safe_list_access(command_parameters, 8)
        trigger_name = Util.safe_list_access(command_parameters, 9)
        child_options = Util.safe_list_access(command_parameters, 10)

        if host_service is None or host_service not in ["Host","Service"]:
            return self.usage(update=update)

        if comment is None or comment == "":
            return self.usage(DowntimeHandler.MESSAGE_COMMENT_MISSING,update=update)

        if start_time is None or start_time == "":
            return self.usage(DowntimeHandler.MESSAGE_START_TIME_MISSING,update=update)

        if end_time is None or end_time == "":
            return self.usage(DowntimeHandler.MESSAGE_END_TIME_MISSING,update=update)

        start_time = dateparser.parse(start_time)
        end_time = dateparser.parse(end_time)

        if start_time is None:
            return self.usage(DowntimeHandler.MESSAGE_START_TIME_INVALID,update=update)

        if end_time is None:
            return self.usage(DowntimeHandler.MESSAGE_END_TIME_INVALID,update=update)

        if fixed is None or fixed == "":
            fixed = True
        else:
            fixed = False

        if (duration is None or duration == "") and fixed == False:
            return self.usage(DowntimeHandler.MESSAGE_DURATION_MANDATORY_FOR_FLEXIBLE,update=update)

        if start_time > end_time:
            return self.usage(DowntimeHandler.MESSAGE_TIME_SWAPPED,update=update)

        self.schedule_downtime(update,host_service,hostname,servicename,comment,int(start_time.timestamp()),int(end_time.timestamp()),duration,fixed,all_services,trigger_name,child_options)

    def schedule_downtime(self, update, host_service,hostname,servicename,comment,start_time,end_time,duration,fixed,all_services,trigger_name,child_options):
        result = ""

        if host_service == "Service":
            result = self.api_client.actions.schedule_downtime(host_service,
                                                      'host.name == "' + hostname + '" && service.name == "' + servicename + '"',
                                                      "Icinga Telegram Bot",comment,start_time,end_time,duration,None,fixed,all_services,trigger_name,child_options)

        if host_service == "Host":
            result = self.api_client.actions.schedule_downtime(host_service,
                                                               'host.name == "' + hostname + '"',
                                                               "Icinga Telegram Bot", comment, start_time, end_time,
                                                               duration, None, fixed, all_services, trigger_name,
                                                               child_options)

        update.message.reply_text(ResultPrinter.printResultsFromResponse(result))