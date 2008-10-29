# -*- coding: utf-8 -*-
# vim: ts=4
###
#
# Listen is the legal property of mehdi abaakouk <theli48@gmail.com>
# Copyright (c) 2006 Mehdi Abaakouk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA
#
###
#
# python implementation of the gossip-expander-cellrenderer.c
# Copyright (C) 2006  Kristian Rietveld <kris@babi-pangang.org>
#
###

# To do:
#  - should probably cancel animation if model changes
#  - need to handle case where node-in-animation is removed
#  - it only handles a single animation at a time; but I guess users
#    aren't fast enough to trigger two or more animations at once anyway :P
#    (could guard for this by just cancelling the "old" animation, and
#     start the new one).
#

import gobject
import gtk

class CellRendererExpander(gtk.GenericCellRenderer):
    __gproperties__ = {
            "expander-style" : (
                gobject.TYPE_PYOBJECT,
                "__expander_style",
                "__expander_style",
                gobject.PARAM_READWRITE)
                
            }
            
    def __init__(self,*args,**kwargs):
        gtk.GenericCellRenderer.__init__(self,*args,**kwargs)

        self.__expander_style = gtk.EXPANDER_COLLAPSED
        self.__expander_size = 12

        self.__animation_view = None # GtkTreeView
        self.__animation_node = None # GtkTreeRowReference
        self.__animation_style = None
        self.__animation_timeout = -1 # Int
        self.__animation_area = None

        self.__activatable = True
        self.__animation_expanding = 1

        self.xpad = 2
        self.ypad = 2

        self.mode = gtk.CELL_RENDERER_MODE_ACTIVATABLE
        self.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)

    def do_set_property(self,property,value):
        if property.name == "expander-style":
            self.__expander_style = value
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def do_get_property(self, property):
        if property.name == "expander-style":
            return self.__expander_style
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def on_get_size(self, widget, cell_area=None):
        if cell_area:
            x_offset = self.get_property("xalign") * (cell_area.width - ( self.__expander_size + (3 * self.xpad)))
            x_offset = max (x_offset,0) 
            y_offset = self.get_property("yalign") * (cell_area.height - ( self.__expander_size + (2 * self.ypad)))
            y_offset = max (y_offset,0) 
        else:
            x_offset = 0 
            y_offset = 0 

        width = self.xpad * 2 + self.__expander_size
        height = self.ypad * 2 + self.__expander_size

        return (int(x_offset), int(y_offset), int(width), int(height))

    def on_render(self, window, widget, background_area, cell_area, expose_area, flags ):
        if self.__animation_node:
            path = self.__animation_node.get_path()
            rect = self.__animation_view.get_background_area(path, widget.get_column(0))
            if  background_area.y == rect.y:
                expander_style = self.__animation_style
            else:
                expander_style = self.__expander_style
        else:
            expander_style = self.__expander_style

        x_offset, y_offset, width, height = self.get_size(widget, cell_area)

        gtk.Style.paint_expander(widget.style, window, gtk.STATE_NORMAL, expose_area, widget, "treeview",
                cell_area.x + x_offset + self.xpad + self.__expander_size /2,
                cell_area.y + y_offset + self.ypad + self.__expander_size /2,
                expander_style);

    def invalide_node(self, treeview, path):
        bin = treeview.get_bin_window()
        rect = treeview.get_background_area(path, treeview.get_column(0))
        rect.x = 0
        rect.width = treeview.allocation.width
        bin.invalidate_rect(rect, True)

    def do_animation(self):
        done = False
        if self.__animation_expanding:
            if self.__animation_style == gtk.EXPANDER_SEMI_COLLAPSED:
                self.__animation_style = gtk.EXPANDER_SEMI_EXPANDED
            elif self.__animation_style == gtk.EXPANDER_SEMI_EXPANDED:
                self.__animation_style = gtk.EXPANDER_EXPANDED
                done = True
        else:
            if self.__animation_style == gtk.EXPANDER_SEMI_EXPANDED:
                self.__animation_style = gtk.EXPANDER_SEMI_COLLAPSED
            elif self.__animation_style == gtk.EXPANDER_SEMI_COLLAPSED:
                self.__animation_style = gtk.EXPANDER_COLLAPSED
                done = True

        path = self.__animation_node.get_path()
        self.invalide_node(self.__animation_view, path)

        if done :
            self.__animation_node = None
            self.__animation_timeout = 0

        return not done

    def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
        return None

    def animation_timeout(self):
        gtk.gdk.threads_enter()
        ret = self.do_animation()
        gtk.gdk.threads_leave()
        return ret

    def start_animation(self, treeview, path, expanding, background_area):
        if expanding:
            self.__animation_style = gtk.EXPANDER_SEMI_COLLAPSED
        else:
            self.__animation_style = gtk.EXPANDER_SEMI_EXPANDED

        self.invalide_node(treeview, path)

        self.__animation_expanding = expanding
        self.__animation_view = treeview
        self.__animation_node = gtk.TreeRowReference(treeview.get_model(), path)
        self.__animation_timeout = gobject.timeout_add(50, self.animation_timeout)

    # Won't work and i don't known why
    def on_activate(self, event, widget, path, background_area, cell_area, flags):
        if not widget or not self.__activatable:
            return False

        if (event.x - cell_area.x < 0) or (event.x - cell_area.x > cell_area.width):
            return False

        settings = widget.get_settings()
        animate = settings.get_property("gtk-enable-animations")
        
        if widget.row_expanded(path):
            widget.collapse_row(path)
            expanding = False
        else:
            widget.expand_row(path,False)
            expanding = True

        if True:
            self.start_animation(widget, path, expanding , background_area)

        return True
