#!/usr/bin/python
import os,os.path,shutil,glob,string

class RPMBuilder:
    """A class to build RPMs for various distributions. This class
    allows us to setup a setup.cfg file with a commented sections per
    distribution, and then to automatically run setup.py bdist_rpm with
    a set of different options.

    The setup.cfg file has marked commented sections (marked with
    START and END) which contain the options for each distribution
    (usually distribution-name and requires, but anything is possible).
    This script will move setup.cfg out of the way (to setup.cfg.base),
    create a set of new setup.cfgs in series and run setup.py with them.

    Is this backasswards? yes.
    Should we do this from within python/distutils? yes.
    Does this work as written? yes. And that's good enough for now :)"""
    
    START = "# START"
    END = "# END"
    STRIP_ME = "# "
    SUFFIX = "# SUFFIX "
    BACKUP_FILE = "setup.cfg.base"

    def __init__ (self, filename='setup.cfg'):
        self.read_setup(filename)

    def read_setup (self, filename='setup.cfg'):
        self.filename = filename
        self.dists = {}
        self.suffixes = {}
        self.before_options = []
        self.after_options = []
        ifi = open(filename,'r')
        backupfi = open('setup.cfg.base','w')
        self.option = None
        self.before = True
        for l in ifi.readlines():
            backupfi.write(l)
            if l.find(self.START)==0:
                self.option = l[len(self.START):]
                self.dists[self.option]=[] #empty list, for lines we're including
            elif l.find(self.END)==0:
                self.option = None
                self.before = False
            elif self.option:
                if l.find(self.SUFFIX)==0:
                    self.suffixes[self.option]=l[len(self.SUFFIX):].strip()
                elif self.option and l.find(self.STRIP_ME)==0:
                    self.dists[self.option].append(l[len(self.STRIP_ME):])
                else:
                    raise SyntaxError("Line in marked section doesn't start with \"%s\": %s"%(self.STRIP_ME,l))
            elif self.before: self.before_options.append(l)
            else: self.after_options.append(l)
        ifi.close()
        backupfi.close()

    def write_setup (self, dist):
        ofi=open(self.filename,'w')
        for l in self.before_options: ofi.write(l)
        for l in self.dists[dist]: ofi.write(l)
        for l in self.after_options: ofi.write(l)

    def build_rpms (self):
        built = []
        for name in self.dists.keys():
            print 'Writing new setup.cfg for ',name
            self.write_setup(name)
            print 'Setup written.'
            print 'Building RPM ',name
            os.system('python setup.py bdist_rpm >> /tmp/GOURMET_RPM_LOG')
            print 'Done building! Renaming RPM files with suffix %s'%self.suffixes[name]
            files = glob.glob('dist/*noarch.rpm')
            files += glob.glob('dist/*src.rpm')
            for f in files:
                # if this isn't one of our renamed files...
                if f not in built:
                    # assume we just built it and rename it
                    fn,ext=os.path.splitext(f)
                    fn,ext2=os.path.splitext(fn)
                    ext3=self.suffixes[name]
                    newname = string.join([fn,ext3.strip('.'),ext2.strip('.'),ext.strip('.')],os.path.extsep)
                    shutil.move(f,newname)
                    # add to our list of renamed files
                    built.append(newname)
                    print 'build = '
            print 'Done!'
            
    def cleanup (self):
        shutil.move(self.BACKUP_FILE,self.filename)
        
                
                
if __name__ == '__main__':
    rpb = RPMBuilder()
    #rpb.write_setup(rpb.dists.keys()[0])
    rpb.build_rpms()
    print 'Cleaning up...'
    rpb.cleanup()
    print "DONE!"
