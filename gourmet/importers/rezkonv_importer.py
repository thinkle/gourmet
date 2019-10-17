# -*- coding: utf-8 -*-
import mealmaster_importer, plaintext_importer, re
import gourmet.convert as convert
from gourmet.gdebug import debug, TimeAction

class rezconf_constants (mealmaster_importer.mmf_constants):
    def __init__ (self):
        mealmaster_importer.mmf_constants.__init__(self)
        for k,v in list({'Titel':'title',
                    'Kategorien':'category',
                    'Menge':'servings',
                    }.items()):
            self.recattrs[k]=v
        for k,v in list({}.items()):
            self.unit_conv[k]=v
        self.unit_convr = {}
        for k,v in list(self.unit_conv.items()):
            self.unit_convr[v]=k

rzc = rezconf_constants()
rzc_start_pattern=r"^(?i)([m=-][m=-][m=-][m=-][m=-]+)-*\s*(rezkonv).*"

class rezkonv_importer (mealmaster_importer.mmf_importer):
    # with long German words, you can end up with short lines in the middle
    # of a block of text, so we'll shorten the length at which we assume
    # a short line means the end of a paragraph.
    end_paragraph_length = 45

    def compile_regexps (self):
        """Compile our regular expressions for the rezkonv format.
        """
        testtimer = TimeAction('mealmaster_importer.compile_regexps',10)
        debug("start compile_regexps",5)
        plaintext_importer.TextImporter.compile_regexps(self)
        self.start_matcher = re.compile(rzc_start_pattern)
        self.end_matcher = re.compile("^[=M-][=M-][=M-][=M-][=M-]\s*$")
        self.group_matcher = re.compile("^\s*([=M-][=M-][=M-][=M-][=M-]+)-*\s*([^-]+)\s*-*",re.IGNORECASE)
        self.ing_cont_matcher = re.compile("^\s*[-;]")
        self.ing_opt_matcher = re.compile("(.+?)\s*\(?\s*optional\)?\s*$",re.IGNORECASE)
        # or or the German, oder
        self.ing_or_matcher = re.compile("^[-= ]*[Oo][dD]?[eE]?[Rr][-= ]*$",re.IGNORECASE)
        self.variation_matcher = re.compile("^\s*(VARIATION|HINT|NOTES?|VERÄNDERUNG|VARIANTEN|TIPANMERKUNGEN)(:.*)?",re.IGNORECASE)
        # a crude ingredient matcher -- we look for two numbers, intermingled with spaces
        # followed by a space or more, followed by a two digit unit (or spaces)
        self.ing_num_matcher = re.compile(
            "^\s*%(top)s%(num)s+\s+[A-Za-z ][A-Za-z ]? .*"%{'top':convert.DIVIDEND_REGEXP,
                                                             'num':convert.NUMBER_REGEXP},
            re.IGNORECASE)
        self.amt_field_matcher = convert.NUMBER_MATCHER
        # we build a regexp to match anything that looks like
        # this: ^\s*ATTRIBUTE: Some entry of some kind...$
        attrmatch="^\s*("
        self.mmf = rzc
        for k in list(self.mmf.recattrs.keys()):
            attrmatch += "%s|"%re.escape(k)
        attrmatch="%s):\s*(.*)\s*$"%attrmatch[0:-1]
        self.attr_matcher = re.compile(attrmatch)
        testtimer.end()

    def is_ingredient (self, l):
        """Return true if the line looks like an ingredient.
        """
        if self.ing_num_matcher.match(l):
            return True
        if len(l) >= 5 and self.blank_matcher.match(l[0:2]):
            return True


