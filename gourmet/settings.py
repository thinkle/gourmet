import os.path
import sys

# The following lines are modified at installation time by setup.py so they
# point to the actual data files installation paths.

base_dir = '..'
lib_dir = '../gourmet'
data_dir = os.path.join(base_dir, "gourmet", "data")
ui_base = os.path.join(base_dir, 'gourmet', 'ui')
doc_base = os.path.join(base_dir, "gourmet")
locale_base = os.path.join(base_dir, "gourmet", "build", "mo")
plugin_base = os.path.join(base_dir, "gourmet", "build", "share", "gourmet")
icon_base = os.path.join(data_dir, "icons")

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    data_dir = base_dir
    ui_base = os.path.join(base_dir, 'ui')
    doc_base = os.path.join(base_dir, 'doc')
    locale_base = os.path.join(base_dir, "locale")
    plugin_base = os.path.join(base_dir)
