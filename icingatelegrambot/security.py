import json
import logging
import sys

from icingatelegrambot.tool.config import ConfigFile
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext

logger = logging.getLogger(__name__)

class SecurityManager():
    configfile = None  # type: ConfigFile
    allowed_chat_ids = []  # type: []
    commands_only_administrators = None

    MESSAGE_CHAT_NOT_ALLOWED = "Sorry, this chat is not allowed to perform any actions."
    MESSAGE_ONLY_ADMINS = "Sorry, only administrators are allowed to issue commands."

    def __init__(self, configfile):
        self.configfile = configfile
        self.allowed_chat_ids = json.loads(self.configfile.configuration.get("security", "allowed_chat_ids"))
        self.commands_only_administrators = json.loads(self.configfile.configuration.get("security", "commands_only_administrators"))

    def check_chat_id(self, chat_id):
        if (chat_id not in self.allowed_chat_ids):
            logger.warning('Chat ID "%s" is not allowed.', chat_id)
            return False

        return True

    def check_message_is_user_administrator(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        # Always true in private chats
        if context.bot.get_chat(chat_id).type == "private":
            return True

        admins = context.bot.get_chat_administrators(chat_id)

        for admin in admins:
            if admin.user.id == user_id:
                return True
        return True

    @staticmethod
    def check_message_permission(func):
        def check(caller_class, update: Update,context: CallbackContext, *args,**kwargs):
            security_manager = caller_class.security_manager # type: SecurityManager

            if(security_manager is None):
                return False

            if (security_manager.check_chat_id(update.effective_message.chat.id) is False):
                update.message.reply_text(SecurityManager.MESSAGE_CHAT_NOT_ALLOWED)
                return False
            if (security_manager.commands_only_administrators and (security_manager.check_message_is_user_administrator(update,context) is False)):
                update.message.reply_text(SecurityManager.MESSAGE_ONLY_ADMINS)
                return False
            return func(caller_class, update, context, *args, **kwargs)
        return check
