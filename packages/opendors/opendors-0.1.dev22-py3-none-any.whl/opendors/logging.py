import logging

_formatter = logging.Formatter(
    fmt="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(module)s.%(funcName)s > %(filename)s:%(lineno)s)"
)


def get_logger(name: str, log_file: str, log_level: str) -> logging.Logger:
    """
    Creates a logger for the given name. If a log file path string is passed,
    a file handler for the given file is attached to the logger if it doesn't already exist.

    :param name: The logger name
    :param log_file: The path string to the log file
    :param log_level: A valid string that describes the log level (CRITICAL, ERROR, WARNING, INFO, DEBUG)
    :return: The logger
    """
    logger = logging.getLogger(name)
    level = logging.getLevelName(log_level)
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(_formatter)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    return logger
