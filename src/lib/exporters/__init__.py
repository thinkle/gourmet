import exporter, gxml_exporter, gxml2_exporter
import html_exporter, mealmaster_exporter, recipe_emailer
import pdf_exporter
#import eatdrinkfeelgood_exporter
import recipe_emailer
import printer
from gettext import gettext as _
from gourmet.gdebug import *

try:
    import rtf_exporter
    rtf = True
except ImportError:
    debug('No RTF support',0)
    rtf = False

# Filetypes as presented to user
WEBPAGE = _('HTML Web Page')
MMF = _('MealMaster file')
TXT = _('Plain Text')
RTF = _('RTF')
PDF = _('PDF (Portable Document Format)')
GXML2 = _('Gourmet XML File')
GXML = _('Gourmet XML File (Obsolete, < v.0.8.2)')
EDFG = _('Eat Drink Feel Good XML File')

# Our list of filename (for user), mimetype, extensions
# for each file we can save
saveas_filters = [
    [WEBPAGE,['text/html'],['']],
    [MMF,['text/mmf'],['*.mmf','*.MMF']],
    [TXT,['text/plain'],['*.txt','*.TXT']],      
    [GXML2,['text/xml'],['*.grmt','*.xml','*.XML']],
    [PDF,['application/pdf'],['*.pdf']],
    #[EDFG,['text/xml'],['*.xml','*.XML']],
    #[GXML,['text/xml'],['*.xml','*.XML']],
    ]

saveas_single_filters = [
    [WEBPAGE,['text/html'],['*.html','*.htm','*.HTM','*.HTML']],
    [MMF,['text/mmf'],['*.mmf','*.MMF']],
    [TXT,['text/plain'],['*.txt','*.TXT']],      
    #[GXML,['text/xml'],['*.xml','*.XML']],
    [GXML2,['text/xml'],['*.grmt','*.xml','*.XML']],
    [PDF,['application/pdf'],['*.pdf']],    
    #[EDFG,['text/xml'],['*.xml','*.XML']],
    ]

# Add RTF to our files if it's supported
if rtf:
    saveas_filters.append([RTF,['application/rtf','text/rtf'],['*.rtf','*.RTF']]),
    saveas_single_filters.append([RTF,['application/rtf','text/rtf'],['*.rtf','*.RTF']]),

