import gtk
import gtk.glade

    def exportg (self, export_all=False):
        """If all is false, export only selected recipes.

        If all is True, export all recipes.
        """
        if not use_threads and self.lock.locked_lock():
            de.show_message(
                parent=self.app.get_toplevel(),
                label=_('An import, export or deletion is running'),
                sublabel=_('Please wait until it is finished to start your export.')
                            )
            return
        saveas_filters = exporters.saveas_filters[0:]
        ext = self.prefs.get('save_recipes_as','%sxml'%os.path.extsep)
        exp_directory = self.prefs.get('rec_exp_directory','~')
        file,exp_type=de.saveas_file(_("Export recipes"),
                                     filename="%s/%s%s"%(exp_directory,_('recipes'),ext),
                                     parent=self.app.get_toplevel(),
                                     filters=saveas_filters)
        if file:
            self.prefs['rec_exp_directory']=os.path.split(file)[0]
            self.prefs['save_recipes_as']=os.path.splitext(file)[1]
            expClass=None
            post_hooks = [self.after_dialog_offer_url(exp_type,file)]
            if exporters.exporter_dict.has_key(exp_type):
                myexp = exporters.exporter_dict[exp_type]
                if myexp.has_key('extra_prefs_dialog'):
                    extra_prefs = myexp['extra_prefs_dialog']()
                else:
                    extra_prefs = {}
                pd_args={'label':myexp['label'],'sublabel':myexp['sublabel']%{'file':file}}
                if export_all: recs = self.rd.fetch_all(self.rd.rview,deleted=False,sort_by=[('title',1)])
                else: recs = self.recTreeSelectedRecs()
                expClass = myexp['mult_exporter']({'rd':self.rd,
                                                   'rv': recs,
                                                   'conv':self.conv,
                                                   'prog':self.set_progress_thr,
                                                   'file':file,
                                                   'extra_prefs':extra_prefs,
                                                   })
            if expClass:
                self.threads += 1
                def show_progress (t):
                    debug('showing pause button',1)
                    gt.gtk_enter()
                    self.show_progress_dialog(t,message=_('Export Paused'),stop_message=_("Stop export"),
                                              progress_dialog_kwargs=pd_args,
                                              )
                    gt.gtk_leave()
                pre_hooks = [show_progress]
                pre_hooks.insert(0, lambda *args: self.lock.acquire())
                #post_hooks.append(lambda *args: self.reset_prog_thr())
                post_hooks.append(lambda *args: self.lock.release())
                t=gt.SuspendableThread(expClass, name='export',
                                    pre_hooks=pre_hooks,
                                    post_hooks=post_hooks)
                if self.lock.locked_lock():
                    de.show_message(label=_('An import, export or deletion is running'),
                                    sublabel=_('Your export will start once the other process is finished.'))
                debug('PRE_HOOKS=%s'%t.pre_hooks,1)
                debug('POST_HOOKS=%s'%t.post_hooks,1)                
                t.start()
                if not use_threads:
                    if not hasattr(self,'_threads'): self._threads = []
                    self._threads.append(t)
            else:
                de.show_message(label=_('Gourmet cannot export file of type "%s"')%os.path.splitext(file)[1],
                                message_type=gtk.MESSAGE_ERROR)

    def import_pre_hook (self, *args):
        debug('import_pre_hook, gt.gtk_enter()',1)
        debug('about to run... %s'%self.rd.add_hooks[1:-1],1)
        gt.gtk_enter()

    def import_post_hook (self, *args):
        debug('import_post_hook,gt.gtk_leave()',5)
        gt.gtk_leave()

    def import_webpageg (self, *args):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to start your import.')
                            )
            return
        import importers.html_importer
        sublabel = _('Enter the URL of a recipe archive or recipe website.')
        url = de.getEntry(label=_('Enter website address.'),
                          sublabel=sublabel,
                          entryLabel=_('Enter URL:'),
                          entryTip=_('Enter the address of a website or recipe archive. The address should begin with http://'),
                          default_character_width=60,
                          )
        if not url: return
        if url.find('//')<0:
            url = 'http://'+url
        self.show_progress_dialog(None,
                                  progress_dialog_kwargs={'label':_('Importing recipe from %s')%url,
                                                      'stop':False,
                                                      'pause':False,})
        try:
            i=importers.html_importer.import_url(
                url,
                self.rd,
                progress=self.set_progress_thr,
                threaded=True)
            if type(i)==list:
                impClass,cant_import = self.prepare_import_classes(i)
                if impClass:
                    self.run_import(impClass,url,display_errors=False)
                else:
                    raise NotImplementedError("Gourmet cannot import")
            else:
                self.run_import(i,url,display_errors=False)
        except NotImplementedError:
            sublabel=_('Gourmet does not know how to import site %s')%url
            sublabel += "\n"
            sublabel += _('Are you sure %(url)s points to a page with a recipe on it?')%locals()
            de.show_message(label=_('Unable to import'),
                            sublabel=sublabel,
                            message_type=gtk.MESSAGE_ERROR)
            self.hide_progress_dialog()
        except BadZipfile:
            de.show_message(label=_('Unable to unzip'),
                            sublabel=_('Gourmet is unable to unzip the file %s')%url,
                            message_type=gtk.MESSAGE_ERROR)
        except IOError:
            self.hide_progress_dialog()
            de.show_traceback(label=_('Unable to retrieve URL'),
                              sublabel=_("""Gourmet was unable to retrieve the site %s. Are you sure your internet connection is working?  If you can retrieve the site with a webbrowser but continue to get this error, please submit a bug report at %s.""")%(url,BUG_URL)
                              )
            raise
        except gt.Terminated:
            if self.threads > 0: self.threads = self.threads - 1
            self.lock.release()
        except:
            self.hide_progress_dialog()
            de.show_traceback(
                label=_('Error retrieving %(url)s.')%locals(),
                sublabel=_('Are you sure %(url)s points to a page with a recipe on it?')%locals()
                )
            raise
        self.make_rec_visible()
        
    def importg (self, *args):
        if not use_threads and self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Please wait until it is finished to start your import.')
                            )
            return
        import_directory = "%s/"%self.prefs.get('rec_import_directory',None)
        debug('show import dialog',0)
        ifiles=de.select_file(
            _("Import Recipes"),
            filename=import_directory,
            filters=importers.FILTERS,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            select_multiple=True)
        if ifiles:
            self.prefs['rec_import_directory']=os.path.split(ifiles[0])[0]
            self.import_multiple_files(ifiles)
        self.make_rec_visible()
            
    def prepare_import_classes (self, files):
        """Handed multiple import files, prepare to import.

        We return a tuple (importerClasses,cant_import)

        importClass - an instance of importers.importer.MultipleImport
        which handles the actual import when their run methods are
        called.

        cant_import - a list of files we couldn't import.

        This does most of the work of import_multiple_files, but
        leaves it up to our caller to display our progress dialog,
        etc.
        """
        impClass = None            
        importerClasses = []
        cant_import = []
        # we're going to make a copy of the list and chew it up. We do
        # this rather than doing a for loop because zip files or other
        # archives can end up expanding our list
        imp_files = files[0:] 
        while files:
            fn = files.pop()
            if type(fn)==str and os.path.splitext(fn)[1] in ['.gz','.gzip','.zip','.tgz','.tar','.bz2']:
                try:
                    debug('trying to unzip %s'%fn,0)
                    from importers.zip_importer import archive_to_filelist
                    archive_files = archive_to_filelist(fn)
                    for a in archive_files:
                        if type(a) == str:
                            files += [a]
                        else:
                            # if we have file objects, we're going to write
                            # them out to real files, so we don't have to worry
                            # about details later (this is stupid, but I'm sick of
                            # tracking down places where I e.g. closed files regardless
                            # of whether I opened them)
                            finame=tempfile.mktemp(a.name)
                            tfi=open(finame,'w')
                            tfi.write(a.read())
                            tfi.close()
                            files += [finame]
                    continue
                except:
                    cant_import.append(fn)
                    raise
                    continue
            try:
                impfilt = importers.FILTER_INFO[importers.select_import_filter(fn)]
            except NotImplementedError:
                cant_import.append(fn)
                continue
            impClass = impfilt['import']({'file':fn,
                                          'rd':self.rd,
                                          'threaded':True,
                                          })
            if impfilt['get_source']:
                if type(fn)==str: fname = fn
                else: fname = "file"
                source=de.getEntry(label=_("Default source for recipes imported from %s")%fname,
                                   entryLabel=_('Source:'),
                                   default=os.path.split(fname)[1], parent=self.app)
                # the 'get_source' dict is the kwarg that gets
                # set to the source
                impClass[2][impfilt['get_source']]=source
            if impClass: importerClasses.append((impClass,fn))
            else:
                debug('GOURMET cannot import file %s'%fn)
        if importerClasses:
            impClass = importers.importer.MultipleImporter(self,
                                                           importerClasses)
            return impClass,cant_import
        else:
            return None,cant_import

    def import_multiple_files (self, files):
        """Import multiple files,  showing dialog."""
        # This should probably be moved to importer with a quiet/not quiet options
        # and all of the necessary connections handed as arguments.
        impClass,cant_import=self.prepare_import_classes(files)
        if impClass:
            filenames = filter(lambda x: isinstance(x,str), files)
            self.run_import(
                impClass,
                import_source=string.join([os.path.split(f)[1] for f in filenames],", ")
                )
        if cant_import:
            # if this is a file with a name...
            BUG_URL="http://sourceforge.net/tracker/?group_id=108118&atid=649652"
            sublabel = gettext.ngettext("Gourmet could not import the file %s",
                                            "Gourmet could not import the following files: %s",
                                            len(cant_import))%", ".join(cant_import)
            sublabel += "\n"
            sublabel += gettext.ngettext(
                "If you believe this file is in one of the formats Gourmet supports, please submit a bug report at %s and attach the file.",
                "If you believe these files are in a format Gourmet supports, please submit a bug report at %s and attach the file.",
                len(cant_import))%BUG_URL
            self.offer_url(
                label=gettext.ngettext("Cannot import file.",
                                       "Cannot import files.",
                                       len(cant_import)),
                sublabel=sublabel,
                url=BUG_URL)
            return

    def run_import (self, impClass, import_source="", display_errors=True):
        """Run our actual import and display progress dialog."""
        # we have to make sure we don't filter while we go (to avoid
        # slowing down the process too much).
        self.wait_to_filter=True
        self.last_impClass = impClass
        pre_hooks = [lambda *args: self.inginfo.disconnect_manually()]
        post_hooks = [lambda *args: self.inginfo.reconnect_manually()]
        pre_hooks.append(lambda *args: self.rd.add_hooks.insert(0,self.import_pre_hook))
        pre_hooks.append(lambda *args: self.rd.add_hooks.append(self.import_post_hook))
        self.threads += 1
        release = lambda *args: self.lock.release()
        post_hooks.extend([self.import_cleanup,
                           lambda *args: setattr(self,'last_impClass',None),
                           release])
        def show_progress_dialog (t):
            debug('showing progress dialog',3)
            gt.gtk_enter()
            if import_source:
                sublab = _('Importing recipes from %s')%import_source
            else: sublab = None
            self.rg.show_progress_dialog(
                t,
                {'label':_('Importing Recipes'),
                 'sublabel':sublab
                 })
            gt.gtk_leave()
        pre_hooks.insert(0,show_progress_dialog)
        pre_hooks.insert(0, lambda *args: self.lock.acquire())
        t=gt.SuspendableThread(impClass,name="import",
                               pre_hooks=pre_hooks, post_hooks=post_hooks,
                               display_errors=display_errors)
        if self.lock.locked_lock():
            de.show_message(label=_('An import, export or deletion is running'),
                            sublabel=_('Your import will start once the other process is finished.'))
        debug('starting thread',2)
        debug('PRE_HOOKS=%s'%t.pre_hooks,1)
        debug('POST_HOOKS=%s'%t.post_hooks,1)
        t.start()

    def import_cleanup (self, *args):
        """Remove our threading hooks"""
        debug('import_cleanup!',1)
        self.rd.add_hooks.remove(self.import_pre_hook)
        self.rd.add_hooks.remove(self.import_post_hook)
        debug('hooks: %s'%self.rd.add_hooks,1)
        self.wait_to_filter=False
        gt.gtk_enter()
        # Check for duplicates
        if self.last_impClass and self.last_impClass.added_recs:
            rmd = RecipeMergerDialog(
                self.rd,
                in_recipes=self.last_impClass.added_recs,
                on_close_callback=lambda *args: self.redo_search()
                )
            rmd.show_if_there_are_dups(
                label=_('Some of the imported recipes appear to be duplicates. You can merge them here, or close this dialog to leave them as they are.')
                )
        # Update our models for category, cuisine, etc.
        self.updateAttributeModels()
        # Reset our index view
        self.redo_search()
        gt.gtk_leave()

    def after_dialog_offer_url (self, linktype, file):
        url = "file:///%s"%file
        label = _("Export succeeded")
        if linktype == exporters.WEBPAGE:
            url += '/index.htm'
            linktype = _("webpage")
        sublabel = _("Exported %s to %s")%(linktype,file)
        def offerer (t):
            if t.completed:
                self.offer_url(label, sublabel, url, True)
        return offerer

    def offer_url (self, label, sublabel, url, from_thread=False):
        if from_thread:
            gt.gtk_enter()
        if hasattr(self,'progress_dialog'):
            self.hide_progress_dialog()            
        d=de.MessageDialog(label=label,
                           sublabel=sublabel,
                           cancel=False
                           )
        b = gtk.Button(stock=gtk.STOCK_JUMP_TO)
        b.connect('clicked',lambda *args: launch_url(url))
        d.vbox.pack_end(b,expand=False)
        b.show()
        d.run()
        if from_thread:
            gt.gtk_leave()
