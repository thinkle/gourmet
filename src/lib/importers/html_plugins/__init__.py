# This directory contains data for importing recipes from common
# recipe websites. If the HTML is consistent, we can write add import
# support simply by adding a rules file to this directory.
#
# Creating a rules file will require consistent python syntax, but
# shouldn't require much if any programming knowledge beyond knowledge
# of HTML and regular expressions. Hopefully advanced users can
# contribute new import sites relatively easily.
#
# A basic template contains three variables (one of them optional):
# SUPPORTED_URLS (list of canonical name(s) of target websites),
# SUPPORTED_URL_REGEXPS (optional list of regular expressions that
# match URLs for which we want to use this filter), and RULES (list of
# rules for scraping the website -- the bulk of the work).
#
#
# SUPPORTED_URLS = ['www.mywebsite.com','www.mywebsitesmirror.com']
# SUPPORTED_URLS_REGEXPS = ['.*\.mywebsite\.com']
# 
# RULES = [
#     ['attribute',
#      [PATH_TO_TAG],
#      'text', 'markup' OR 'attname'
#      post_processing # Either a function that returns a string or a dictionary
#                      # Or a tuple (regexp, force_match)
#                      # if force_match, then return "" if there is no match
#                      # else, return the unmodified string if there is no match
#                      # If a function, return a string for most cases. Return a dictionary
#                      # if we're doing ingredient parsing ({'amt':1,'unit':'cup',...})
#                      #
#                      # If a function, we take two args -- value (string or markup) and tag (tag object)
#                      # e.g.
#                      # def post_proc (value, tag): ... return "something"
#
#      ],
#     ...
#    ]
#
# attribute can be: title, servings, image, source, preptime,
# cooktime, instructions, modifications, ingredient_block (string) or ingredient_parsed (dictionary)
#
# attributes can be specified more than once, in which case there will
# be added to. For example, you might want to add various parts of the
# webpage to your instructions.
#
# PATH_TO_TAG is a list of search criteria that zero in on the HTML
# element we want to find, drilling down as necessary (see below)
#
# 'text' or 'markup' specifies whether we want markup when we grab the value
#
# POST_PROCESSING can be a function or a regexp.  If it is a regexp,
# it should have a grouping construct which will contain the text we
# want to keep.
#
# Each instruction in the PATH_TO_TAG is a python dictionary
# containing the following entries
#
# 'regexp': REGEXP a regular expression text search; if this is
#                  specified, anything else is ignored
# 'string': STRING a string text search; if this is specified, 
#                  everything else is ignored
# OR...
#
# 'tag': TAGNAME                  HTML Element Name
# 'attributes':{attname:value}    Attributes on the Element we're looking for
# 'index': INTEGER or [START,END] python index for the count of the tag
#                                 we start counting from 0
#
# EXAMPLES OF RULES
# 
# Here are some examples of how a rule can look.
#
# EXAMPLE 1
#
# Get the 'image' attribute from the IMG tag in the 2nd row of the
# first <table class='recipe'>. (Note: for img, we want the HTML img
# tag with its markup; our importer class will do the right thing and
# grab the image from the src attribute)
#
# <table class='recipe'><tr>...</tr><tr>...<IMG></tr></table>
# 
# ['image',
#  [{'tag':'table',{'class':'recipe'},'index':0},
#   {'tag':'tr','index':1},
#   {'tag':'img','index':0}],
#  'markup']
#
# EXAMPLE 2
#
# Get our "servings" value by searching all the text for the phrase
# "X servings"
#
# ['servings',
#  [{'regexp':'[0-9]+\s+servings?'}],
#  'text',
#  '([0-9]+)\s+servings?'] # our grouping construct will grab just the number.
#
# EXAMPLE 3
#
# Get our instructions from all <p class='body'> elements.
#
# ['instructions',
# [{'tag':'p',
#   'attributes':{'class':'body'},
#   'index':[0,None]
#   }],
# 'text']
#
# For a further sense of how things work, take a look at the actual
# rulesets below.
#
# You can test out rules as you write them by running this file as a
# script directly at a console.

import re
import glob
import os
import sys

from gourmet import convert
from gourmet.OptionParser import options
from gourmet.gglobals import html_plugin_dir
from gourmet.gdebug import debug

my_dir = os.path.split(__file__)[0]
current_dir = os.path.join(os.getcwdu(), "html_plugins")
plugin_directories = [my_dir,html_plugin_dir,current_dir]

SUPPORTED_URLS = {}
SUPPORTED_URLS_REGEXPS = {}

for d in plugin_directories:
    module_names = [os.path.split(m[0:-3])[1] for m in glob.glob(os.path.join(d,'*.py'))]
    if not d in sys.path:
        sys.path.append(d)
    for mod in module_names:
        m = __import__(mod)
        if hasattr(m,'SUPPORTED_URLS') and hasattr(m,'RULES'):
            for u in m.SUPPORTED_URLS:
                SUPPORTED_URLS[u]=m.RULES
            if hasattr(m,'SUPPORTED_URLS_REGEXPS'):
                for r in m.SUPPORTED_URLS_REGEXPS:
                    SUPPORTED_URLS_REGEXPS[r]=m.RULES
        else:
            debug('Ignoring %s: not a set of HTML import rules'%m,0)
            #locals()[mod]=m
        
if __name__ == '__main__':
    keep_going = 1
    while keep_going:
        print 'Testing Interface for Gourmet HTML import.'
        print '------------------------------------------'
        print 'Import supported for: '
        for s in SUPPORTED_URLS.keys():
            print '               ',s
        print '\n'
        url = raw_input('Enter URL to import: ')
        import sys
        sys.path.append(os.path.split(my_dir)[0])
        import html_importer
        print 'Importing URL: ',url
        print 'here we go...'
        d=html_importer.scrape_url(url)
        print d, 'type: ',type(d)
        print '---------------' 
        if (not d) or (not isinstance(d,dict)):
            print 'Failed to import'
            print 'd=',d,'(',type(d),')'
            keep_going=raw_input('import another website? (y or n)')
            if not keep_going or keep_going.lower().strip() in ['no','n','n.']:
                keep_going = False
            break
        for k,v in d.items():
            if k=='image' and v:
                display_image = raw_input('Display image %s? (yes or no):'%v).lower()
                if display_image=='y' or display_image=='yes':
                    ofi = open('/tmp/gourmet_image_test','w')
                    ofi.write(html_importer.get_image_from_tag(v,url))
                    ofi.close()
                    import os
                    os.popen('display /tmp/gourmet_image_test','w')
            else:
                if type(v)==list:
                    print k,':'
                    for i in v: print i                
                else:
                    print k,' :\t',v
        keep_going=raw_input('import another website?')
        if not keep_going or keep_going.lower().strip() in ['no','n','n.']:
            keep_going = False
            
