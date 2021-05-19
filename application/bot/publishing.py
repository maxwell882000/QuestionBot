from application import telegram_bot
from application.core.models import Test, Channel, Answer, BotUser
from application.resources import strings, keyboards
import os


def publish_rating():
    channels = Channel.query.all()
    for channel in channels:
        quiz = channel.get_current_quiz()
        if quiz:
            user_points = Answer.get_summary_user_points_by_channel_and_period(quiz.id, quiz.top_count)
            username_points = []
            for user_point in user_points:
                user = BotUser.get_by_id(user_point[0])
                username = user.first_name
                if user.last_name:
                    username += " %s" % user.last_name
                if user.username:
                    username += " - %s" % user.username
                username_points.append((username, user_point[1]))
            rating_message = strings.from_user_points_rating(username_points, quiz.start_date, quiz.end_date)
            telegram_bot.send_message(channel.chat_id, rating_message, parse_mode='HTML')


def publish_test(test_id: int):
    test = Test.get_by_id(test_id)
    if test.published:
        return
    channel_chat_id = test.quiz.channel.chat_id
    test_message = strings.from_test(test)
    keyboard = keyboards.from_test_options(test.options.all())
    if test.file_path:
        file = open(test.file_path, 'rb')
        _, file_ext = os.path.splitext(test.file_path)
        if file_ext in ['.jpg', '.png']:
            telegram_bot.send_photo(channel_chat_id,
                                    file,
                                    caption=test_message,
                                    reply_markup=keyboard, parse_mode='HTML')
        else:
            telegram_bot.send_document(channel_chat_id,
                                       file,
                                       caption=test_message,
                                       reply_markup=keyboard, parse_mode='HTML')
    else:
        telegram_bot.send_message(channel_chat_id, test_message, reply_markup=keyboard, parse_mode='HTML')
    test.make_published()
