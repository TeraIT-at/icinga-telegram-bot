import os
import sys
# pylint: disable=import-error,no-name-in-module
from icingatelegrambot.exception import Icinga2TelegramBotConfigFileException

if sys.version_info >= (3, 0):
    import configparser as configparser
else:
    import ConfigParser as configparser


class ConfigFile(object):
    configuration = None  # type: configparser.ConfigParser

    def __init__(self, file_name):
        '''
        initialization
        '''

        self.file_name = file_name
        self.sections = ['telegram', 'security', 'icinga']
        self.configuration = configparser.ConfigParser()

        if self.file_name:
            self.check_access()

        self.parse()

    def check_access(self):
        '''
        check access to the config file

        :returns: True
        :rtype: bool
        '''

        if not os.path.exists(self.file_name):
            raise Exception(
                'Config file "{0}" doesn\'t exist.'.format(
                    self.file_name
                )
            )

        if not os.access(self.file_name, os.R_OK):
            raise Exception(
                'No read access for config file "{0}".\n'.format(
                    self.file_name
                )
            )

        return True

    def parse(self):
        '''
        parse the config file
        '''

        self.configuration.read(self.file_name)

        for section in self.sections:
            if not self.configuration.has_section(section):
                raise Icinga2TelegramBotConfigFileException(
                    'Config file is missing "{0}" section.'.format(
                        section
                    )
                )