# Our dictionary (keyed by filetype description string) of exporters.
# This works pretty magically: 'mult_exporter' and 'exporter' keys are lambdas
# that take a dictionary of standard arguments which we can use as we like
# {'rd':recipe_database,'rv':recipe_view,'file':outfile,'conv':converter_instance,
#  'prog':progress_displaying_function,'rec':individual_recipe_to_export,...}
exporter_dict = {
    WEBPAGE : {'mult_exporter': lambda args : html_exporter.website_exporter(
        args['rd'], 
        args['rv'],
        args['file'],
        args['conv'],
        progress_func=args['prog']),
        'exporter': lambda args : html_exporter.html_exporter(
        args['rd'],
        args['rec'],
        args['out'],
        change_units=args['change_units'],
        mult=args['mult'],
        conv=args['conv']),
        'label':_('Exporting Webpage'),
        'sublabel':_('Exporting recipes to HTML files in directory %(file)s'),
        'single_completed':_('Recipe saved as HTML file %(file)s'),
        },
    MMF : {'mult_exporter':lambda args : exporter.ExporterMultirec(
        args['rd'],
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
        mult=args['mult'],
        change_units=args['change_units'],
        conv=args['conv']),
        'label':_('MealMaster Export'),
        'sublabel':_('Exporting recipes to MealMaster file %(file)s.'),
        'single_completed':_('Recipe saved as MealMaster file %(file)s'),
           },
    TXT : {'mult_exporter':lambda args: exporter.ExporterMultirec(
         args['rd'],args['rv'],args['file'],
         conv=args['conv'],
         progress_func=args['prog']),
         'exporter':lambda args: exporter.exporter_mult(args['rd'],
         args['rec'],
         args['out'],
         mult=args['mult'],
         change_units=args['change_units'],
         conv=args['conv']),
         'label':_('Text Export'),
         'sublabel':_('Exporting recipes to Plain Text file %(file)s.'),
         'single_completed':_('Recipe saved as Plain Text file %(file)s'),
         },
    GXML2 : {'mult_exporter':lambda args: gxml2_exporter.rview_to_xml(
         args['rd'],
         args['rv'],
         args['file'],
         progress_func=args['prog']),
         'exporter': lambda args: gxml2_exporter.rview_to_xml(args['rd'],
         [args['rec']],
         args['out'],
         change_units=args['change_units'],
         mult=args['mult']
         ).run(),
         'label':_('Gourmet XML Export'),
         'sublabel':_('Exporting recipes to Gourmet XML file %(file)s.'),
         'single_completed':_('Recipe saved in Gourmet XML file %(file)s.'),
         },
#     GXML : {'mult_exporter':lambda args: gxml_exporter.rview_to_xml(args['rd'],
#                                                                     args['rv'],
#                                                                     args['file'],
#                                                                     progress_func=args['prog']),
#             'exporter': lambda args: gxml_exporter.rview_to_xml(args['rd'],
#                                                                 [args['rec']],
#                                                                 args['out'],
#                                                                 ).run(),
#             'label':_('XML Export'),
#             'sublabel':_('Exporting recipes to Gourmet XML (<0.8.2) file %(file)s.'),
#             'single_completed':_('Recipe saved in Gourmet XML (<0.8.2) file %(file)s.'),
#             },
    RTF : {'mult_exporter':lambda args : rtf_exporter.rtf_exporter_multidoc(args['rd'],
                                                                            args['rv'],
                                                                            args['file'],
                                                                            progress_func=args['prog']),
           'exporter': lambda args: rtf_exporter.rtf_exporter(args['rd'],
                                                              args['rec'],
                                                              args['out'],
                                                              change_units=args['change_units'],
                                                              mult=args['mult']),
           'label':_('RTF Export'),
           'sublabel':_('Exporting recipes to Rich Text file %(file)s.'),
           'single_completed':_('Recipe saved as Rich Text file %(file)s'),
           },
    PDF : {'mult_exporter':lambda args: pdf_exporter.PdfExporterMultiDoc(args['rd'],
                                                                         args['rv'],
                                                                         args['file'],
                                                                         progress_func=args['prog'],
                                                                         ),
           'exporter':lambda args: pdf_exporter.PdfExporter(args['rd'],
                                                            args['rec'],
                                                            args['out'],
                                                            change_units=args['change_units'],
                                                            mult=args['mult']),
           'label':_('PDF Export'),
           'sublabel':_('Exporting recipes to PDF %(file)s.'),
           'single_completed':_('Recipe saved as PDF %(file)s'),
           },
    
    # EDFG : {'mult_exporter': lambda args : eatdrinkfeelgood_exporter.EdfgXmlM(
#         args['rd'], 
#         args['rv'],
#         args['file'],
#         args['conv'],
#         progress_func=None),
#         'exporter': lambda args : eatdrinkfeelgood_exporter.EdfgXml(
#         args['rd'],
#         args['rec'],
#         args['out'],
#         change_units=args['change_units'],
#         mult=args['mult'],
#         conv=args['conv']),
#         'label':_('Exporting Eat Drink Feel Good Format'),
#         'sublabel':_('Exporting recipes to EDFG in directory %(file)s'),
#         'single_completed':_('Recipe saved as EDFG file %(file)s'),
#         },
    }

class Tester:
    def __init__ (self):
        import gourmet.recipeManager, gourmet.convert
        self.rm = gourmet.recipeManager.RecipeManager(**gourmet.recipeManager.dbargs)
        self.conv = gourmet.convert.converter()

    def interactive_test (self):
        self.run_export(**self.get_choice())

    def get_choice (self):
        print 'We can export: '
        for n,f in enumerate(saveas_filters):
            print n,'. ',f
        n = raw_input('Choose format: ')
        while type(n)==str or n < 0 or n > len(saveas_filters):
            try:
                n=int(n)
            except:
                n = raw_input('Choose format (enter number of a choice please!): ')
        format=saveas_filters[n][0]
        fn = raw_input('Export %s to file: '%format)
        if raw_input('Multiple recipes? y or n [n]: ')=='y':
            mode='mult_exporter'
            out=None
        else:
            mode='exporter'
            out = open(fn,'wb')
        return {'file':fn,
                'format':format,
                'out':out,
                'mode':mode,
                }

    def run_export (self, **args):
        defaults = {'rd':self.rm,
                    'mult':1,
                    'rec':self.rm.rview.select(deleted=False)[0],
                    'rv':self.rm.rview.select(deleted=False),
                    'change_units':True,
                    'conv':self.conv,
                    'format': TXT,
                    'mode':'exporter',
                    'out':None
                    }
        for k,v in args.items(): defaults[k]=v
        exporter = exporter_dict[defaults['format']][defaults['mode']]
        print 'Running exporter ',exporter, defaults['format'], defaults['mode'], defaults['rec'].title, 
        e=exporter(defaults)
        if hasattr(e,'run'): e.run()
        if defaults['out']:
            defaults['out'].close()
            print 'Closed file'

if __name__ == '__main__':
    t=Tester()
    t.interactive_test()

            
            
            
            
            
                
