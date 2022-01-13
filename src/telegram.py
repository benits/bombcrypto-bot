import sys
import yaml
import requests
import telebot

# Load config file.
stream = open("config.yaml", 'r')
configFile = yaml.safe_load(stream)
bot_token = configFile['telegram']['token_api']

bot = telebot.TeleBot(bot_token)
bot_chatID = configFile['telegram']['chat_id']


def telegram_bot_sendtext(bot_message):
    telegram_bot_is_enabled = configFile['telegram']['level'] == 'disable'

    if telegram_bot_is_enabled:
        return

    if bot_token == 'your_bot_token' and bot_chatID == 'yout_chat_id':
        raise ValueError(
            "You must change the 'your_bot_token' and 'yout_chat_id' in the config file")

    if type(bot_message) != str:
        raise ValueError("bot_message Should be a string")

    return bot.send_message(bot_chatID, bot_message, parse_mode="markdown", disable_notification=configFile['telegram']['notification'])


def telegram_bot_sendimage(photo):
    telegram_bot_is_enabled = configFile['telegram']['level'] == 'disable'

    if telegram_bot_is_enabled:
        return

    if bot_token == 'your_bot_token' and bot_chatID == 'yout_chat_id':
        raise ValueError(
            "You must change the 'your_bot_token' and 'yout_chat_id' in the config file")

    return bot.send_photo(bot_chatID, photo, disable_notification=configFile['telegram']['notification'])
