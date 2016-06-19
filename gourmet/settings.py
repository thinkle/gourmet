from __future__ import print_function

import os.path
import sys

# The following lines are modified at installation time by setup.py so they
# point to the actual data files installation paths.

lib_dir = os.path.join(os.path.dirname(__file__),'../gourmet')
base_dir = os.path.join(os.path.dirname(__file__),'..')
data_dir = os.path.join(base_dir, "data")
ui_base = os.path.join(data_dir, 'ui')
doc_base = os.path.join(base_dir, "gourmet")
locale_base = os.path.join(base_dir, "build", "mo")
plugin_base = os.path.join(base_dir, "build", "share", "gourmet")

# Apologies for the formatting -- something in the build process is
# getting rid of indentations in this file which throws a syntax error
# on install
if getattr(sys, 'frozen', False): base_dir = os.path.dirname(sys.executable); data_dir = base_dir; ui_base = os.path.join(base_dir, 'ui'); doc_base = os.path.join(base_dir, 'doc');locale_base = os.path.join(base_dir, "locale"); plugin_base = os.path.join(base_dir)
    
icon_base = os.path.join(data_dir, "icons")
