from __future__ import print_function

import gtk

def fix_action_group_importance (ag):
    for action in ag.list_actions():
        ifact = gtk.IconFactory()
        if not action.get_property('stock-id') or not  ifact.lookup(action.get_property('stock-id')):
            # print('No icon found for', action)
            action.set_property('is-important',True)
