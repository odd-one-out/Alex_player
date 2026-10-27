import logging
from functools import wraps

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

formatter = logging.Formatter('%(levelname)s-%(name)s %(asctime)s: %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

file_handler = logging.FileHandler('player.log', mode='a', encoding='utf-8')
file_handler.setLevel('DEBUG')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel('WARNING')
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def logger_decor(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        f(*args,**kwargs)
        logger.info('func: %s with args: %s worked successfully', f.__name__, args)
    return wrap


