import gxml_importer, importer, mastercook_importer, mealmaster_importer, mastercook_plaintext_importer
import fnmatch
from gettext import gettext as _
#import mastercook_plaintext_importer
from exporters import MMF,GXML
MC = _('MasterCook file')
MX2 = _('MasterCook XML file')

FILTER_INFO = {
    'mealmaster': {'import': lambda args: [mealmaster_importer.mmf_importer,[],
                                           {'filename':args['file'],
                                            'rd':args['rd'],
                                            'threaded':args['threaded']}],
                   'get_source':'source',
                   'name':MMF,
                   'patterns':['*.mmf','*.txt'],
                   'mimetypes':['text/mealmaster','text/plain'],
                   'tester':importer.Tester("^([M-][M-][M-][M-][M-])-*\s*(Recipe|[Mm]eal-?[Mm]aster).*")},
    'mastercookplain': {'import': lambda args: [mastercook_plaintext_importer.mastercook_importer,
                                               [args['file'],args['rd']],
                                               {'threaded':args['threaded']}],
                        'name': MC,
                        'patterns': ['*.mxp','*.txt','*.mxp'],
                        'mimetypes': ['text/plain'],
                        'tester':mastercook_plaintext_importer.Tester(),
                        'get_source':False,
                        },
    'mastercook': {'import': lambda args: [mastercook_importer.converter,
                                           [args['file'],args['rd']],
                                           {'threaded':args['threaded']}
                                           ],
                   'name':MX2,
                   'patterns': ['*.mx2','*.xml','*.mxp'],
                   'mimetypes': ['application/xml','text/xml','text/plain'],
                   'tester': importer.Tester('.*<mx2[> ]'),
                   'get_source':False,
                   },
    'gxml': {'import': lambda args: [gxml_importer.converter,
                                            [args['file'],args['rd']],
                                            {'threaded':args['threaded']}
                                            ],
             'name':GXML,
             'get_source':False,
             'patterns': ['*.xml','*.gourmet'],
             'mimetypes': ['text/xml','application/xml','text/plain'],
             'tester': importer.Tester('.*<recipeDoc[> ]'),
             'get_source':False,
             },
    }

FILTERS = []
ALL_PATTERNS = []
ALL_MIMES = []
for d in FILTER_INFO.values():
    FILTERS.append([d['name'],d['mimetypes'],d['patterns']])
    ALL_PATTERNS += d['patterns']
    ALL_MIMES += d['mimetypes']

FILTERS = [[_('All importable files'),ALL_MIMES,ALL_PATTERNS]] + FILTERS

def get_filters_by_extension (fn):
    ret = []
    for name,d in FILTER_INFO.items():
        if True in [fnmatch.fnmatch(fn.lower(),p.lower()) for p in d['patterns']]:
            ret.append(name)
    return ret

def select_import_filter (fn):
    start_filters = get_filters_by_extension(fn)
    for f in start_filters:
        if FILTER_INFO[f]['tester'].test(fn):
            return f
    other_filters = filter(lambda n: n not in start_filters,FILTER_INFO.keys())
    for f in other_filters:
        if FILTER_INFO[f]['tester'].test(fn):
            return f
    
