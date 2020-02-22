#!/usr/bin/env python3

"""
Main
"""

import argparse
import logging
import os
# import sys
import platform

import subtitle


class AppSetup:
    """ some app setup pre processing of sub """

    def __init__(self):
        # pylint: disable=invalid-name
        self.name = "subtproc"
        self.version = "0.0.1"
        self.OS = platform.uname()[0]
        self.HOME = os.getenv("HOME", os.getenv("USERPROFILE"))
        self.TMP_DIR = os.getenv("TMPDIR", "/tmp")
        # TODO: Maybe figure out how to support windows or mac
        self.CONF_DIR = os.getenv("XDG_CONFIG_HOME", os.path.join(self.HOME, ".config", self.name))
        self.CONF_FILE = os.path.join(self.CONF_DIR, f"{self.name}.conf")

    @staticmethod
    def log_init(level):
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

    def post_init(self, args):
        """ See if any directories/files need to be created """
        if not os.path.exists(self.CONF_DIR):
            LOGGER.debug("os.mkdir(self.CONF_DIR)")
        else:
            if not os.path.exists(self.CONF_FILE):
                LOGGER.debug("No config file present, ignoring")
            else:
                LOGGER.debug("Parsing user config")

    class ArgParse:
        """ https://docs.python.org/3/library/argparse.html """

        # pylint: disable=too-few-public-methods
        def __init__(self, name, version):
            self.parser = argparse.ArgumentParser(
                prog=name,
                # usage="{} [path/file] [-e <encoding>] [-v|-q]".format(name),
                description="Automatically process subtitles",
                # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                allow_abbrev=False)
            self.group = self.parser.add_mutually_exclusive_group()
            self.set_args(version)

        def set_args(self, version):
            """ Setup argparse arguments """
            self.parser.add_argument("file",
                                     action="store", type=str,
                                     help="subtitle to process")
            self.parser.add_argument("-o", "--output",
                                     action="store", type=str, dest="output",
                                     metavar="path",
                                     help="folder to store subtitles in")
            self.parser.add_argument("-e",
                                     action="store", type=str, dest="encoding",
                                     metavar="encoding", default="utf-8-sig",
                                     help="encoding to use when reading subtitle (default: utf-8)")
            self.group.add_argument("-v", "--verbose", dest="verbose",
                                    action="store_true", default=False,
                                    help="increase verbosity")
            self.group.add_argument("-q", "--quiet", dest="quiet",
                                    action="store_true", default=False,
                                    help="suppress output")
            self.parser.add_argument("--version",
                                     action="version", version=version)


def main():
    """ Main function. """
    app = AppSetup()
    for key, value in app.__dict__.items():
        LOGGER.debug("%s: %s", key, value)
    # TODO: Let user set log level via cmdline
    args = vars(app.ArgParse(app.name, app.version).parser.parse_args())
    for key, value in args.items():
        LOGGER.debug("%s: %s", key, value)
    app.post_init(args)

    file_handle = subtitle.Input(args["file"], args["encoding"])
    file_original = file_handle.read()
    file_cleaned = subtitle.Process(file_original)


if __name__ == "__main__":
    LOGGER = AppSetup.log_init("debug")
    main()
