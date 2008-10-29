    def shop_recipes (self, *args):
        debug("shop_recipes",1)
        rr = self.get_selected_recipes()
        for r in rr:
            if r.servings and r.servings != "None":
                debug("servings=%s"%r.servings,5)
                serv = de.getNumber(default=float(r.servings),
                                    label=_("Number of servings of %s to shop for")%r.title,
                                    parent=self.app.get_toplevel())
                if serv: mult = float(serv)/float(r.servings)
                else:
                    debug('getNumber cancelled',2)
                    return
            else:
                mult = de.getNumber(default=float(1),
                                    label=_("Multiply %s by:")%r.title,
                                    parent=self.app.get_toplevel(),
                                    digits=2)
                if not mult:
                    mult = float(1)
            d = shopgui.getOptionalIngDic(self.db.get_ings(r),mult,self.prefs,self)
            self.sl.addRec(r,mult,d)
            self.sl.show()
