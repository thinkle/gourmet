#!/usr/bin/python
import gtk # only needed for threading voodoo
import rmetakit, keymanager, convert, time
from gdebug import debug, TimeAction, print_timer_info
from gglobals import gt, use_threads
import os,stat,re

class importer:
    def __init__ (self, rd, threaded=False):
        timeaction = TimeAction('importer.__init__',10)
        self.rd=rd
        self.rd_orig_ing_hooks = self.rd.add_ing_hooks
        self.added_recs=[]
        self.added_ings=[]
        #self.rd_orig_hooks = self.rd.add_hooks
        self.rd.add_ing_hooks = []
        #self.rd.add_hooks = []
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
        timeaction.end()
    # end __init__

    def run (self):
        debug('Running ing hooks',0)
        for i in self.added_ings:
            for h in self.rd_orig_ing_hooks:
                h(i)
        #debug('Running rec hooks',0)                
        #for r in self._added_recs:
        #    for h in self.rd_orig_hooks:
        #        h(r)
        self.rd.add_ing_hooks = self.rd_orig_ing_hooks
        #self.rd.add_hooks = self.rd_orig_hooks
        print_timer_info()

    def check_for_sleep (self):
        timeaction = TimeAction('importer.check_for_sleep',10)
        gt.gtk_update()
        if self.terminated:
            raise "Importer Terminated!"
        while self.suspended:
            gt.gtk_update()
            if self.terminated:
                raise "Importer Terminated!"
            if not use_threads:
                # we only sleep a little while if we're suspended!
                time.sleep(0.1)
            else:
                time.sleep(1)
        timeaction.end()

    def start_rec (self, dict=None, base="import"):
        self.rec_timer = TimeAction('importer RECIPE IMPORT',10)
        timeaction = TimeAction('importer.start_rec',10)
        self.check_for_sleep()
        self.added_ings=[]
        self.group = None
        if dict:
            self.rec=dict
        else:
            self.rec = {}
        if not self.rec.has_key('id'):
            self.rec['id']=self.rd.new_id(base)
        debug('New Import\'s ID=%s'%self.rec['id'],0)
        timeaction.end()

    def commit_rec (self):
        timeaction = TimeAction('importer.commit_rec',10)
        if self.rec.has_key('servings'):
            self.rec['servings']=str(self.convert_servings(self.rec['servings']))
        for k,v in self.rec.items():
            try:
                self.rec[k]=v.strip()
            except:
                pass
        tt=TimeAction('importer.commit_rec - rd.add_rec',5)
        debug('commiting recipe %s'%self.rec,0)
        r = self.rd.add_rec(self.rec)
        tt.end()
        self.added_recs.append(r)
        self.check_for_sleep()
        timeaction.end()
        self.rec_timer.end()

    def convert_servings (self, str):
        timeaction = TimeAction('importer.convert_servings',10)
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
        timeaction.end()
            
    def start_ing (self, **kwargs):
        timeaction = TimeAction('importer.start_ing',10)
        gt.gtk_update()
        self.ing=kwargs
        self.ing['id']=self.rec['id']
        debug('ing ID %s, recipe ID %s'%(self.ing['id'],self.rec['id']),0)
        timeaction.end()
                 
    def commit_ing (self):
        timeaction = TimeAction('importer.commit_ing 1',10)
        if not ((self.ing.has_key('refid') and self.ing['refid']) or (self.ing.has_key('ingkey') and self.ing['ingkey'])):
            #self.ing['ingkey']=self.km.get_key(self.ing['item'],0.9)
            self.ing['ingkey']=self.km.get_key_fast(self.ing['item'])
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 2',10)
        if not (self.ing.has_key('position') and self.ing['position']):
            self.ing['position']=self.position
            self.position+=1
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 3',10)
        if self.group:
            self.ing['inggroup']=self.group
        timeaction.end()
        timeaction = TimeAction('importer.commit_ing 4',10)
        self.added_ings.append(self.rd.add_ing(self.ing))
        timeaction.end()
        

    def add_amt (self, amount):
        timeaction = TimeAction('importer.add_amt',10)
        """We should NEVER get non-numeric amounts.
        Amounts must contain [/.0-9 ] e.g. 1.2 or 1 1/5
        or 1/3 etc."""
        gt.gtk_update()
        try:
            self.ing['amount']=convert.frac_to_float(amount)
        except:
            self.ing['amount']=float(amount)
        timeaction.end()

    def add_ref (self, id):
        timeaction = TimeAction('importer.add_ref',10)
        self.ing['refid']=id
        self.ing['unit']='recipe'
        timeaction.end()

    def add_item (self, item):
        timeaction = TimeAction('importer.add_item',10)        
        itm=str(item.strip())
        itm=itm.replace("\n"," ")
        self.ing['item']=itm
        timeaction.end()
        
    def add_unit (self, unit):
        timeaction = TimeAction('importer.add_unit',10)
        self.ing['unit']=str(unit.strip())
        timeaction.end()

    def add_key (self, key):
        timeaction = TimeAction('importer.add_key',10)
        self.ing['ingkey']=str(key.strip())
        timeaction.end()

    def terminate (self):
        timeaction = TimeAction('importer.terminate',10)
        debug('Terminate!',0)
        self.terminated = True
        timeaction.end()

    def suspend (self):
        timeaction = TimeAction('importer.suspend',10)
        debug('Suspend!',0)
        self.suspended = True
        timeaction.end()
        print_timer_info()

    def resume (self):
        debug('Resume!',0)
        self.suspended = False

