from gourmet.defaults.defaults import lang as defaults
from gourmet.gdebug import debug
from gourmet.gglobals import doc_base, icondir
from gourmet import version

import gtk.gdk
import os.path

# About/Help
def show_about (*args):
    """Show information about ourselves."""
    debug("show_about ():",5)
    translator=_("translator-credits")
    # translators should translate the string 'translator-credits'
    # If we're not using a translation, then this isn't shown
    if translator == "translator-credits":
        translator = None
    # Grab CREDITS from our defaults_LANG file too!
    if hasattr(defaults,'CREDITS') and defaults.CREDITS:
        if translator and translator.find(defaults.CREDITS) > -1:
            translator += "\n%s"%defaults.CREDITS
        else:
            translator = defaults.CREDITS

    logo=gtk.gdk.pixbuf_new_from_file(os.path.join(icondir,"gourmet.png"))

    # load LICENSE text file
    try:
        license_text = open(os.path.join(doc_base,'LICENSE'),'r').read()
    except IOError, err:
        print "IO Error %s" % err
    except:
        print "Unexpexted error"

    paypal_link = """https://www.paypal.com/cgi-bin/webscr?cmd=_donations
&business=Thomas_Hinkle%40alumni%2ebrown%2eedu
&lc=US&item_name=Gourmet%20Recipe%20Manager%20Team&no_note=0&currency_code=USD
&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedGuest"""
    gittip_link = "https://www.gittip.com/on/github/thinkle/"
    flattr_link = "http://flattr.com/profile/Thomas_Hinkle/things"

    about = gtk.AboutDialog()
    about.set_artists(version.artists)
    about.set_authors(version.authors)
    about.set_comments(version.description)
    about.set_copyright(version.copyright)
    #about.set_documenters(None)
    about.set_license(license_text)
    about.set_logo(logo)
    about.set_program_name(version.appname)
    about.set_translator_credits(translator)
    about.set_version(version.version)
    #about.set_wrap_license(True)
    about.set_website(version.website)
    #about.set_website_label('Gourmet website')

    donation_buttons = gtk.HButtonBox()
    donation_buttons.set_layout(gtk.BUTTONBOX_SPREAD)
    donations_label = gtk.Label(_("Please consider making a donation to "
    "support our continued effort to fix bugs, implement features, "
    "and help users!"))
    donations_label.set_line_wrap(True)
    donations_label.show()
    paypal_button = gtk.LinkButton(paypal_link, _("Donate via PayPal"))
    paypal_button.show()
    flattr_button = gtk.LinkButton(flattr_link, _("Micro-donate via Flattr"))
    flattr_button.show()
    gittip_button = gtk.LinkButton(gittip_link, _("Donate weekly via Gittip"))
    gittip_button.show()
    donation_buttons.add(paypal_button)
    donation_buttons.add(gittip_button)
    donation_buttons.add(flattr_button)
    donation_buttons.show()
    content = about.get_content_area()
    content.add(donations_label)
    content.add(donation_buttons)

    about.run()
    about.destroy()