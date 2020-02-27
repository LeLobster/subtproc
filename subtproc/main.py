#!/usr/bin/env python3

"""
Main
"""

import argparse
import configparser
import logging
import os
import platform


def logger_init(level: str):
    """ Initialize the logger """
    logger = logging.getLogger("subtproc")
    stream = logging.StreamHandler()
    log_levels = {
        "critical": logging.CRITICAL, "error": logging.ERROR,
        "warning": logging.WARNING, "info": logging.INFO,
        "debug": logging.DEBUG, "notset": logging.NOTSET
    }
    logger.setLevel(log_levels.get(level, "notset"))
    stream.setFormatter(logging.Formatter(
        '[%(levelname)s] %(message)s'
    ))
    logger.addHandler(stream)
    logger.debug("Logger initialized with loglevel: %s", level)
    return logger


class AppSetup:
    """ some app setup pre processing of sub """

    def __init__(self, name: str, version: float):
        # pylint: disable=invalid-name
        self.name = name
        self.version = version
        self.OS = platform.uname()[0]
        self.HOME = os.getenv("HOME", os.getenv("USERPROFILE"))
        self.TMP_DIR = os.getenv("TMPDIR", "/tmp")
        # TODO: Maybe figure out how to support windows and/or mac
        self.CONF_DIR = os.path.join(
            os.getenv("XDG_CONFIG_HOME", os.path.join(self.HOME, ".config")),
            self.name
        )
        self.CONF_FILE = os.path.join(self.CONF_DIR, f"{self.name}.conf")

    class ArgParse:
        """ https://docs.python.org/3/library/argparse.html """

        def __init__(self, name: str, version: float):
            self.parser = argparse.ArgumentParser(
                prog=name,
                description="Automatically process subtitles",
                allow_abbrev=False)
            self.group = self.parser.add_mutually_exclusive_group()
            self.setup_args(name, version)

        def setup_args(self, name: str, version: float):
            """ Setup argparse arguments """
            self.parser.add_argument("file",
                                     action="store", type=str,
                                     help="subtitle to process")
            self.parser.add_argument("-o", "--output", default=os.getcwd(),
                                     action="store", type=str, dest="output",
                                     metavar="path",
                                     help="folder to store subtitles in")
            self.parser.add_argument("-e",
                                     action="store", type=str, dest="encoding",
                                     metavar="encoding", default="utf-8-sig",
                                     help="encoding to use when reading subtitle (default: utf-8)")
            self.group.add_argument("-v", "--verbose", default=False,
                                    action="store_true", dest="verbose",
                                    help="increase verbosity")
            self.group.add_argument("-q", "--quiet", default=False,
                                    action="store_true", dest="quiet",
                                    help="suppress output")
            self.parser.add_argument("--version", action="version",
                                     version=f"{name} version {version}")

        def process_args(self):
            """
            parse_args() returns a Namespace which is not iterable
            vars() returns the Namespace object as a dict
            """
            args = vars(self.parser.parse_args())

            # TODO: Let user set log level via cmdline
            for key, value in args.items():
                LOGGER.debug("[args] %s: %s", key, value)

            return args

    class ConfigParse:
        def __init__(self, conf):
            self.config = configparser.ConfigParser()
            self.config['DEFAULT'] = {
                'blacklist': 'None'
            }
            self.config_file = conf

        def validate(self):
            """ See if the config file exists """
            # TODO: make sure config file opts are overwritten by cmd args
            if not os.path.exists(self.config_file):
                LOGGER.debug("No config file present, ignoring")
            else:
                LOGGER.debug("Parsing user config")


def main():
    """ Main function. """
    app = AppSetup("subtproc", 0.15)
    for key, value in app.__dict__.items():
        LOGGER.debug("[app] %s: %s", key, value)
    args = app.ArgParse(app.name, app.version).process_args()
    conf = app.ConfigParse(app.CONF_FILE).validate()

    # file_handle = subtitle.Input(args["file"], args["encoding"])
    # file_original = file_handle.read()
    # file_cleaned = subtitle.Process(file_original)


if __name__ == "__main__":
    LOGGER = logger_init("debug")
    main()
