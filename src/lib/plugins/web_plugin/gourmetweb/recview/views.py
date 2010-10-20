from gettext import gettext as _
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response
from django.template import Context, loader
import sys
import re
sys.path.append('/usr/share/gourmet/')
import gourmet.backends.db
import gourmet.shopping
from django.utils import simplejson


class MultiplierForm (forms.Form):
    yields = forms.FloatField(label='New Yield',min_value=0,required=False)
    multiplier = forms.FloatField(label='x',min_value=0,required=False)

class NoYieldsMultiplierForm (forms.Form):
    multiplier = forms.FloatField(label='x',min_value=0,required=False)

class SearchForm (forms.Form):
    choices = {unicode(_('anywhere')):'anywhere',
               unicode(_('title')):'title',
               unicode(_('ingredient')):'ingredient',
               unicode(_('instructions')):'instructions',
               unicode(_('notes')):'modifications',
               unicode(_('category')):'category',
               unicode(_('cuisine')):'cuisine',
               unicode(_('source')):'source',}
    search_field = forms.CharField(max_length=100)
    regexp_field = forms.BooleanField(label='Use regexp')
    choice_field = forms.ChoiceField(label='Search in...',
                                     initial='anywhere',
                                     choices=choices.items()
                                     )

rd = gourmet.backends.db.get_database()
slist = gourmet.shopping.ShoppingList()

def list_recs (view, default_search_values={},
               template='index.html'):
    sf = SearchForm()
    for k,v in default_search_values.items():
        print 'Set',k,'to',v
        sf.fields[k].initial = v
    return render_to_response(
        template,
        {'recs':[(rec,rd.get_cats(rec)) for rec in view],
         'form':sf
        }
        )

def index (request):
    return list_recs(rd.fetch_all(rd.recipe_table,deleted=False))

def sort (request, field):
    return list_recs(rd.fetch_all(rd.recipe_table,deleted=False,sort_by=[(field,1)]))

def do_search_xhr (request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        print 'Searching ',form.data['search_field']
        return search(request,form.data['search_field'],template='list.html')
    else:
        print 'Not a post!'


def do_search (request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        print 'Searching ',form.data['search_field']
        return search(request,form.data['search_field'])
    else:
        print 'Not a post!'

def search (request, term, template='index.html'):
    vw = rd.search_recipes(
        [{'column':'deleted','operator':'=','search':False},
         {'column':'anywhere',
          'operator':'LIKE',
          'search':'%'+term.replace('%','%%'+'%')+'%',
          }
         ]
        )
    print 'We got ',len(vw),'for "%s"'%term
    return list_recs(vw, default_search_values={
        'search_field':term,
        'regexp_field':False,
        'choice_field':'anywhere',
        },
                     template=template
                     )


def get_ings (rec_id, mult):
    ings = rd.order_ings(rd.get_ings(rec_id))
    formatted_ings = []
    for g,items in ings:
        formatted_items = []
        for item in items:
            strings = []
            amt,unit = rd.get_amount_and_unit(item,mult=mult)
            if amt: strings.append(amt)
            if unit: strings.append(unit)
            strings.append(item.item)
            if item.optional: strings.append(' (optional)')
            formatted_items.append(' '.join(strings))
        formatted_ings.append((g,formatted_items))
    return formatted_ings

def rec (request, rec_id, mult=1):
    mult = float(mult)
    rec = rd.get_rec(rec_id)
    formatted_ings = get_ings(rec_id,mult)
    def textify (t):
        if not t: return ''
        print 'textifying "%s"'%t
        return re.sub('\n','<br>',
                      re.sub('\n\n+','</p><p>','<p>%s</p>'%t.strip()))
    if rec.yields:
        mf = MultiplierForm()
    else:
        mf = NoYieldsMultiplierForm()
    return render_to_response(
        'rec.html',
        {'rd':rd,
         'r':rec,
         'ings':formatted_ings,
         'cats':', '.join(rd.get_cats(rec)),
         'instructions':textify(rec.instructions),
         'notes':textify(rec.modifications),
         'mult':mult,
         'yields':(rec.yields and rec.yields * mult or None),
         'is_adjusted': (mult!=1),
         'multiplier_form':mf,
         }
        )

def multiply_rec_xhr (request):
    return multiply_rec(request,xhr=True)

def multiply_rec (request, xhr=None):
    if request.method == 'POST':
        form = MultiplierForm(request.POST)
        if form.is_valid():
            multiplier = form.cleaned_data['multiplier']
            recid = request.POST.get('rid',None)
            if not multiplier:
                yields = form.cleaned_data['yields']
                if yields:
                    orig_yields = rd.get_rec(recid).yields
                    multiplier = (yields / float(orig_yields))
                else:
                    multiplier = 1
            if xhr:
                rec = rd.get_rec(recid)
                d = {'yields':rec.yields * multiplier,
                     'ingredients':get_ings(recid,multiplier),
                     'multiplier':multiplier}
                return HttpResponse(
                    simplejson.dumps(d),
                    mimetype='application/javascript'
                    )
            else:
                return HttpResponseRedirect('/rec/%s/%s'%(recid,multiplier))

        
def shop (request, rec_id=None, mult=1):
    mult = float(mult)
    if rec_id is not None:
        slist.addRec(rd.get_rec(rec_id),mult)
    recs = slist.recs.values()
    data,pantry = slist.organize_list(slist.lst)
    #recs = [('foo',4),]
    #data = [('sugar','3 cups'),]
    #pantry = [('sugar','3 cups'),]    
    return render_to_response('shop.html',{'data':data,'pantry':pantry,
                                           'recs':recs})

def shop_remove (request, rec_id=None):
    try:
        rec_id = int(rec_id)
        if slist.recs.has_key(rec_id):
            del slist.recs[int(rec_id)]
        else:
            print 'Odd, there is no ',rec_id,'on the shopping list'
    except TypeError:
        print 'Odd, rec_id',rec_id,'is the wrong type'
        raise
    return shop(request)
        
def thumb (request, rec_id):
    return HttpResponse(rd.get_rec(rec_id).thumb,
                        mimetype='image/jpeg'
                        )

def img (request, rec_id):
    return HttpResponse(rd.get_rec(rec_id).image,
                        mimetype='image/jpeg'
                        )
