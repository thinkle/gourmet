import re
from collections import defaultdict
from typing import List, Optional, Tuple

from .defaults.defaults import lang as defaults
from .defaults.defaults import langProperties as langProperties

note_separator_regexp = r'(;|\s+-\s+|--)'
note_separator_matcher = re.compile(note_separator_regexp)


class KeyManager:

    MAX_MATCHES = 10
    word_splitter = re.compile(r'\W+')

    __single = None

    @classmethod
    def instance(cls, recipe_manager=None):
        if KeyManager.__single is None:
            KeyManager.__single = cls(recipe_manager)

        return KeyManager.__single

    def __init__(self, recipe_manager=None):
        if recipe_manager is None:
            from . import recipeManager  # work around cyclic dependencies
            recipe_manager = recipeManager.default_rec_manager()
        self.rm = recipe_manager

        if self.rm.fetch_len(self.rm.keylookup_table) == 0:
            self.initialize_from_defaults()
        self.initialize_categories()

    @staticmethod
    def _snip_notes(s: str) -> str:
        m = note_separator_matcher.search(s)
        if not m:
            return s
        ret = s[:m.start()].strip()

        return ret if ret else s

    def initialize_from_defaults(self):
        dics = []
        for key, items in defaults.keydic.items():
            for i in items:
                dics.append({'ingkey': str(key),
                             'item': str(i),
                             'count': 1})
        self.rm.keylookup_table.insert().execute(dics)

    def regexp_for_all_words(self, txt):
        """Return a regexp to match any of the words in string."""
        regexp = r"(^|\W)("
        count = 0
        for w in self.word_splitter.split(txt):
            # for each keyword, we create a search term
            if w:  # no blank strings!
                count += 1
                regexp = "%s%s|" % (regexp, re.escape(w))
        regex = r"%s)(?=\W|$)" % (regexp[0:-1])  # slice off extra |
        if count:
            return re.compile(regex), count
        else:
            return None, count

    def initialize_categories(self):
        """We treat things like flour as categories, usually
        designated as "flour, all purpose" or "flour, whole wheat". We
        look for this sort of thing, assuming the noun, descriptor
        format has been followed previously. With our handy list, we
        will more easily be able to guess correctly that barley flour
        should be flour, barley"""
        self.cats = []
        for k in self.rm.get_unique_values('ingkey',
                                           self.rm.ingredients_table,
                                           deleted=False):
            fnd = k.find(',')
            if fnd != -1:
                self.cats.append(k[0:fnd])

    def grab_ordered_key_list(self, str):
        """We return a list of potential keys for string."""
        kl = self.look_for_key(str)
        gk = self.generate_key(str)
        nwlst = []
        added_gk = False
        for key, rnk in kl:
            if rnk < 0.9 and not added_gk:
                if not nwlst.__contains__(gk):
                    nwlst.append(gk)
                added_gk = True
            if not nwlst.__contains__(key):
                nwlst.append(key)
        if not added_gk:
            if not nwlst.__contains__(gk):
                nwlst.append(gk)
        return nwlst

    def get_key_fast(self, s) -> str:
        srch = self.rm.fetch_all(self.rm.keylookup_table, item=s,
                                 sort_by=[('count', 1)])
        if srch:
            return srch[-1].ingkey
        else:
            s = self._snip_notes(s)
            return self.generate_key(s)

    def get_key(self, txt: str, certainty: Optional[float] = 0.61) -> str:
        """Grab a single key. This is simply a best guess at the
        right key for an item (we can't be sure -- if we could be,
        we wouldn't need a key system in the first place!"""
        if not txt:
            return ''
        txt = self._snip_notes(txt)
        result = self.look_for_key(txt)
        if result and result[0][0] and result[0][1] > certainty:
            k = result[0][0]
        else:
            k = self.generate_key(txt)
        return k

    def look_for_key(self, txt: str) -> Optional[List[Tuple[str, float]]]:
        """Given a key, return a sorted list of potential matching known keys.

        By using some heuristics to find spelling variations, look up the
        database for similar entries.

        These are then sorted according to their matching score.

        A matching score is first established by giving a high score if a word
        appears in the database, and further refined by the word's occurrences
        relative to its other spellings.
        """
        txt = txt.casefold()
        retvals = defaultdict(float)

        # First look for matches for our full text (or full text +/- s)
        main_txts = [txt]
        main_txts.extend(defaults.guess_singulars(txt))
        if len(main_txts) == 1:
            main_txts.extend(defaults.guess_plurals(txt))

        # Look up for an entry in the ingredient table where the term t is
        # found in the value from the ingkey column.
        # By doing so, it establishes a baseline for the accuracy of t
        # being a useful keyword.
        for t in main_txts:
            entry = self.rm.fetch_one(self.rm.ingredients_table, ingkey=t)

            if entry is not None:
                retvals[t] = 0.9

            exact = self.rm.fetch_all(self.rm.keylookup_table, item=t)
            for o in exact:
                retvals[o.ingkey] += (float(o.count) / len(exact)) * 2

        # Part II -- look up individual words
        words = self.word_splitter.split(txt)
        nwords = len(words)
        extra_words = []

        # use heuristic rules to include plural and singular spellings
        for word in words:
            singulars = defaults.guess_singulars(word)
            for s in singulars:
                if s not in extra_words:
                    extra_words.append(s)
            if not singulars:  # the word was already singular
                for p in defaults.guess_plurals(word):
                    if p not in extra_words:
                        extra_words.append(p)
        words.extend(extra_words)

        for word in words:
            if not word:
                return
            srch = self.rm.fetch_all(self.rm.keylookup_table, word=word)
            total_count = sum([m.count for m in srch])
            for match in srch:
                # We have a lovely ratio.
                #
                # count      1
                # _____   x ___
                # total_count   words
                #
                # Where count is the number of times this word has
                # resulted in this key, matches is the number of keys
                # that match this word in all, and words is the number
                # of words we're dealing with.
                ik = match.ingkey
                words_in_key = len(ik.split())
                wordcount = words_in_key if words_in_key > nwords else nwords
                retvals[ik] += (match.count / total_count) * (1 / wordcount)

                # Add some probability if our word shows up in the key
                if word in ik:
                    retvals[ik] += 0.1

        retv = list(retvals.items())
        retv.sort(key=lambda x: x[1])
        return retv

    def generate_key(self, ingr: str) -> str:
        """Generate a generic-looking key from a string."""
        ingr = ingr.strip()

        if not langProperties['capitalisedNouns']:
            # language specific here - turn off the strip().lower() for eg.
            # German nouns that always start with an uppercase Letter.
            ingr = ingr.lower()

        if ingr.find(',') == -1:
            # if there are no commas, we see if it makes sense
            # to turn, e.g. whole-wheat bread into bread, whole-wheat
            words = ingr.split()
            if len(words) >= 2:
                if self.cats.__contains__(words[-1]):
                    ingr = f'{words[-1]}, {"".join(words[0:-1])}'
        return ingr