class MultipleImporter:
    def __init__ (self,grm,imports):
        """GRM is a GourmetRecipeManager instance.
        Imports is a list of classes to run and filenames."""
        self.imports = imports
        self.grm = grm
        self.total_size = 0
        self.current_prog = 0
        self.sizes = {}
        self.completed_imports = 0
        self.current_imports = 0
        self.completed_imports_last_fn = ""
        self.num_matcher = re.compile('([0-9]+)')
        for c,fn in imports:
            size = os.stat(fn)[stat.ST_SIZE]
            self.total_size += size
            self.sizes[fn]=size

    def run (self):
        for importer,fn in self.imports:
            ic,args,kwargs = importer
            self.fn = fn
            self.current_percentage = float(self.sizes[fn])/self.total_size
            gt.gtk_enter()
            self.grm.prog_dialog.detail_label.set_text(_('<i>Importing %s</i>')%fn)
            self.grm.prog_dialog.detail_label.set_use_markup(True)
            #self.grm.prog_dialog.label.set_text(_('<i>Importing %s</i>')%fn)
            gt.gtk_leave()
            kwargs['progress']=self.show_progress
            self.iclass = ic(*args,**kwargs)
            self.suspend = self.iclass.suspend
            self.terminate = self.iclass.terminate
            self.resume = self.iclass.resume
            self.iclass.run()
            #print self.current_prog, '+', self.current_percentage
            self.current_prog += self.current_percentage
        self.grm.set_progress_thr(1,'Import complete!')
    
    def show_progress (self, prog, msg):
        if len(self.imports)>1:
            # we muck about with the messages if we have more than one...            
            m=self.num_matcher.search(msg)
            if not m: msg=""
            else:
                if self.fn != self.completed_imports_last_fn:
                    self.completed_imports_last_fn = self.fn
                    self.completed_imports += self.current_imports
                self.current_imports=int(m.groups()[0])
                total = self.current_imports + self.completed_imports
                if self.completed_imports:
                    msg = _("Imported %(number)s recipes from %(file)s (%(total)s total)")%{'number':self.current_imports,
                                                                                            'total':total,
                                                                                            'file':os.path.split(self.fn)[1]
                                                                                            }
        self.grm.set_progress_thr(self.current_prog + (prog * self.current_percentage),
                                  msg)
        
        
    
            
    
