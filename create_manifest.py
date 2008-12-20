import os, os.path, glob

def recursive_match (base, patterns, seed=[]): 
    for pattern in patterns:
        seed.extend(glob.glob(os.path.join(base,pattern)))
    for subdir in glob.glob(os.path.join(base,'*/')):
        recursive_match(subdir,patterns,seed)
    return seed

outfi = open('MANIFEST','w')

def write_lst_to_file (lst, fi=outfi):
    lst = list(set(lst))
    lst.sort()
    for itm in lst:
        print 'Write:',itm
        if itm.strip():
            fi.write(itm.strip()+'\n')

STARTER_LIST ='''ChangeLog
CHANGES
FAQ
MANIFEST
README
README.txt
TODO
TESTS
copyright
setup.cfg
setup.py
''' 
# A hack because MANIFEST.in isn't working right... grrr...

lst = STARTER_LIST.split('\n')
lst.extend(['src/gourmet','src/gourmet_in_place'])
recursive_match('data',['*.txt','*.wav','*.css'],lst)
lst.extend(['data/FAQ'])
recursive_match('src/lib',['*.py'],lst)
recursive_match('glade',['*.glade'],lst)
recursive_match('src/lib/plugins/',['*.glade',
                                    '*.gourmet-plugin',
                                    '*.gourmet-plugin.in'],
                lst)
recursive_match('images/',['*.png'],lst)
recursive_match('',['*.desktop.in'],lst)
recursive_match('i18n',['NOTE_TO_TRANSLATORS','*.in','*.pot','*.po','*.mo'],lst)
recursive_match('documentation',['*.xml','*.png'],lst)
recursive_match('windows',['*.pyw'],lst)
recursive_match('tools',['*.py'],lst)
write_lst_to_file(lst)
