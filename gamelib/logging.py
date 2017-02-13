import logging
import logging.config
import sys

from gamelib import streamlog


class DebugOnly(logging.Filter):

    def filter(self, record):
        # non-zero return means we log this message
        return record.levelno == logging.DEBUG


def _get_config_dict(log_level):

    _ansi = {
        'reset': '\x1b[0m',
        'norm': '\x1b[22m',
        'purple': '\x1b[35m',
        'white': '\x1b[37m',
        'cyan': '\x1b[36m',
        'red': '\x1b[31;1m',
    }

    _1 = _ansi['purple']
    _2 = _ansi['purple']
    _h = _ansi['cyan']
    _t = _ansi['white']
    # log_level = logging.DEBUG if debug else logging.INFO
    config_dict = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'custom': {
                'format': (_1 + '[' + _2 + '%(asctime)s' +
                           _1 + ' - ' + _h + '%(name)s' +
                           _1 + ':' + _h + '%(lineno)s' +
                           _1 + ' - ' + _2 + '%(levelname)s' +
                           _1 + '] __beg__\n' +
                           _t + '%(message)s' +
                           _1 + '\n__end__' +
                           _1 + _ansi['reset']
                           ),
                'datefmt': '%y-%m-%d %H:%M:%S',
            },
            'custom_info': {
                'format': (_1 + '[' + _2 + '%(asctime)s' +
                           _1 + ' - ' + _h + '%(name)s' +
                           _1 + ':' + _h + '%(lineno)s' +
                           _1 + ' - ' + _2 + '%(levelname)s' +
                           _1 + '] ' +
                           _t + '%(message)s' +
                           _1 + _ansi['reset']
                           ),
                'datefmt': '%y-%m-%d %H:%M:%S',
            },
            'plain': {
                'format': ('[%(asctime)s - %(name)s:%(lineno)s' +
                           ' - %(levelname)s] %(message)s'
                           ),
                'datefmt': '%y-%m-%d %H:%M:%S',
            },
        },
        'filters': {
            'debug_only': {
                '()': DebugOnly,
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'custom',
                'filters': ['debug_only']
            },
            'console_info': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'custom_info'
            },
        },
        'loggers': {
            'root': {
                'handlers': ['console_info', 'console'],
                'propogate': True,
                'level': log_level,
            },
            'boto3': {
                'handlers': ['null'],
                'propogate': True,
                'level': logging.WARNING,
            },
            'botocore': {
                'handlers': ['null'],
                'propogate': True,
                'level': logging.WARNING,
            },
            's3transfer': {
                'handlers': ['null'],
                'propogate': True,
                'level': logging.WARNING,
            },
            '': {
                'handlers': ['console_info', 'console'],
                'propogate': True,
                'level': log_level,
            }
        }
    }
    return config_dict


def config(log_level='DEBUG'):
    """Setup custom logging options."""
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level)
    config_dict = _get_config_dict(log_level)
    logging.config.dictConfig(config_dict)


def log_to(_file, logger=None, debug=False, level=logging.INFO):
    """Add a FileHandler to the root logger.

    Arguments:
        logger: The logging object. Defaults to the root logger.
        _file: The file path.
    Return:
        The file handler object.
    Raises:
        None.
    """
    config_dict = _get_config_dict(debug)
    handler = logging.FileHandler(_file)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt=config_dict['formatters']['plain']['format'],
        datefmt=config_dict['formatters']['plain']['datefmt'],
    )
    handler.setFormatter(formatter)

    if not logger:
        # add to root logger!
        logger = logging.getLogger()
    logger.addHandler(handler)
    return handler


def stop_file_loggers(self, logger=None):
    """Remove FileHandlers from the logger.

    Arguments:
        logger: The logging object. Defaults to the root logger.
    Return:
        None.
    Raises:
        None.
    """
    if not logger:
        logger = logging.getLogger()  # default to root logger
    logger.handlers = [
        h for h in logger.handlers
        if not isinstance(h, logging.FileHandler)
    ]
    return


def remove_handler(handler, logger=None):
    """Remove FileHandlers from the logger.

    Arguments:
        logger: The logging object. Defaults to the root logger.
    Return:
        None.
    Raises:
        None.
    """
    if not logger:
        logger = logging.getLogger()  # default to root logger
    logger.handlers = [
        h for h in logger.handlers
        if not h == handler
    ]
    return


"""Redirect stderr to and from logging."""
TMP_STDERR = None


def stderr_to_log():
    """Setup redirect of stderr to logging."""
    # backup stderr
    global TMP_STDERR
    if TMP_STDERR is None:
        TMP_STDERR = sys.stderr
    else:
        return  # already logging stderr
    logger = logging.getLogger('STDERR')
    s2l = streamlog.StreamLogger(logger, logging.ERROR)
    sys.stderr = s2l
    return


def restore_stderr():
    """Revert stderr from logging."""
    global TMP_STDERR
    if TMP_STDERR is not None:
        sys.stderr = TMP_STDERR
        TMP_STDERR = None
    return
