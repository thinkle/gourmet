import os.path

try:
    import bin._preamble
    base = bin._preamble.get_path()
    locale_base = os.path.join(base, 'po')
except ImportError:
    import sys
    sys.exc_clear()

    # GRAB EXPLICITLY STATED GOURMET BASE DIRECTORY FROM OPTIONS
    from OptionParser import options
    if options.gourmet_base:
        base=options.gourmet_base
        locale_base = os.path.split(base)[0]
    else:
        base=os.path.join(sys.prefix,'share','gourmet')
        locale_base = os.path.join(sys.prefix,'share','locale')
