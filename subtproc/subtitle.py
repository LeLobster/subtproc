"""
This module handles the reading and writing of a subtitle file
"""

import logging
import os
import re
import sys

from __version__ import __name__


class Input:
    """ Input """

    def __init__(self, file: str, enc: str):
        self.logger = logging.getLogger(__name__).getChild(f"{self.__class__.__name__}")
        self.subtitle = file
        self.encoding = enc
        # TODO: look at what has to be changed to support ssa and ass
        self.supported_exts = ["srt", "ssa", "ass"]
        self.sub_contents = {}
        self.validate()

    def validate(self) -> str:
        """ Validate the provided file """
        if not os.path.isfile(self.subtitle):
            self.logger.error("%s not found!", self.subtitle)
            sys.exit()
        else:
            ext = os.path.splitext(self.subtitle)[-1].lstrip(".")
            if ext not in self.supported_exts:
                self.logger.warning("%s extension is not supported!", ext)
                sys.exit()
        return self.subtitle

    def parse(self) -> dict:
        """
        Store subtitle information in a dict

        List of standard encodings
        https://docs.python.org/3/library/codecs.html#standard-encodings
        """
        __re_sub_line = re.compile(
            r'(?#line_number)(\d{1,3})\n'
            r'(?#time_stamp)(\d{2}:.+--> \d{2}:.+)\n'
            r'(?#text_content)((?:.+(?:\n.+)?|\n))'
        )
        try:
            with open(self.subtitle, "r", encoding=self.encoding) as sub_obj:
                sub_list = __re_sub_line.findall(sub_obj.read())
        except (UnicodeDecodeError, UnicodeError, LookupError) as error:
            self.logger.error("%s", error)
            sys.exit()

        for sub in sub_list:
            try:
                self.sub_contents[int(sub[0])] = {
                    'time': sub[1].split(' --> '),
                    'text': sub[2]
                }
            except ValueError as e:
                # this will indicate a wrong encoding used
                # but one thats still able to open the file and not produce a
                # error during the inintial parsing
                # TODO: looks at whats actually happening here
                self.logger.error("%s", e)
                sys.exit()

        self.logger.info("Subtitle \"%s\" succesfully parsed!", os.path.split(self.subtitle)[-1])
        return self.sub_contents


