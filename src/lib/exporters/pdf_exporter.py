from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
import reportlab.platypus as platypus
import reportlab.lib.pagesizes as pagesizes
import reportlab.lib.fonts as fonts
import reportlab.lib.units as units
import reportlab.lib.styles as styles
from gettext import gettext as _
import convert

def write_shopping_list (shopper, recs, file, head=_('Shopping List')):
    # setup document
    doc = platypus.SimpleDocTemplate(file)
    styleSheet=styles.getSampleStyleSheet()
    normsty=styleSheet['Normal']
    catheadsty=styleSheet['Heading3']
    headsty = styleSheet['Heading1']
    spacer = platypus.Spacer(1,0.2*units.inch)
    # organize shopping output
    org = shopper.organize(shopper.dic)
    txt = []
    txt.append(platypus.Paragraph(head,headsty))
    txt.append(platypus.Paragraph(_("Shopping list for: "),catheadsty))
    for r,mult in recs.items():
        recline = "%s"%r.title

        if mult: recline += " x%s"%convert.float_to_frac(mult)
        p=platypus.Paragraph(recline,normsty)
        txt.append(p)
    txt.append(spacer)
    for c,d in org:
        print 'category: ',c,' d: ',d
        p=platypus.Paragraph(c,catheadsty)
        # space around the paragraph...        
        #txt.append(spacer)
        txt.append(p)
        for i,a in d:
            p=platypus.Paragraph("%s %s"%(a,i),normsty)
            txt.append(p)
        # space around the list...
        #txt.append(spacer)
    #print 'txt: ',txt
    doc.build(txt)
