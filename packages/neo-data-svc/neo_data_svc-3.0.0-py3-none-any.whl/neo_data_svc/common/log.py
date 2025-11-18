import logging
from functools import wraps


def NDS_log(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(f.__module__)
        logger.info(f"{f.__name__} => {args}, {kwargs}")

        try:
            result = await f(*args, **kwargs)
            logger.info(result)
            return result
        except Exception as e:
            logger.exception(f"{f.__name__} => {e}")
            raise

    return wrapper
