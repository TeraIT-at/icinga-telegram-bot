import argparse
import logging

from icingatelegrambot.bot import Icinga2TelegramBot

self_description = """This is an Icinga2 Telegram bot.

It can be used to interact with Icinga2 from your Telegram client. It uses the
Icinga2 API.
"""

__version__ = "0.1.0"
__version_date__ = "2020-02-26"
__author__ = "Christian Jonak-Möchel <christian@jonak.org>"
__description__ = "Icinga2 Telegram Bot"
__license__ = "Apache"
__url__ = "https://github.com/joni1993/icinga-telegram-bot"


def main(args):
    bot = Icinga2TelegramBot(args)


if __name__ == '__main__':
    description = "%s\nVersion: %s (%s)" % (self_description, __version__, __version_date__)

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config_file", type=argparse.FileType("r"), default="icinga-telegram-bot.config", help="""points to the config file to read config data from
                        which is not installed under the default path
                        './icinga-telegram-bot.config'")""")
    parser.add_argument(
            "--log-level",default=logging.INFO,type=lambda x: getattr(logging, x),help="Configure the logging level.")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    main(args)
