#!/usr/bin/python
import gtk # only needed for threading voodoo
import rmetakit, keymanager, convert, time
from gdebug import debug

class importer:
    def __init__ (self, rd, threaded=False):
        self.rd=rd
        self.position=0
        self.group=None
        self.threaded=threaded
        # allow threaded calls to pause
        self.suspended = False
        # allow threaded calls to be termintaed (this
        # has to be implemented in subclasses).
        self.terminated = False
        if hasattr(self.rd,'km'):
            debug('Using existing keymanager',2)
            self.km=self.rd.km
        else:
            debug('Making new keymanager',2)
            self.km=keymanager.KeyManager(rm=self.rd)
        if not self.threaded:
            ## run ourselves, unless we're threaded, in which
            ## case we'll want to call run explicitly from outside.
            self.run()

    def run (self):
        pass

    def check_for_sleep (self):
        if self.terminated:
            raise "Importer Terminated!"
        while self.suspended:
            if self.terminated:
                raise "Importer Terminated!"
            time.sleep(1)        

    def start_rec (self, dict=None, base="import"):
        self.check_for_sleep()
        self.added_ings=[]
        self.group = None
        if dict:
            self.rec=dict
        else:
            self.rec = {}
        if not self.rec.has_key('id'):
            self.rec['id']=self.rd.new_id(base)
        debug('New Import\'s ID=%s'%self.rec['id'])

    def commit_rec (self):
        if self.rec.has_key('servings'):
            self.rec['servings']=str(self.convert_servings(self.rec['servings']))
        for k,v in self.rec.items():
            try:
                self.rec[k]=v.strip()
            except:
                pass
        self.rd.add_rec(self.rec)
        self.check_for_sleep()

    def convert_servings (self, str):
        debug('converting servings for %s'%str,5)
        try:
            return float(str)
        except:
            try:
                return convert.frac_to_float(str)
            except:
                m=re.match("([0-9/. ]+)",str)
                if m:
                    num=m.groups()[0]
                    try:
                        return float(num)
                    except:
                        try:
                            return convert.frac_to_float(num)
                        except:
                            return ""
                else:
                    return ""
            
    def start_ing (self, **kwargs):        
        self.ing=kwargs
        self.ing['id']=self.rec['id']
                 
    def commit_ing (self):
        if not ((self.ing.has_key('refid') and self.ing['refid']) or (self.ing.has_key('key') and self.ing['key'])):
            self.ing['key']=self.km.get_key(self.ing['item'],0.9)
        if not (self.ing.has_key('position') and self.ing['position']):
            self.ing['position']=self.position
            self.position+=1
        if self.group:
            self.ing['group']=self.group
        self.added_ings.append(self.rd.add_ing(self.ing))

    def add_amt (self, amount):
        """We should NEVER get non-numeric amounts.
        Amounts must contain [/.0-9 ] e.g. 1.2 or 1 1/5
        or 1/3 etc."""
        try:
            self.ing['amount']=convert.frac_to_float(amount)
        except:
            self.ing['amount']=float(amount)

    def add_ref (self, id):
        self.ing['refid']=id
        self.ing['unit']='recipe'

    def add_item (self, item):
        self.ing['item']=str(item.strip())

    def add_unit (self, unit):
        self.ing['unit']=str(unit.strip())

    def add_key (self, key):
        self.ing['key']=str(key.strip())

    def terminate (self):
        debug('Terminate!',0)
        self.terminated = True

    def suspend (self):
        debug('Suspend!',0)
        self.suspended = True

    def resume (self):
        debug('Resume!',0)
        self.suspended = False
