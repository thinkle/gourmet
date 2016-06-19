from __future__ import print_function

from gourmet.plugin import ToolPlugin
import gtk
import ipython_view
from gettext import gettext as _

class ConsolePlugin (ToolPlugin):

    menu_items = '''<placeholder name="StandaloneTool">
    <menuitem action="ShowConsole"/>
    </placeholder>'''

    def setup_action_groups (self):
        self.action_group = gtk.ActionGroup('ConsolePluginActionGroup')
        self.action_group.add_actions([
            ('ShowConsole',None,_('_Python Console'),
             None,_('Show python console (provides access to current gourmet instance)'),self.show_console)
            ]
                                      )
        self.action_groups.append(self.action_group)

    def show_console (self, *args):
        from gourmet.GourmetRecipeManager import get_application
        import sys, sqlalchemy
        sys.argv = []
        app = get_application()
        w = gtk.Window(); w.set_title('Gourmet Console')
        w.set_default_size(800,600)
        sw = gtk.ScrolledWindow()
        w.add(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        v = ipython_view.IPythonView()
        v.set_wrap_mode(gtk.WRAP_CHAR)
        sw.add(v)
        def info ():
            print("""Welcome to the interactive shell. You have full access to
            the current instance of Gourmet from here, which means of
            course you could really hose your system if you're not
            careful.
            
            The following local variables are defined for your convenience:

            app - the main GourmetApplication singleton
            
            rd - the main recipeManager singleton (Gourmet's interface
                 to the DB)
            
            db - the sqlalchemy interface to the DB (a level of
                 abstraction closer to sql)

            v - this IPythonView itself

            consolePlugin - the plugin that gave you this tool.""")
            
        v.updateNamespace({'app':app,
                           'rd':app.rd,
                           'db':app.rd.db,
                           'consolePlugin':self,
                           'v':v,
                           'info':info,
                           'gtk':gtk,
                           'sqlalchemy':sqlalchemy,
                           })
        v.write('info()')
        w.show_all()

plugins = [ConsolePlugin]
