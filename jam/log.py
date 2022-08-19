import logging
import pathlib
import sys


def formatter():
    return logging.Formatter(
        fmt="%(levelname)s::%(message)s",
    )


def setupLogging():
    rootLogger = logging.getLogger(pathlib.Path(sys.argv[0]).name)
    rootLogger.setLevel(logging.ERROR)

    # Add logging to stderr
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter())
    rootLogger.addHandler(streamHandler)

    return rootLogger


log = setupLogging()
