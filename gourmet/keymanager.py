import re, time, sys
from .defaults.defaults import lang as defaults
from .defaults.defaults import langProperties as langProperties
from .gdebug import debug, TimeAction

note_separator_regexp = r'(;|\s+-\s+|--)'
note_separator_matcher = re.compile(note_separator_regexp)

def snip_notes (s):
    m = note_separator_matcher.search(s)
    if not m: return s
    ret = s[:m.start()].strip()
    if ret: return ret
    else: return s

class KeyManager(Exception):

    MAX_MATCHES = 10
    word_splitter = re.compile(r'\W+')

    __single = None

    def __init__ (self, kd={}, rm=None):
        if KeyManager.__single:
            raise KeyManager.__single
        else:
            KeyManager.__single = self
        self.kd = kd
        if not rm:
            from . import recipeManager
            rm = recipeManager.default_rec_manager()
        self.rm = rm
        self.cooking_verbs=cooking_verbs
        # This needs to be made sane i18n-wise
        self.ignored = defaults.IGNORE
        self.ignored.extend(self.cooking_verbs)
        self.ignored_regexp = re.compile("[,; ]?(" + '|'.join(self.ignored) + ")[,; ]?")
        if self.rm.fetch_len(self.rm.keylookup_table) == 0:
            self.initialize_from_defaults()
        self.initialize_categories()

    def initialize_from_defaults (self):
        dics = []
        for key,items in list(defaults.keydic.items()):
            for i in items:
                dics.append(
                    {'ingkey':str(key),
                     'item':str(i),
                     'count':1}
                    )
        self.rm.keylookup_table.insert().execute(dics)

    def make_regexp_for_strings (self, ignored):
        ret = "("
        ignored.join("|")

    def regexp_for_all_words (self, txt):
        """Return a regexp to match any of the words in string."""
        regexp=r"(^|\W)("
        count=0
        for w in self.word_splitter.split(txt):
            #for each keyword, we create a search term
            if w: #no blank strings!
                count += 1
                regexp="%s%s|"%(regexp,re.escape(w))
        regex="%s)(?=\W|$)"%(regexp[0:-1]) #slice off extra |
        if count:
            return re.compile(regex), count
        else:
            return None, count

    def initialize_categories (self):
        """We treat things like flour as categories, usually
        designated as "flour, all purpose" or "flour, whole wheat". We
        look for this sort of thing, assuming the noun, descriptor
        format has been followed previously. With our handy list, we
        will more easily be able to guess correctly that barley flour
        should be flour, barley"""
        debug("Start initialize_categories",10)
        self.cats = []
        for k in self.rm.get_unique_values('ingkey',self.rm.ingredients_table,deleted=False):
            fnd=k.find(',')
            if fnd != -1:
                self.cats.append(k[0:fnd])
        debug("End initialize_categories",10)

    def grab_ordered_key_list (self, str):
        debug("Start grab_ordered_key_list",10)
        """We return a list of potential keys for string."""
        kl=self.look_for_key(str)
        gk = self.generate_key(str)
        nwlst = []
        added_gk = False
        for key,rnk in kl:
            if rnk < 0.9 and not added_gk:
                if not nwlst.__contains__(gk):
                    nwlst.append(gk)
                added_gk = True
            if not nwlst.__contains__(key):
                nwlst.append(key)
        if not added_gk :
            if not nwlst.__contains__(gk):
                nwlst.append(gk)
        debug("End grab_ordered_key_list",10)
        return nwlst

    def get_key_fast (self, s):
        try:
            if s: srch = self.rm.fetch_all(self.rm.keylookup_table,
                                           item=s,
                                           sort_by=[('count',1)]
                                           )
            else: srch = None
        except:
            print('error seeking key for ',s)
            raise
        else:
            if srch: return srch[-1].ingkey
            else:
                s = snip_notes(s)
                return self.generate_key(s)

    def get_key (self,txt, certainty=0.61):
        """Grab a single key. This is simply a best guess at the
        right key for an item (we can't be sure -- if we could be,
        we wouldn't need a key system in the first place!"""
        debug("Start get_key %s"%str,10)
        if not txt: return ''
        txt = snip_notes(txt)
        result = self.look_for_key(txt)
        if result and result[0][0] and result[0][1] > certainty:
            k=result[0][0]
        else:
            k=self.generate_key(txt)
        debug("End get_key",10)
        return k

    def look_for_key (self, txt):
        """handed a key, return a sorted ALIST of potential keys and
        scores.

        The higher the score, the more probable the match.
        """

        txt = txt.lower()
        retvals = {}
        # First look for matches for our full text (or full text +/- s
        main_txts = [txt]
        main_txts.extend(defaults.guess_singulars(txt))
        if len(main_txts)==1:
            main_txts.extend(defaults.guess_plurals(txt))
        for t in main_txts:
            is_key = self.rm.fetch_one(self.rm.ingredients_table,ingkey=t)
            if is_key>=0:
                retvals[t]=.9
            exact = self.rm.fetch_all(self.rm.keylookup_table,
                                      item=t)
            if exact:
                for o in exact:
                    k = o.ingkey
                    if k not in retvals:
                        retvals[k]=0
                    retvals[k]+=(float(o.count)/len(exact))*2
        # Part II -- look up individual words
        words = self.word_splitter.split(txt)
        nwords = len(words)
        extra_words = []
        # Include plural and singular variants
        for w in words:
            singulars = defaults.guess_singulars(w)
            for s in singulars:
                if not s in extra_words: extra_words.append(s)
            if not singulars:
                for p in defaults.guess_plurals(w):
                    if not p in extra_words:
                        extra_words.append(p)
        words.extend(extra_words)
        for w in words:
            if not w:
                continue
            srch = self.rm.fetch_all(self.rm.keylookup_table,word=w)
            total_count = sum([m.count for m in srch])
            for m in srch:
                ik = m.ingkey
                if ik not in retvals:
                    retvals[ik]=0
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
                words_in_key = len(ik.split())
                if words_in_key > nwords: wordcount = words_in_key
                else: wordcount = nwords
                retvals[ik]+=(float(m.count)/total_count)*(float(1)/(wordcount))
                # Add some probability if our word shows up in the key
                if ik.find(w)>=0: retvals[ik]+=0.1
        retv = list(retvals.items())
        retv.sort(lambda a,b: a[1]<b[1] and 1 or a[1]>b[1] and -1 or 0)
        return retv

    def generate_key(self, ingr):
        """Generate a generic-looking key from a string."""
        timer = TimeAction('keymanager.generate_key 1',3)
        debug("Start generate_key(self,%s)"%ingr,10)
        ingr = ingr.strip()
        # language specific here - turn off the strip().lower() for German, 'cos:
        # i) german Nouns always start with an uppercase Letter.
        # ii) the function 'lower()' doesn't appear to work correctly with umlauts.
        if (not langProperties['capitalisedNouns']):
            # We want to use unicode's lower() method
            if not isinstance(ingr,str):
                ingr = str(ingr.decode('utf8'))
            ingr = ingr.lower()
        timer.end()
        timer = TimeAction('keymanager.generate_key 2',3)
        debug("verbless string=%s"%ingr,10)
        if ingr.find(',') == -1:
            # if there are no commas, we see if it makes sense
            # to turn, e.g. whole-wheat bread into bread, whole-wheat
            words = ingr.split()
            if len(words) >= 2:
                if self.cats.__contains__(words[-1]):
                    ingr = "%s, %s" %(words[-1],''.join(words[0:-1]))
        #if len(str) > 32:
        #    str = str[0:32]
        debug("End generate_key",10)
        timer.end()
        return ingr

    def sing_equal(self, str1, str2):
        debug("Start sing_equal(self,%s,%s)"%(str1,str2),10)
        sing_str1 = self.remove_final_s(str1)
        sing_str2 = self.remove_final_s(str2)
        return sing_str1 == sing_str2

    def remove_verbs (self,words):
        """Handed a list of words, we remove anything from the
        list that matches a regexp in self.ignored"""
        debug("Start remove_verbs",10)
        t=TimeAction('remove_verbs',0)
        stringp=True
        if type(words)==type([]):
            stringp=False
            words = " ".join(words)
        words = words.split(';')[0] #we ignore everything after semicolon
        words = words.split("--")[0] # we ignore everything after double dashes too!
        m = self.ignored_regexp.match(words)
        while m:
            words = words[0:m.start()] + words[m.end():]
            m = self.ignored_regexp.match(words)
        t.end()
        if stringp:
            return words
        else:
            return words.split()


