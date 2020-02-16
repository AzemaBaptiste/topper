import logging


def get_logger(name):
    """
    Return a logger with the specified name, creating it if necessary.
    :param name: module name
    :return: logging.Logger
    """
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
                        datefmt='%Y-%m-%d_%H:%M:%S',)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
