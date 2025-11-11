import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def safe_method(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return None

    return wrapper
