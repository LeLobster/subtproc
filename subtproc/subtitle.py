"""
This module handles the reading and writing of a subtitle file
"""

import logging
import os
import re
import sys

import cleaner as clnr

LOGGER = logging.getLogger("subtproc")


class Input:
    """ Input """

    def __init__(self, sub, enc):
        self.subtitle = sub
        self.encoding = enc
        self.subtitle_exts = ("srt", "ssa", "ass")
        self.sub_contents = {}
        self.check()

    def check(self):
        """ Validate the provided file """
        if not os.path.isfile(self.subtitle):
            LOGGER.warning("%s not found!", self.subtitle)
            sys.exit()
        else:
            ext = os.path.splitext(self.subtitle)[-1].lstrip(".")
            if ext not in self.subtitle_exts:
                LOGGER.warning("%s extension is not supported!", ext)
                sys.exit()
            else:
                return self.subtitle

    def read(self):
        """ Store subtitle information in a dict """
        _re_sub_line_number = re.compile(r'^\d+$')
        _re_time_codes = re.compile(r"""
            # timecodes are formatted as HH:MM:SS,MS --> HH:MM:SS,MS
            ^(\d{2}[:]\d{2}[:]\d{2}[,]\d+)
            \s-->\s
            (\d{2}[:]\d{2}[:]\d{2}[,]\d+)
        """, re.VERBOSE)

        try:
            # Open the file and while iterating over each line
            # store the line number, time (split in a list) and textcontent
            with open(self.subtitle, 'r', encoding=self.encoding) as sub:

                current_line = 0

                for line in sub:
                    if bool(_re_sub_line_number.search(line)):
                        # TODO: How to handle textcontent which consists only of numbers?
                        current_line = int((line.strip('\n')))
                        self.sub_contents[current_line] = {'time': '', 'text': ''}
                    elif ' --> ' in line:
                        # Store timecodes in a list
                        tc = _re_time_codes.search(line)
                        self.sub_contents[current_line]['time'] = [tc.group(1), tc.group(2)]
                    elif line != '\n':
                        # Else it's just text
                        self.sub_contents[current_line]['text'] += line

        except (UnicodeDecodeError, UnicodeError, LookupError) as error:
            LOGGER.warning("%s", error)
            sys.exit()

        LOGGER.debug("\"%s\" succesfully parsed!", self.subtitle)
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
