import glob, os
for fi in glob.glob("*.po"):
    lang = fi[0:-3]
    print 'executing: make_mo.sh ',lang
    ifi=os.popen('./make_mo.sh %s'%lang,'r')
    print '%s Done!'%ifi.read()
