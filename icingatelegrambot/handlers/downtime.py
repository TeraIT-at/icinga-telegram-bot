import logging
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
    MESSAGE_START_TIME_MISSING = "You need to specify a start time."
    MESSAGE_END_TIME_MISSING = "You need to specify a end time."
    MESSAGE_DURATION_MANDATORY_FOR_FLEXIBLE = "You need to specifiy a duration for flexible downtimes."
    #MESSAGE_UNKNOWN_NOTIFICATION_TYPE = "Unknown Notification type: {notification_type}" \
    #                                    ""
    def __init__(self, security_manager, api_client, ):
        Icinga2TelegramBotHandler.__init__(self, security_manager, api_client)

        self.schedule_downtime_handler = CommandHandler("schedule_downtime", self.schedule_downtime)

        self.handlers.append(self.schedule_downtime_handler)

    @SecurityManager.check_message_permission
    def schedule_downtime(self, update: Update, context: CallbackContext):
        ''' /schedule_downtime (Host|Service);(Hostname);(Servicename);(Comment);(Start time);(End time);(Fixed);
                (Duration);(All services);(Trigger name);(Child options)'''
        def reply_usage(update:Update, additional=None):
            text = additional+"\n"+DowntimeHandler.MESSAGE_USAGE if additional else DowntimeHandler.MESSAGE_USAGE
            update.message.reply_text(text)

        command = update.message.text.split(" ", 1)

        if(len(command) <= 1):
            reply_usage(update)
            return

        command_parameters = command[1].split(";")
        host_service = Util.safe_list_access(command_parameters,0)
        hostname = Util.safe_list_access(command_parameters,1)
        servicename = Util.safe_list_access(command_parameters,2)
        comment = Util.safe_list_access(command_parameters,3)
        start_time = Util.safe_list_access(command_parameters,4)
        end_time = Util.safe_list_access(command_parameters,5)
        fixed = Util.safe_list_access(command_parameters,6)
        duration = Util.safe_list_access(command_parameters,7)
        all_services = Util.safe_list_access(command_parameters,8)
        trigger_name = Util.safe_list_access(command_parameters,9)
        child_options = Util.safe_list_access(command_parameters,10)

        if host_service is None or host_service not in ["Host","Service"]:
            reply_usage(update)
            return

        if comment is None:
            reply_usage(update,DowntimeHandler.MESSAGE_COMMENT_MISSING)
            return

        if start_time is None:
            reply_usage(update,DowntimeHandler.MESSAGE_START_TIME_MISSING)
            return

        if end_time is None:
            reply_usage(update,DowntimeHandler.MESSAGE_END_TIME_MISSING)
            return

        if fixed is None:
            fixed = True

        if duration is None and fixed is False:
            reply_usage(update,DowntimeHandler.MESSAGE_DURATION_MANDATORY_FOR_FLEXIBLE)
            return

#'''def schedule_downtime(self,
#                          object_type,
#                          filters,
#                          author,
#                          comment,
#                          start_time,
#                          end_time,
#                          duration,
#                          filter_vars=None,
#                          fixed=None,
#                          all_services=None,
#                          trigger_name=None,
#                          child_options=None):'''

        result = ""

        if host_service == "Service":
            result = self.api_client.actions.schedule_downtime(host_service,
                                                      'host.name == "' + hostname + '" && service.name == "' + servicename + '"',
                                                      "Icinga Telegram Bot",comment,start_time,end_time,duration,None,fixed,all_services,trigger_name,child_options);

        if host_service == "Host":
            result = self.api_client.actions.schedule_downtime(host_service,
                                                               'host.name == "' + hostname + '"',
                                                               "Icinga Telegram Bot", comment, start_time, end_time,
                                                               duration, None, fixed, all_services, trigger_name,
                                                               child_options)

        update.message.reply_text(ResultPrinter.printResultsFromResponse(result))