class Processor:
    """ docstring for Process. """

    def __init__(self):
        self.logger = logging.getLogger(__name__).getChild(f"{self.__class__.__name__}")
        self.logger.setLevel(logging.WARNING)
        self.regex = self.Regexer()

    def clean(self, subtitle: dict) -> dict:
        """ Clean """
        for line in subtitle.keys():
            line_current = subtitle[line]["text"]
            self.logger.debug("Checking line %s:\n\t%s", line, line_current.replace("\n", "\\n"))
            for pattern in self.regex.patterns:
                match_obj = self.regex.match(pattern, line_current)
                if match_obj:
                    line_current = self.regex.replace(pattern, line_current)
            subtitle[line]["text"] = line_current
        return subtitle

    def retime(self, sub, method, value):
        """ Allows for adding/subtracting time from the timecodes """
        # TODO: might also implement giving a start value and retiming the entire sub
        #  based on that value (shift)
        #  and what about recalculating framerate?

    class Regexer:
        """ Defines the different regexes and related functions """

        def __init__(self):
            self.logger = logging.getLogger(__name__).getChild(f"{self.__class__.__name__}")
            # TODO: finetune these regexes, maybe some can be combined?
            #  look at todo.txt to see what other rules should be added
            """
            https://docs.python.org/3/library/re.html#re.sub
            here repl can contain either a string value for replacing
            or a backreference pattern including the matchgroups to use
            """
            self.patterns = {
                # @double_space
                # MATCHES: any that is 2 or more of whitespace
                # REPLACES: with one space
                # converts multiple spaces to a single space
                'double_space':
                    {'pattern': re.compile(r'([^\S\n]){2,}'), 'repl': " "},
                # @space_before_punct
                # MATCHES: one or more whitespace followed by a char in the set
                # REPLACES: with group 1
                # removes any whitespace in front of puncuation marks
                'space_before_punct':
                    {'pattern': re.compile(r'[^\S\n]+([.,:;!?%$])'), 'repl': r"\g<1>"},
                # @dot_after_punct
                # MATCHES: any one char from the first set, followed by 1 from the second
                # REPLACES: with group 1
                # sometimes caused by OCR errors
                'dot_after_punct':
                    {'pattern': re.compile(r'([:;!?%$])[.,]'), 'repl': r"\g<1>"},
                # @no_space_after_punct
                # MATCHES: any except dot, any char from the second set, followed by 1 or more word char
                # REPLACES: with group 1, a space, and then group 2
                # adds a whitespace after punctuation marks
                # note: we don't include ['"] here because ('n|"n) are valid
                'no_space_after_punct':
                    {'pattern': re.compile(r'([^.][.,:;!?%$])([a-zA-Z]+)'), 'repl': r"\g<1> \g<2>"},
                # @lower_l_not_upper_i
                # MATCHES: zero or one of uppercase, one or more of lowercase,
                #   one uppercase I, and one or more of lowercase
                # REPLACES: with group 1, a lowercase l, and then group 2
                # we replace the uppercase I in lowercase words with a lowercase l
                'lower_l_not_upper_i':
                    {'pattern': re.compile(r'\b([A-Z]?[a-z]+)[I]([a-z]+)'), 'repl': r"\g<1>l\g<2>"},
                # @sungle_upper_i_not_lower
                # MATCHES: lowercase i followed by one or more whitespace or any one of the set
                # REPLACES: with group 1
                # a single lowercase i followed by a space or puncuation is converted to uppercase
                'single_upper_i_not_lower':
                    {'pattern': re.compile(r'\b[i]([^\S\n]+|[,.?!])'), 'repl': r"I\g<1>"},
                # @double_apostrophe
                # MATCHES: two apostrophes
                # REPLACES: with a single quotation mark
                # common OCR error
                'double_apostrophe':
                    {'pattern': re.compile(r'([\']{2})'), 'repl': '"'},
                # @one_line_dialogue
                # MATCHES: dash at start of line, one or more of any char, followed by end punctuation,
                #   any char that is not line-feed, a dash, one or more of any char, followed by end punctuation
                #   at the end of the line
                # REPLACES: with group 1, a line-feed char, and then group 2
                # both sentences are wrapped in a match group and a newline is inserted in between
                'one_line_dialogue':
                    {'pattern': re.compile(r'(^[-].+[.?!])[^\n]([-].+$)'), 'repl': r"\g<1>\n\g<2>"},
                # @missing_dialogue_line
                # MATCHES: line not starting with a dash or whitespace, one or more of any char,
                #   a line-feed char, line starting with dash, followed by one of more of any char to end of line
                # REPLACES: with a dash, group 1 (which includes the newline), and then group 2
                # adds a missing dialogue line to group 1
                'missing_dialogue_line':
                    {'pattern': re.compile(r'^([^-\s].+[\n])^([-].+)$'), 'repl': r"- \g<1>\g<2>"}
            }

        def match(self, rule: str, sub: str):
            """ Look for a pattern match in sub """
            # re.search only return the first match it finds
            # but re.sub replaces all occurances
            return re.search(self.patterns[rule]['pattern'], sub)

        def replace(self, rule: str, sub: str) -> str:
            """ Replace matching rule with sub """
            self.logger.debug("Matched line on rule: %s\n\t%s", rule, sub.replace("\n", "\\n"))
            sub = re.sub(self.patterns[rule]['pattern'], self.patterns[rule]['repl'], sub)
            self.logger.debug("New line is:\n\t%s\n", sub.replace("\n", "\\n"))
            return sub


class Output:
    """ Write the processed output to a new file """

    # TODO: probably a temp file first and then backup and replace the original
    def __init__(self, arg):
        self.logger = logging.getLogger(__name__).getChild(f"{self.__class__.__name__}")
        self.arg = arg

    def write(self):
        """ Writes the cleaned subtitle to file """
