#!/usr/bin/env python

if __name__ == '__main__' and False:

    def test_ing_editing (rc):
        rc.show_edit(module=rc.NOTEBOOK_ING_PAGE)        
        g = rc.ingtree_ui.ingController.add_group('Foo bar')
        for l in ('''1 c. sugar
        1 c. silly; chopped and sorted
        1 lb. very silly
        1 tbs. extraordinarily silly'''.split('\n')):
            rc.add_ingredient_from_line(l,group_iter=g)
        rc.ingtree_ui.ingController.delete_iters(g)
        rc.undo.emit('activate')

    import GourmetRecipeManager
    rg = GourmetRecipeManager.RecGui()
    gtk.main()
    rg.app.hide()
    try:
        rc = RecCard(rg,rg.rd.fetch_one(rg.rd.recipe_table,title='Black and White Cookies'))
        rc.display_window.connect('delete-event',
                                  lambda *args: gtk.main_quit()
                                  )
        rc.edit_window.connect('delete-event',lambda *args: gtk.main_quit())
        #rc.show_edit()
        #rc.rw['title'].set_text('Foo')
        
        test_ing_editing(rc)
    except:
        rg.app.hide()
        raise
    else:
        gtk.main()
