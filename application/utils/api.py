def error_message(code: int, *errors):
    return {
        'code': code,
        'errors': errors
    }