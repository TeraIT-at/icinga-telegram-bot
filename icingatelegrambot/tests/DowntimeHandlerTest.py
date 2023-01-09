import mock
import pytest
import datetime

import telegram

import icinga2apic.client
import icingatelegrambot.handlers.downtime
from icingatelegrambot.handlers.downtime import DowntimeHandler
from telegram import (Update,Message,Chat,User)

handler = DowntimeHandler(None,None)


@pytest.fixture(scope="function")
def update(command):
    update = Update(
        0,
        Message(
            0,
            datetime.datetime.utcnow(),
            Chat(0, "private"),
            from_user=User(0, "Testuser", False),
            via_bot=User(0, "Testbot", True),
            sender_chat=Chat(0, "Channel"),
            forward_from=User(0, "HAL9000", False),
            forward_from_chat=Chat(0, "Channel"),
            text=command
        ),
    )
    return update

@pytest.fixture(autouse=True)
def disable_api(mocker):
    mocker.patch("icingatelegrambot.handlers.downtime.DowntimeHandler.schedule_downtime", return_value=None)


@pytest.fixture(autouse=True)
def disable_telegram_reply(mocker):
        mocker.patch("telegram.Message.reply_text", return_value=Message)


class TestDowntimeHandler():
    @pytest.mark.parametrize('command', ["/schedule_downtime"])
    def test_usage(self,update):
        result = handler.handle_schedule_downtime(update,None)
        assert result == handler.usage()

    @pytest.mark.parametrize('command', ["/schedule_downtime invalid;testhost;;comment;1671465125;1671465500;;;;;"])
    def test_usage_host_service_invalid(self,update):
        result = handler.handle_schedule_downtime(update,None)
        assert result == handler.usage()

    @pytest.mark.parametrize('command', ["/schedule_downtime Host;testhost;;comment;1671465125;1671465500;;;;;",
                                         "/schedule_downtime Service;testhost;;comment;1671465125;1671465500;;;;;"])
    def test_ok(self, update):
        result = handler.handle_schedule_downtime(update, None)
        assert result == None

    @pytest.mark.parametrize('command', ["/schedule_downtime Host;testhost;;;1671465125;1671465500;;;;;"])
    def test_usage_when_comment_missing(self, update):
        result = handler.handle_schedule_downtime(update, None)
        assert result == handler.usage(handler.MESSAGE_COMMENT_MISSING)

    @pytest.mark.parametrize('command', ["/schedule_downtime Host;testhost;;comment;;1671465500;;;;;",
                                         "/schedule_downtime Service;testhost;;comment;1671465125;;;;;;"])
    def test_time_missing(self, update):
        result = handler.handle_schedule_downtime(update, None)
        assert result in [handler.usage(handler.MESSAGE_START_TIME_MISSING), handler.usage(handler.MESSAGE_END_TIME_MISSING)]

    @pytest.mark.parametrize('command', ["/schedule_downtime Host;testhost;;comment;1671465125;1671465500;False;;;;"])
    def test_fixed_without_duration(self, update):
        result = handler.handle_schedule_downtime(update, None)
        assert result == handler.usage(handler.MESSAGE_DURATION_MANDATORY_FOR_FLEXIBLE)

    @pytest.mark.parametrize('command', ["/schedule_downtime Host;testhost;;comment;1671465125;1671465500;;;;;",
                                         "/schedule_downtime Host;testhost;;comment;In one hour;in two hours;;;;;",
                                         "/schedule_downtime Host;testhost;;comment;Yesterday;Today;;;;;",
                                         "/schedule_downtime Host;testhost;;comment;Heute;Morgen;;;;;"])
    def test_date_conversion(self, update):
        result = handler.handle_schedule_downtime(update, None)
        assert result == None

    @pytest.mark.parametrize('command', ["/schedule_downtime Host;testhost;;comment;1671465500;1671465125;;;;;",
                                         "/schedule_downtime Host;testhost;;comment;Today;Yesterday;;;;;"])
    def test_time_swapped(self, update):
        result = handler.handle_schedule_downtime(update, None)
        assert result == handler.usage(handler.MESSAGE_TIME_SWAPPED)