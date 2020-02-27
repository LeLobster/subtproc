"""
This module handles the processing of subtitle lines
"""

import logging
import re

LOGGER = logging.getLogger("subtproc")


class Cleaner:
    """docstring for Cleaner."""

    def __init__(self):
        self.regexer = self.Regexer()

    def clean(self, line):
        re_patterns = self.regexer.regexes
        for p in re_patterns.keys():
            match = re.search(re_patterns[p], line["text"])
            if match is not None:
                LOGGER.warning("Found match with pattern: %s\n%s\n%s\n",
                               p, line["text"], match.groups()
                               )

    class Regexer:
        """Defines the different regexes"""

        def __init__(self):
            # TODO: finetune these regexes, maybe some can be combined?
            #  maybe add regex for situation like: haven 't
            #  and single lowercase i to upper
            self.regexes = {'double_space': re.compile(r"([^\S\n]){2,}"),
                            'space_before_punct': re.compile(r"[^\S\n]+([.,:;!?])"),
                            'dot_after_punct': re.compile(r"([:!?])+([.,]+)"),
                            'no_space_after_punct': re.compile(r"([.,:;!?])[\w]+"),
                            'lower_l_not_cap_i': re.compile(r"\w+([I])\w+"),
                            'double_apostrophe': re.compile(r"([']{2})"),
                            'one_line_dialogue': re.compile(r"(^[-].+[.])[^\n]([-].+)"),
                            'missing_dialogue_line': re.compile(r"(^[-].+)[\n]([^-].+)")}

        def replace(self):
            pass
