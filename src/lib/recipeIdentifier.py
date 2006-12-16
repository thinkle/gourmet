import convert, xml.sax.saxutils
import md5, difflib, types
from gettext import gettext as _
from gglobals import REC_ATTRS,TEXT_ATTR_DIC,INT_REC_ATTRS

IMAGE_ATTRS = ['image','thumb']
ALL_ATTRS = [r[0] for r in REC_ATTRS] + TEXT_ATTR_DIC.keys() + IMAGE_ATTRS
REC_FIELDS = ['title',
              'instructions',
              ]
ING_FIELDS = ['amount','unit']

STANDARD_UNITS = ['g.','ml.']


# Hash stuff.

def standardize_ingredient (ing_object, converter):
    if ing_object.item:
        ing = ing_object.item
    else:
        ing = ing_object.ingkey
    unit,amount = ing_object.unit,ing_object.amount
    gconv = converter.converter(unit,'g.')
    vconv = converter.converter(unit,'ml.')
    if not (gconv or vconv):
        gconv = converter.converter(unit,'g.',ing)
        vconv = converter.converter(unit,'ml.',ing)
    if gconv:
        unit = 'g.'
        if amount: amount = amount*gconv
    elif vconv:
        unit = 'ml.'
        if amount: amount = amount*vconv
    if unit in ['g.','ml.']:
        # Round to the 10s place...
        amount = round(amount,-1)
    istring = "%s %s %s"%(amount,unit,ing)
    return istring.lower()

def get_ingredient_hash (ings, conv):
    ings = [standardize_ingredient(i,conv) for i in ings]
    ings.sort()
    ings = '\n'.join(ings)
    m = md5.md5(ings)
    #print 'Hash',ings,m.hexdigest()
    return m.hexdigest()

def get_recipe_hash (recipe_object):
    recstrings = []
    for field in REC_FIELDS:
        if getattr(recipe_object,field): recstrings.append(getattr(recipe_object,field))
    recstring = '\n'.join(recstrings)
    recstring = recstring.strip()
    recstring = recstring.lower()
    #print 'hash',recstring
    m = md5.md5(recstring)
    return m.hexdigest()

def hash_recipe (rec, rd, conv=None):
    if not conv: conv = convert.converter()
    rechash = get_recipe_hash(rec)
    inghash = get_ingredient_hash(rd.get_ings(rec),conv)
    return rechash,inghash


# Diff stuff

# Convenience methods
def format_ing_text (ing_alist,rd,conv=None):
    strings = []
    for g,ings in ing_alist:
        if g: strings.append('\n<u>'+g+'</u>')
        for i in ings:
            istring = []
            a,u = rd.get_amount_and_unit(i,conv=conv)
            if a: istring.append(a)
            if u: istring.append(u)
            if i.item: istring.append(i.item)
            if (type(i.optional)!=str and i.optional) or i.optional=='yes': 
                    istring.append(_('(Optional)'))
            if i.refid: istring.append('=>%s'%i.refid)
            if i.ingkey: istring.append('key=%s'%i.ingkey)
            strings.append(xml.sax.saxutils.escape(' '.join(istring)))
    return '\n'.join(strings).strip()
            
def format_ings (rec, rd):
    ings = rd.get_ings(rec)
    alist = rd.order_ings(ings)
    return format_ing_text(alist,rd)

def apply_line_markup (line, markup):
    out = ''
    current_tag = ''
    if len(markup) < len(line):
        markup += ' '*(len(line)-len(markup))
    for n in range(len(line)):
        if markup[n]==' ':
            tag = None
        elif markup[n]=='+':
            tag = 'add'
        elif markup[n]=='-':
            tag = 'del'
        if tag != current_tag:
            if current_tag:
                out += '</%s>'%current_tag
            if tag:
                out += '<%s>'%tag
            current_tag = tag
        out += line[n]
    if current_tag:
        out += '</%s>'%current_tag
    return out

def get_diff_markup (s1,s2):
    diffs = []
    for line in difflib.ndiff(s1,s2):
        code = line[:2]
        line = line[2:]
        if code!='? ':
            diffs.append([code,line])
        else:
            diffs[-1][1] = apply_line_markup(diffs[-1][1],line)
    return diffs

def get_two_columns (s1,s2):
    diffs = get_diff_markup(s1,s2)
    left = []
    right = []
    for code,line in diffs:
        if code=='- ':
            left.append('<diff>'+line+'</diff>')
        elif code=='+ ':
            right.append('<diff>'+line+'</diff>')
        elif code=='  ':
            while len(left) < len(right):
                left.append('<diff/>')
            while len(right) < len(left):
                right.append('<diff/>')
            left.append(line)
            right.append(line)
    return left,right
        
def diff_ings (rec1,rec2,rd):
    ings1 = format_ings(rec1,rd)
    ings2 = format_ings(rec2,rd)
    if ings1 != ings2:
        return get_two_columns(ings1.splitlines(),ings2.splitlines())

def diff_recipe (rd,recs):
    diffs = {}
    for attr in ALL_ATTRS:
        if attr == 'category':
            vals = [', '.join(rd.get_cats(r)) for r in recs]
        else:
            vals = [getattr(r,attr) for r in recs]
        if vals != [vals[0]] * len(vals):
            #if TEXT_ATTR_DIC.has_key(attr):
            #    val1,val2 = 
            diffs[attr]=vals
    return diffs

def merge_recipes (rd, recs):
    diffs = diff_recipe(rd,recs)
    my_recipe = {}
    for attr,vals in diffs.items():
        # We don't care about fill-in-the-missing-thingy differences
        value = None
        conflict = False
        for v in vals:
            if not v:
                continue
            elif not value:
                value = v
            elif (v != value):
                if ((type(v) in types.StringTypes
                     and
                     type(value) in types.StringTypes)
                    and v.lower()==value.lower()):
                    continue
                else:
                    conflict = True
                    break
        if conflict: continue
        else:
            if value: my_recipe[attr]=value
            del diffs[attr]
    return my_recipe,diffs

if __name__ == '__main__' and False:
    import recipeManager
    rd = recipeManager.default_rec_manager()
    empty_hash = get_ingredient_hash([],None)
    rr = {}; ii = {}; ir = {}
    for rec in rd.fetch_all(rd.rview,deleted=False):
        rh,ih = hash_recipe(rec,rd)
        ch = rh+ih
        print ch,rec.id
        if ir.has_key(ch):
            print rec.id,rec.title,'is a complete duplicate of',ir[ch].id,ir[ch].title
            print 'Merge would be: ',merge_recipes(rec,ir[ch],rd)
        else:
            ir[ch]=rec
        if rr.has_key(rh):
            print rec.id,rec.title,'duplicates',rr[rh].id,rr[rh].title
            rdiff = diff_recipe(rec,rr[rh],rd)
            idiff =  diff_ings(rec,rr[rh],rd)
            if (not rdiff) and (not idiff):
                print 'PERFECT DUPS!'
            if rdiff:
                print 'Rec Diff'
                for k,v in rdiff.items(): print '%s: %s\t%s'%(k,v[0],v[1])
            if idiff:
                left,right = idiff
                print 'ING DIFF\n----------\n'
                for n in range(len(left)):
                    print left[n],right[n]
        else:
            rr[rh]=rec
        if ii.has_key(ih) and ih != empty_hash:
            print rec.id,rec.title,'duplicates ings',ii[ih].id,ii[ih].title
        else:
            ii[ih]=rec
