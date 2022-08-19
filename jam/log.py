import sys
import pathlib
import logging

# logging.basicConfig()


def formatter():
    return logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%d.%m.%y %I:%M:%S %p",
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
