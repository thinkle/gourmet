import string, re, time, sys
from defaults import lang as defaults
from gdebug import *

class KeyManager:
    def __init__ (self,kd={}, rm=None):
        """We have a dictionary {item:[key1,key2],item:[key1]} which includes
        all existing keys. Then, we have fancy means of guessing new keys"""
        debug("start Keymanager.__init__",5)
        self.kd = kd
        if not self.kd:
            if rm:
                self.kd = KeyDictionary(rm)
            else:
                self.kd = defaults.keydic
        self.keys = []
        self.cooking_verbs=cooking_verbs
        self.ignored = ["and","with","of","for","cold","warm","finely","thinly","roughly","coarsely"]
        self.ignored.extend(self.cooking_verbs)
        self.ignored_regexp = re.compile("[,; ]?(" + string.join(self.ignored,"|") + ")[,; ]?")
        self.set_keylist()
        self.initialize_categories()
        debug("__init__ end",10)

    def make_regexp_for_strings (self, ignored):
        ret = "("
        ignored.join("|")

    def set_keylist (self):
        self.keys = []
        for vv in self.kd.values():
            for v in vv:
                if not self.keys.__contains__(v):
                    self.keys.append(v)
        self.keys.sort()

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

    def initialize_categories (self):
        """We treat things like flour as categories, usually
        designated as "flour, all purpose" or "flour, whole wheat". We
        look for this sort of thing, assuming the noun, descriptor
        format has been followed previously. With our handy list, we
        will more easily be able to guess correctly that barley flour
        should be flour, barley"""
        debug("Start initialize_categories",10)
        self.cats = []
        for vv in self.kd.values():
            for v in vv:
                fnd=string.find(v,',')
                if fnd != -1:
                    self.cats.append(v[0:fnd])
        debug("End initialize_categories",10)


    def get_key_fast (self, str):
        #if self.kd.has_key(str):
        #    return self.kd[str][0]
        if defaults.keydic.has_key(str):
            return defaults.keydic[str][0]
        else:
            return self.generate_key(str)

    def get_key (self, str, certainty=0.75):
        """Grab a single key. This is simply a best guess at the
        right key for an item (we can't be sure -- if we could be,
        we wouldn't need a key system in the first place!"""
        debug("Start get_key",10)
        result = self.look_for_key(str)
        if result and result[0][0] and result[0][1] > certainty:
            k=result[0][0]
        else:
            k=self.generate_key(str)
        debug("End get_key",10)
        return k

    def regexp_for_all_words (self, str):
        """Return a regexp to match any of the words in string."""
        regexp="(^|\W)("
        count=0
        for w in re.split("\W+",str):
            #for each keyword, we create a search term
            if w: #no blank strings!
                count += 1
                regexp="%s%s|"%(regexp,re.escape(w))
        regex="%s)(?=\W|$)"%(regexp[0:-1]) #slice off extra |
        if count:
            return re.compile(regex), count
        else:
            return None, count

    def look_for_key (self, str):

        """A mildly insane function, we take a string and
        return... something.  We simply return the key if there's a
        straightforward answer. Otherwise, we return a list of
        probabilities which looks like this [key, probablity] where
        key is the key and probability is a number between 0 and 1"""
        
        debug("Start look_for_key for %s"%str,10)
        retvals={}
        
        def append_to_retvals (itm, score):
            """Add itm to retval dict, assuming it's not already there.
            If it's already there, we ignore, so those calling us better
            make sure they call us first for high probabilities, etc."""
            flag = True
            for v in retvals.values():
                if v.__contains__(itm):
                    debug("already have %s"%itm,10)
                    flag=False
            if flag:
                if retvals.has_key(score):
                    retvals[score].append(itm)
                else:
                    retvals[score]=[itm]

        ## First we look ourselves up in the items list
        str = string.lower(str)
        if self.kd.has_key(str):
            keys = self.kd[str][0:]
            for key in keys:
                append_to_retvals(key,1)
            debug("look_for_key direct result!",10)
        ## If we're not directly on the list, we'll have to get
        ## a bit fancier -- let's see if our auto-generated key
        ## matches an existing key
        gkey = self.generate_key(str)
        if self.keys.__contains__(gkey):
            debug("look_for_key auto-generated result!",10)
            append_to_retvals(gkey,0.95)
            debug("retvals=%s"%retvals,10)
        ## If that fails, we'll have to look and see if we look
        ## like any of the existing items
        regexp,wcount=self.regexp_for_all_words(gkey)
        if wcount > 0: #only do this if we have some words!
            for itm in self.kd.keys():
                # now we multiply 0.9 * the fraction of words found
                eqval = 0.9*len(regexp.findall(itm))/wcount
                if eqval:
                    # If the key is longer than our key, then we multiply
                    # by the fraction of length (in other words, if the
                    # real key is 5 words long and we only match on 1,
                    # then we multiply by 0.2
                    kwcnt = len(itm.split())
                    if kwcnt > wcount:
                        eqval = eqval * (float(wcount)/float(kwcnt))
                        append_to_retvals(itm,eqval)
            ## Now lets make an ordered list of potential keys...
        retranked = retvals.items()
        retranked.sort()
        retranked.reverse()
        ret = []
        debug("DEBUG: retranked==%s"%retranked,10)
        for itm in retranked:
            for i in itm[1]:
                ret.append([i, itm[0]])
        debug("End look_for_key (complex result)",10)
        return ret
            
    def generate_key(self, ingr):
        """Generate a generic-looking key from a string."""
        timer = TimeAction('keymanager.generate_key 1',3)
        debug("Start generate_key(self,%s)"%ingr,10)
        ingr = string.strip(ingr)
        ingr = string.lower(ingr)
        timer.end()
        timer = TimeAction('keymanager.generate_key 2',3)
        ingr = self.remove_verbs(ingr)
        debug("verbless string=%s"%ingr,10)
        # we remove final s
        timer.end()
        timer = TimeAction('keymanager.generate_key 3',3)
        ingr=self.remove_final_s(ingr)
        timer.end()
        timer = TimeAction('keymanager.generate_key 4',3)
        ingr = self.remove_verbs(ingr)
        timer.end()
        timer = TimeAction('keymanager.generate_key 5',3)
        if string.find(ingr,',') == -1:
            # if there are no commas, we see if it makes sense
            # to turn, e.g. whole-wheat bread into bread, whole-wheat
            words = string.split(ingr)
            if len(words) >= 2:
                if self.cats.__contains__(words[-1]):
                    ingr = "%s, %s" %(words[-1],string.join(words[0:-1]))
        #if len(str) > 32:
        #    str = str[0:32]
        debug("End generate_key",10)
        timer.end()
        return ingr

    def remove_final_s (self, str, with_orig=1):
        """Returns a list, probably with just one word (made single),
        but possibly with potential variants for things that end funny:
        i.e. loaves will return loaf, loav and loave"""
        debug("Start remove_final_s",10)
        
        if irregular_plurals.has_key(str):
            retval=irregular_plurals[str]
        elif re.search("[szxo]es$", str):
            retval=str[0:-2]
        elif re.search("(us|ss)$",str):
            retval=str
        elif re.search("s$",str):
            retval=str[0:-1]
        else:
            retval = str
        debug("End remove_final_s",10)
        return retval

    def sing_equal(self, str1, str2):
        debug("Start sing_equal(self,%s,%s)"%(str1,str2),10)
        sing_str1 = self.remove_final_s(str1)
        sing_str2 = self.remove_final_s(str2)
        return sing_str1 == sing_str2


    def string_equal (self, str1, str2):
        """This returns negative if the words are not
        at all the same, 1 if they are exactly the same, and somewhere
        between if they look similar"""
        debug("Start string_equal",10)
        str1s = string.lower(string.strip(str1))
        str2s = string.lower(string.strip(str2))
        if str1s == str2s:
            return 1
        ## Now just try removing final 's'es from the whole string
        elif self.sing_equal(str1s, str2s):
            return 0.9
        ## Now we're going to have to get fancy.
        else:
            words1 = re.split("[ ,.:;]",str1s)
            words2 = re.split("[ ,.:;]",str2s)
            ## If there's only one word, then we've done all we can do
            self.remove_verbs(words1)
            self.remove_verbs(words2)
            if len(words1) == 1 and len(words2) == 1:
                return 0
            else:
                retval = 0
                for word1 in words1:
                    for word2 in words2:
                        if word1 == word2:
                            retval += 1
                        elif self.sing_equal(word1,word2):
                            retval += 0.9
                if retval:
                    return float(retval) / ((len(words1) + len(words2)) / float(2))
                else:
                    return 0

    def remove_verbs (self,words):
        """Handed a list of words, we remove anything from the
        list that matches a regexp in self.ignored"""
        debug("Start remove_verbs",10)
        stringp=True
        if type(words)==type([]):
            stringp=False
            words = string.join(words," ")
        words = words.split(';')[0] #we ignore everything after semicolon
        m = self.ignored_regexp.match(words)
        while m:
            words = words[0:m.start()] + words[m.end():]
            m = self.ignored_regexp.match(words)            
        if stringp:
            return words
        else:
            return words.split()

