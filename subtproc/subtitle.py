"""
This module handles the reading and writing of a subtitle file
"""

import logging
import os
import sys

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

    def validate(self) -> str:
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
        except (UnicodeDecodeError, UnicodeError, LookupError) as error:
            LOGGER.error("%s", error)
            sys.exit()

        for sub in sub_list:
            sub_split = sub.split('\n')
            self.sub_contents[int(sub_split[0])] = {
                'time': sub_split[1].split(' --> '),
                'text': "\n".join(sub_split[2:])
            }

        LOGGER.info("Subtitle \"%s\" succesfully parsed!", self.subtitle)
        return self.sub_contents


class Processor:
    """ docstring for Process. """

    def __init__(self):
        self.regex = self.Regexer()

    def clean(self, subtitle):
        """ Clean """
        re_patterns = self.regex.patterns
        for number in subtitle:
            LOGGER.debug("line %s: %s", number, subtitle[number])

    def retime(self, sub, type, value):
        """ Allows for adding/subtracting time from the timecodes """
        # TODO: might also implement giving a start value and retiming the entire sub
        #  based on that value (shift)
        #  and what about recalculating framerate?

    class Regexer:
        """ Defines the different regexes and related functions """

        def __init__(self):
            import re

            # TODO: finetune these regexes, maybe some can be combined?
            #  look at todo.txt to see what other rules should be added
            # TODO: also figure out how we actually want to structure the replacement method
            self.patterns = {
                # repl will contain either a string value to replace with
                # or an int which represents the matchgroup which should be used
                'double_space':
                    {'pattern': re.compile(r"([^\S\n]){2,}"), 'repl': ' '},
                'space_before_punct':
                    {'pattern': re.compile(r"[^\S\n]+([.,:;!?])"), 'repl': 1},
                'dot_after_punct':
                    {'pattern': re.compile(r"([:!?])+([.,]+)"), 'repl': 1},
                'no_space_after_punct':
                # TODO: how to replace?
                    {'pattern': re.compile(r"([.,:;!?])[\w]+"), 'repl': ' '},
                'lower_l_not_cap_i':
                    {'pattern': re.compile(r"\w+([I])\w+"), 'repl': 'l'},
                'double_apostrophe':
                    {'pattern': re.compile(r"([']{2})"), 'repl': '"'},
                'one_line_dialogue':
                # TODO: how to replace?
                    {'pattern': re.compile(r"(^[-].+[.])[^\n]([-].+)"), 'repl': ' '},
                'missing_dialogue_line':
                # TODO: how to replace?
                    {'pattern': re.compile(r"(^[-].+)[\n]([^-].+)"), 'repl': ' '}
            }

        def match(self, rule, sub):
            """ Look for a match """

        def replace(self, rule, sub):
            """ Replace matching rule with sub """


class Output:
    """ Write the processed output to a new file """

    # TODO: probably a temp file first and then backup and replace the original
    def __init__(self, arg):
        self.arg = arg

    def write(self):
        """ Writes the cleaned subtitle to file """
