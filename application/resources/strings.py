import json
import os
from typing import List, Tuple
from datetime import datetime

_basedir = os.path.abspath(os.path.dirname(__file__))

_strings = json.loads(open(os.path.join(_basedir, 'strings.json'), 'r', encoding='utf8').read())


def get_string(key: str) -> str:
    return _strings.get(key, 'no_string')


def from_test(test) -> str:
    test_content = '<b>Вопрос:</b>\n'
    test_content += test.question
    return test_content


def from_user_points_rating(user_points_list: List[Tuple[str, int]], start_date: datetime, end_date: datetime):
    format_date_str = '%d.%m.%Y'
    rating_content = '<b>Еженедельный рейтинг за {} - {}</b>' \
        .format(start_date.strftime(format_date_str),
                end_date.strftime(format_date_str))
    rating_content += '\n\n'
    counter = 1
    for user_points in user_points_list:
        rating_content += '{}. {} - {}\n'.format(counter, user_points[0], user_points[1])
        counter += 1
    return rating_content