class KeyDictionary:
    def __init__ (self, rm):
        """We create a readonly dictionary based on the metakit iview table."""
        self.iview = rm.iview
        self.default = defaults.keydic

    def has_key (self, k):
        debug('has_key testing for %s'%k,10)
        if self.iview.select(item=k): return True
        elif self.default.has_key(k): return True
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
        ivw = self.iview.select(item=k)
        kvw = ivw.counts(ivw.ingkey, 'count')
        v = {}
        for k in kvw:
            v[k.ingkey] = k.count
        # we want to sort by the frequency of the
        # key -- with the most frequent key coming
        # first in the list we return.
        lst = v.items()
        lst.sort(self.srt_by_2nd)
        if not lst:
            return self.default[k]
        return map(lambda x: x[0], lst)

    def keys (self):
        ivw = self.iview.counts(self.iview.item,'count')
        ll = map(lambda i: i.item, ivw)
        ll.extend(self.default.keys())
        return ll

    def values (self):
        kvw = self.iview.counts(self.iview.ingkey,'count')
        ll = map(lambda k: [k.ingkey], kvw)
        ll.extend(self.default.values())
        return ll

    def items (self):
        lst = []
        for i in self.keys():
            lst.append((i, self.__getitem__(i)))
        lst.extend(self.default.items())
        return lst
        
            
irregular_plurals={
    "loaves":"loaf",
    "leaves":"leaf",
    "geese":"goose",
    "sheaves":"sheaf",
    }
    
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
