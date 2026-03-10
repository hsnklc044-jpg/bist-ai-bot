from logger_engine import log_error


def safe_execute(func, *args, **kwargs):

    try:

        return func(*args, **kwargs)

    except Exception as e:

        log_error(f"Error in {func.__name__}: {str(e)}")

        return None
