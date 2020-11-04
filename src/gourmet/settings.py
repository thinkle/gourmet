import os.path as op
import sys

# The following lines are modified at installation time by setup.py so they
# point to the actual data files installation paths.

base_dir = op.abspath(op.join(op.dirname(__file__), '..'))
locale_base = op.join(base_dir, 'build', 'mo')

# Apologies for the formatting -- something in the build process is
# getting rid of indentations in this file which throws a syntax error
# on install
if getattr(sys, 'frozen', False): base_dir = op.dirname(sys.executable); data_dir = base_dir; ui_base = op.join(base_dir, 'ui'); doc_base = op.join(base_dir, 'doc'); locale_base = op.join(base_dir, 'locale'); plugin_base = op.join(base_dir)
