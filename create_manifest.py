import os, os.path, glob

def recursive_match (base, patterns, seed=[]): 
    for pattern in patterns:
        seed.extend(glob.glob(os.path.join(base,pattern)))
    for subdir in glob.glob(os.path.join(base,'*/')):
        recursive_match(subdir,patterns,seed)
    return seed

outfi = open('MANIFEST','w')

def write_lst_to_file (lst, fi=outfi):
    for itm in lst:
        fi.write(itm.strip()+'\n')

STARTER_LIST ='''CHANGES
FAQ
MANIFEST
README
README.txt
TODO
copyright
setup.cfg
setup.py
''' 
# A hack because MANIFEST.in isn't working right... grrr...

outfi.write(STARTER_LIST)
write_lst_to_file(['src/gourmet','src/gourmet_in_place'])
write_lst_to_file(recursive_match('data',['*.txt','*.wav','*.css']))
write_lst_to_file(['data/FAQ'])
write_lst_to_file(recursive_match('src/lib',['*.py']))
write_lst_to_file(recursive_match('glade',['*.glade']))
write_lst_to_file(recursive_match('src/lib/plugins/',['*.glade',
                                                      '*.gourmet-plugin',
                                                      '*.gourmet-plugin.in']
                                  ))
write_lst_to_file(recursive_match('images/',['*.png']))
write_lst_to_file(recursive_match('',['*.desktop.in']))
write_lst_to_file(recursive_match('i18n',['NOTE_TO_TRANSLATORS','*.in','*.pot','*.po','*.mo']))
write_lst_to_file(recursive_match('documentation',['*.xml','*.png']))
write_lst_to_file(recursive_match('windows',['*.pyw']))
write_lst_to_file(recursive_match('tools',['*.py']))



