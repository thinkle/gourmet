import exporter, gxml_exporter, html_exporter, mealmaster_exporter, recipe_emailer
import recipe_emailer
import printer
from gettext import gettext as _
from gourmet.gdebug import *

try:
    import rtf_exporter
    rtf = True
except:
    debug('No RTF support',0)
    rtf = False

#WEBPAGE = _('HTML Web Page (Creates a new Folder)')
WEBPAGE = _('HTML Web Page')
MMF = _('Mealmaster file')
TXT = _('Plain Text')
RTF = _('RTF')
GXML = _('Gourmet XML File')

saveas_filters = [
    [WEBPAGE,['text/html'],['']],
    [MMF,['text/mmf'],['*.mmf','*.MMF']],
    [TXT,['text/plain'],['*.txt','*.TXT']],      
    [GXML,['text/xml'],['*.xml','*.XML']]
    ]

saveas_single_filters = [
    [WEBPAGE,['text/html'],['*.html','*.htm','*.HTM','*.HTML']],
    [MMF,['text/mmf'],['*.mmf','*.MMF']],
    [TXT,['text/plain'],['*.txt','*.TXT']],      
    [GXML,['text/xml'],['*.xml','*.XML']]
    ]

if rtf:
    saveas_filters.append([RTF,['application/rtf','text/rtf'],['*.rtf','*.RTF']]),
    saveas_single_filters.append([RTF,['application/rtf','text/rtf'],['*.rtf','*.RTF']]),

exporter_dict = {
    WEBPAGE : {'mult_exporter': lambda args : html_exporter.website_exporter(args['rd'], args['rv'],
                                                                             args['file'], args['conv'],
                                                                             progress_func=args['prog']),
               'exporter': lambda args : exporter.html_exporter(args['rd'],args['rec'],args['out'],conv=args['conv']),
               'label':_('Exporting Webpage'),
               'sublabel':_('Exporting recipes to HTML files in directory %(file)s'),
               'single_completed':_('Recipe saved as HTML file %(file)s'),
               },
    MMF : {'mult_exporter':lambda args : exporter.ExporterMultirec(args['rd'],
                                                                   args['rv'],
                                                                   args['file'],
                                                                   one_file=True,
                                                                   ext='mmf',
                                                                   conv=args['conv'],
                                                                   progress_func=args['prog'],
                                                                   exporter=mealmaster_exporter.mealmaster_exporter),
           'exporter': lambda args: mealmaster_exporter.mealmaster_exporter(args['rd'],
                                                                 args['rec'],
                                                                 args['out'],
                                                                 conv=args['conv']),
           'label':_('Mealmaster Export'),
           'sublabel':_('Exporting recipes to MealMaster(tm) file %(file)s.'),
           'single_completed':_('Recipe saved as Mealmaster file %(file)s'),
           },
    TXT : {'mult_exporter':lambda args: exporter.ExporterMultirec(args['rd'],args['rv'],args['file'],
                                                              conv=args['conv'], progress_func=args['prog']),
           'exporter':lambda args: exporter.exporter(args['rd'],
                                                 args['rec'],
                                                 args['out'],
                                                 conv=args['conv']),
           'label':_('Text Export'),
           'sublabel':_('Exporting recipes to Plain Text file %(file)s.'),
           'single_completed':_('Recipe saved as Plain Text file %(file)s'),
           },
    GXML : {'mult_exporter':lambda args: gxml_exporter.rview_to_xml(args['rd'],
                                                                    args['rv'],
                                                                    args['file'],
                                                                    progress_func=args['prog']),
            'exporter': lambda args: gxml_exporter.rview_to_xml(args['rd'],
                                                                [args['rec']],
                                                                args['out'],
                                                                ),
            'label':_('XML Export'),
            'sublabel':_('Exporting recipes to Gourmet XML file %(file)s.'),
            'single_completed':_('Recipe saved in Gourmet XML file %(file)s.'),
            },
    }