class KeyDictionary:
    def __init__ (self, rm):
        """We create a readonly dictionary based on the metakit ingredients_table table."""
        self.rm = rm
        self.default = defaults.keydic

    def has_key (self, k):
        debug('has_key testing for %s'%k,1)
        if self.rm.fetch_one(self.rm.ingredients_table,item=k): return True
        elif k in self.default: return True
        else: return False

    def srt_by_2nd (self, i1, i2):
        """Sort by the reverse order of the second item in each of i1
        and i2"""
        if i1[1] < i2[1]:
            return 1
        if i2[1] < i1[1]:
            return -1
        else: return 0

    def __getitem__ (self, k):
        kvw = self.rm.fetch_count(
            self.rm.ingredients_table,
            'ingkey',
            sort_by=('count',-1),
            item=k
            )

    def keys (self):
        ll = self.rm.get_unique_values('item',self.rm.ingredients_table,deleted=False)
        ll.extend(list(self.default.keys()))
        return ll

    def values (self):
        ll = self.rm.get_unique_values('ingkey',self.rm.ingredients_table,deleted=False)
        ll.extend(list(self.default.values()))
        return ll

    def items (self):
        lst = []
        for i in list(self.keys()):
            lst.append((i, self.__getitem__(i)))
        lst.extend(list(self.default.items()))
        return lst

cooking_verbs=["cored",
               "peeled",
               "sliced",
               "chopped",
               "diced",
               "pureed",
               "blended",
               "grated",
               "minced",
               "cored",
               "heated",
               "warmed",
               "chilled"]

def get_keymanager (*args, **kwargs):
    try:
        return KeyManager(*args,**kwargs)
    except KeyManager as km:
        return km

if __name__ == '__main__':

    def timef (f):
        t = time.time()
        f()
        print(time.time()-t)
    import tempfile
    from . import recipeManager
    km = KeyManager(rm=recipeManager.RecipeManager(**recipeManager.dbargs))
    recipeManager.dbargs['file']=tempfile.mktemp('.mk')
    fkm = KeyManager(rm=recipeManager.RecipeManager(**recipeManager.dbargs))

