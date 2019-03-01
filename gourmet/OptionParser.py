import argparse
import version

try:
    import argcomplete

    has_argcomplete = True
except ImportError:
    has_argcomplete = False


def parse_options():
    parser = argparse.ArgumentParser(prog='gourmet', description=version.description)
    parser.add_argument('--version', action='version', version=version.version)
    parser.add_argument('--database-url', action='store', dest='db_url',
                        help='Custom url for database of form driver://args/location', default='')
    parser.add_argument('--plugin-directory', action='store', dest='html_plugin_dir',
                        help='Directory for webpage import filter plugins.', default='')
    parser.add_argument('--use-threads', action='store_const', const=True, dest='threads',
                        help='Enable threading support.', default=False)
    parser.add_argument('--disable-threads', action='store_const', const=False, dest='threads',
                        help='Disable threading support.')
    parser.add_argument('--gourmet-directory', action='store', dest='gourmetdir',
                        help='Gourmet configuration directory', default='')
    parser.add_argument('--debug-threading-interval', action='store', type=float, dest='thread_debug_interval',
                        help='Interval for threading debug calls', default=5.0)
    parser.add_argument('--debug-threading', action='store_true', dest='thread_debug',
                        help='Print debugging information about threading.')
    parser.add_argument('--debug-file', action='store', dest='debug_file',
                        help='Regular expression that matches filename(s) containing code for which we want to display debug messages.',
                        default='')
    parser.add_argument('--showtimes', action='store_true', dest='time', help='Print timestamps on debug statements.')
    parser.add_argument('--disable-psyco', dest='psyco', action='store_false', help='Do not use psyco if it is installed.',
                        default=True)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', action='store_const', const=-1, dest='debug', help='Don\'t print gourmet error messages')
    group.add_argument('-v', action='count', dest='debug', help='Be verbose (extra v\'s will increase the verbosity level)')

    if has_argcomplete:
        argcomplete.autocomplete(parser)

    return parser.parse_args()


try:
    args = parse_options()
    print 'args1 = %s' % args
except SystemExit as e:
    import sys

    exc = sys.exc_info()[1]
    if e.code is 0:
        # Normal system exit
        exit(e.code)
    else:
        print "Exception code: ", exc
        argv = str(sys.argv[0])

        if argv == "manage.py":
            print 'Ignore the error message. Launching gourmetweb Django server ...'
            sys.argv = ['gourmet']
            args = parse_options()
        else:
            # unrecognized argument
            exit(e.code)
