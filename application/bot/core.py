"""
Main core for inline queries handlers
"""
from application import telegram_bot
from telebot.types import CallbackQuery, User
from telebot.apihelper import ApiException
from application.core.models import Test, Channel, BotUser, Answer
from application.resources import strings
from datetime import datetime
from application.utils import date
import settings


@telegram_bot.callback_query_handler(func=lambda query: True)
def answer_handler(query: CallbackQuery):
    if settings.get_bot_state() != settings.BotStates.WORK:
        return
    data = query.data
    data = data.split('@')
    test_id = data[0]
    option_id = data[1]
    user = query.from_user
    channel_id = query.message.chat.id
    try:
        answers_processor(test_id, option_id, user, channel_id, query)
    except Exception as e:
        telegram_bot.answer_callback_query(query.id, strings.get_string('answer.error'))
        raise e


def answers_processor(test_id, option_id, user: User, channel_chat_id, query: CallbackQuery):
    """
    Processor which process user answers
    :param test_id: The test id which the user given an answer
    :param option_id: The answer id
    :param user: The user
    :param channel_chat_id: Telegram chat id of channel
    :param query: Telegram Callback query
    :return: void
    """
    channel = Channel.get_by_chat_id(channel_chat_id)
    if not channel:
        # if channel is not registered just stop processing
        return
    # if user given answer in first time, add him to channel members
    current_user = BotUser.add_user(user.id, user.first_name, user.last_name, user.username)
    channel.add_member(current_user)
    test = Test.get_by_id(test_id)
    if not test:
        telegram_bot.answer_callback_query(query.id, strings.get_string('answer.test_not_found'))
        return
    # Check if user given an answer for current quiz
    now_utc = datetime.utcnow()
    quiz_date = test.quiz.end_date
    local_date = date.convert_utc_to_asia_tz(now_utc)
    if datetime(local_date.year, local_date.month, local_date.day) > datetime(quiz_date.year, quiz_date.month,
                                                                              quiz_date.day):
        message = strings.get_string('answer.quiz_already_ended')
        telegram_bot.answer_callback_query(query.id, message, show_alert=True)
        return
    if test.user_given_right_answer(user_id=current_user.id):
        # if user already given the right answer send message to him and stop processing
        message = strings.get_string('answer.already_given')
        telegram_bot.answer_callback_query(query.id, message, show_alert=True)
        return
    right_answer = test.get_right_answer()
    # if user given right answer
    if int(option_id) == right_answer.id:
        answer_right = True
        answers_count = test.get_count_user_answers(user.id)
        # If user given right answer on first try
        if answers_count == 0:
            # If user not in top 10, but answered on first try
            answer_points = settings.get_right_answer_points()
            message = strings.get_string('answer.right_answer_on_the_first_try').format(answer_points)
        else:
            # if user answered not on first try
            answer_points = 0
            message = strings.get_string('answer.right_answer_on_the_not_first_try').format(answers_count + 1,
                                                                                            answer_points)
    else:
        answer_right = False
        answer_points = 0
        message = strings.get_string('answer.wrong_answer')
    answer = Answer(user_id=user.id, points=answer_points, channel_id=channel.id, is_right=answer_right,
                    quiz_id=test.quiz.id)
    test.add_answer(answer)
    try:
        telegram_bot.answer_callback_query(query.id, message, show_alert=True)
    except ApiException:
        pass
