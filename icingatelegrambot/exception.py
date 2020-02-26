class Icinga2TelegramBotException(Exception):
    def __init__(self, error):
        super(Icinga2TelegramBotException, self).__init__(error)
        self.error = error

    def __str__(self):
        return str(self.error)


class Icinga2TelegramBotConfigFileException(Icinga2TelegramBotException):
    def __init__(self, error):
        super(Icinga2TelegramBotConfigFileException, self).__init__(error)
        self.error = error

    def __str__(self):
        return str(self.error)
