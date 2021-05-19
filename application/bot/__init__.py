from flask import Blueprint, request, abort
from application import telegram_bot as bot, logger
from config import Config
from telebot.types import Update
import os
import logging

bp = Blueprint('bot', __name__)

# Load bot's behaviors
from application.bot import core

if 'PRODUCTION' in os.environ:
    # When app started in production, configure Telegram webhook to receive updates
    @bp.route(Config.WEBHOOK_URL_PATH, methods=['POST'])
    def receive_message():
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            abort(400)

    bot.remove_webhook()
    bot.set_webhook(Config.WEBHOOK_URL_BASE + '/bot' + Config.WEBHOOK_URL_PATH, certificate=open(Config.WEBHOOK_SSL_CERT, 'r'))
