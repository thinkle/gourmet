import glob, os, sys, tempfile
tf = tempfile.TemporaryFile()
#sys.stdout = tf
#def get_error_message ():
#    tf.seek(0)
#    ret =  tf.read()
#    tf.flush()
#    return ret

#errors = {}

errors = []
success = []

for fi in glob.glob("*.po"):
    lang = fi[0:-3]
    #sys.stderr.write('Format %s\n'%lang)
    if not os.path.exists(os.path.join(lang,'LC_MESSAGES')):
        os.makedirs(os.path.join(lang,'LC_MESSAGES'))
    ret = os.spawnl(os.P_WAIT,'/usr/bin/msgfmt','-o %s/LC_MESSAGES/gourmet.mo'%lang,'%s.po'%lang)
    if ret != 0:
        errors.append(lang)
    else:
        success.append(lang)

if not errors: print 'All languages generated successfully!'
else:
    print 'Successful:',success
    print 'Failed:',errors
    
        
