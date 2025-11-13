import logging


def pytest_addoption(parser):
    parser.addoption('--log-ignore', action='append', help="Ignore some loggers' log")
    parser.addini('log_ignore', help="Ignore some loggers' log")


def pytest_configure(config):
    logger_names = config.getoption('--log-ignore') or []
    if config.getini('log_ignore'):
        logger_names += config.getini('log_ignore').split('\n')
    logger_names = list(set([item.strip() for item in logger_names]))

    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL + 1)
        logger.propagate = False
        logger.addHandler(logging.NullHandler())
