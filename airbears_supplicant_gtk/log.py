import os

from logging.config import dictConfig

SUPPLICANT_DIR = os.path.expanduser('~/.airbears_supplicant')
if not os.path.exists(SUPPLICANT_DIR):
    os.mkdir(SUPPLICANT_DIR)

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SUPPLICANT_DIR, 'supplicant.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}

dictConfig(LOGGING_CONFIG)
