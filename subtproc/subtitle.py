"""
This module handles the reading and writing of a subtitle file
"""

import logging
import os
import sys

import cleaner as clnr

LOGGER = logging.getLogger("subtproc")


class Input:
    """ Input """

    def __init__(self, file: str, enc: str):
        self.subtitle = file
        self.encoding = enc
        # TODO: look at what has to be changed to support ssa and ass
        self.supported_exts = ["srt", "ssa", "ass"]
        self.sub_contents = {}
        self.validate()

    def validate(self):
        """ Validate the provided file """
        if not os.path.isfile(self.subtitle):
            LOGGER.error("%s not found!", self.subtitle)
            sys.exit()
        else:
            ext = os.path.splitext(self.subtitle)[-1].lstrip(".")
            if ext not in self.supported_exts:
                LOGGER.warning("%s extension is not supported!", ext)
                sys.exit()
            return self.subtitle

    def parse(self) -> dict:
        """ Store subtitle information in a dict """
        try:
            with open(self.subtitle, "r", encoding=self.encoding) as sub_obj:
                sub_list = sub_obj.read().split("\n\n")

            for sub in sub_list:
                sub_split = sub.split('\n')
                self.sub_contents[int(sub_split[0])] = {
                    'time': sub_split[1], 'text': "\n".join(sub_split[2:])
                }

        except (UnicodeDecodeError, UnicodeError, LookupError) as error:
            LOGGER.warning("%s", error)
            sys.exit()

        LOGGER.debug("Subtitle \"%s\" succesfully parsed!", self.subtitle)
        return self.sub_contents


class Process:
    """docstring for Process."""

    def __init__(self, sub):
        self.subtitle = sub
        cleaner = clnr.Cleaner()
        for number in self.subtitle:
            LOGGER.debug("Checking line: %s", number)
            cleaner.clean(self.subtitle[number])


class Output:
    """docstring for Output."""

    def __init__(self, arg):
        self.arg = arg

    def write(self):
        """ Writes the cleaned subtitle to file """
        pass
