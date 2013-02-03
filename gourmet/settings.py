import os.path

# The following lines are modified at installation time by setup.py so they
# point to the actual data files installation paths.
base_dir = '..'
data_dir = os.path.join(base_dir, "gourmet", "data")
doc_base = os.path.join(base_dir, "gourmet")
icon_base = os.path.join(data_dir, "icons")
locale_base = os.path.join(base_dir, "gourmet", "build", "mo")
plugin_base = os.path.join(base_dir, "gourmet", "build", "gourmet")

