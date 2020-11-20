"""
Main
"""

import argparse
import configparser
import logging
import os
import platform

import subtitle
# noinspection PyUnresolvedReferences
from version import (__app__, __version__)


class AppInit:
    # pylint: disable=too-few-public-methods
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

    class Logger:
        """ https://docs.python.org/3/library/logging.html """

        def __init__(self, name):
            """ initialize some logger values """
            self.name = name
            self.levels = {
                "critical": logging.CRITICAL, "error": logging.ERROR,
                "warning": logging.WARNING, "info": logging.INFO,
                "debug": logging.DEBUG, "notset": logging.NOTSET
            }
            self.formatter = logging.Formatter(
                "[%(levelname)s] [%(name)s] %(message)s"
            )

        def create(self, level: str):
            """ create a new logger instance """
            logger = logging.getLogger(self.name)
            stream = logging.StreamHandler()
            stream.setFormatter(self.formatter)
            logger.setLevel(self.levels.get(level, "notset"))
            logger.addHandler(stream)
            logger.debug("Initialized with loglevel: %s", level)
            return logger

    class ArgParse:
        """ https://docs.python.org/3/library/argparse.html """

        def __init__(self, name: str, version: float):
            self.logger = logging.getLogger(__app__).getChild(f"{self.__class__.__name__}")
            self.parser = argparse.ArgumentParser(
                prog=name,
                description="Automatically process subtitles",
                allow_abbrev=False)
            self.group = self.parser.add_mutually_exclusive_group()
            self.setup(name, version)

        def setup(self, name: str, version: float):
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

        def parse(self) -> dict:
            """
            parse_args() returns a Namespace which is not iterable
            vars() returns the Namespace object as a dict
            """
            args = vars(self.parser.parse_args())

            # TODO: Let user set log level via cmdline
            for key, value in args.items():
                self.logger.debug("%s: %s", key, value)

            return args

    class ConfigParse:
        """ https://docs.python.org/3/library/configparser.html """

        def __init__(self, conf: str):
            self.logger = logging.getLogger(__app__).getChild(f"{self.__class__.__name__}")
            self.config = configparser.ConfigParser(
                empty_lines_in_values=False
            )
            # TODO: check which additional options we'll include in user config
            self.config["blacklist"] = {
                "rules": []
            }
            self.config["extra"] = {
                "rules": {}
            }
            self.config_file = self.validate(conf)

        def validate(self, conf):
            """ See if the config file exists """
            if os.path.exists(conf):
                self.logger.debug("Parsing user config: %s", conf)
                return conf
            self.logger.debug("No user config, using defaults")
            return None

        def parse(self) -> dict:
            """ parse the config file """
            if self.config_file is not None:
                self.config.read(self.config_file)

            self.config_file = {
                option: dict(self.config.items(option)) for option in self.config.sections()
            }

            for key, value in self.config_file.items():
                self.logger.debug("%s: %s", key, value)

            return self.config_file


def main():
    """ Main function. """
    app = AppInit(__app__, __version__)
    logger = app.Logger(__app__).create("debug")
    for key, value in app.__dict__.items():
        logger.debug("%s: %s", key, value)
    # TODO: make sure config file opts are overwritten by cmd args if needed
    args = app.ArgParse(app.name, app.version).parse()
    conf = app.ConfigParse(app.CONF_FILE).parse()

    file_original = subtitle.Input(args["file"], args["encoding"]).parse()
    processor = subtitle.Processor()
    processor.clean(file_original)
