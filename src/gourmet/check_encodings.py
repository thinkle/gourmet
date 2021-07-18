from typing import Dict

from gi.repository import Gtk

from gourmet.i18n import _

from .gdebug import debug
from .gtk_extras import dialog_extras as de
from .prefs import Prefs


class CheckEncoding:
    """A class to read a file and guess the correct text encoding."""

    encodings = ['iso8859', 'ascii', 'latin_1', 'cp850', 'cp1252', 'utf-8']
    all_encodings = ['ascii', 'cp037', 'cp424', 'cp437', 'cp500', 'cp737',
                     'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857',
                     'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865',
                     'cp869', 'cp874', 'cp875', 'cp1006', 'cp1026', 'cp1140',
                     'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254',
                     'cp1255', 'cp1256', 'cp1258', 'latin_1', 'iso8859_2',
                     'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6',
                     'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10',
                     'iso8859_13', 'iso8859_14', 'iso8859_15', 'koi8_r',
                     'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland',
                     'mac_latin2', 'mac_roman', 'mac_turkish', 'utf_16',
                     'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8']

    def __init__(self, file, encodings=None):
        if Prefs.instance().get('utf-16', False):
            self.encodings.extend(['utf_16', 'utf_16_le', 'utf_16_be'])
        if encodings is not None:
            self.encodings = encodings
        if isinstance(file, str):
            file = open(file, 'rb')
        self.txt = file.read()
        file.close()

    def test_encodings(self):
        """Move through self.encodings one at a time and return the first
        encoding that decodes our text cleanly. We return a tuple (encoding,decoded_text)"""
        for e in self.encodings:
            try:
                t=self.txt.decode(e)
                return (e,t)
            except UnicodeDecodeError:
                pass

    def get_encodings (self):
        encs = self.test_all_encodings(self.encodings)
        if encs:
            return encs
        else:
            return self.test_all_encodings(self.all_encodings)

    def test_all_encodings (self,encodings=None):
        """Test all encodings and return a dictionary of possible encodings."""
        if not encodings:
            encodings=self.all_encodings
        self.possible_encodings = {}
        for e in encodings:
            try:
                d=self.txt.decode(e)
                if d and (d not in self.possible_encodings.values()):
                    # if we don't already have this possibility, add
                    self.possible_encodings[e] = d
            except UnicodeDecodeError:
                pass
        return self.possible_encodings

class GetFile(CheckEncoding):
    """Handed a filename, return a list of lines."""
    def __init__(self, file: str, encodings=None):
        super().__init__(file, encodings)
        encs: Dict[str, str] = self.get_encodings()
        if encs:
            if len(list(encs.keys())) > 1:
                encoding = getEncoding(encodings=encs)
            else:
                encoding = list(encs.keys())[0]
            self.enc = encoding
            self.lines = encs[self.enc].splitlines()
            debug('reading file %s as encoding %s'%(file, self.enc))
        else:
            raise Exception("Cannot decode file %s" % file)


def get_file(file: str, encodings=None):
    gf = GetFile(file, encodings)
    return gf.lines


class EncodingDialog(de.OptionDialog):
    """Create a dialog to allow user to select correct encoding for an input file."""

    context_lines = 2

    def __init__(self, default=None, label=_("Select encoding"),
                 sublabel=_("Cannot determine proper encoding. Please select the correct encoding from the following list."),
                 expander_label=_("See _file with encoding"),
                 encodings=None):
        self.diff_lines = {}
        self.cursor_already_set = False
        self.expander_label = expander_label
        self.encodings = encodings if encodings is not None else {}
        self.current_error = 0
        self.diff_texts()
        self.options = self.create_options()
        expander = self.create_expander()
        self.setup_buffers()
        super().__init__(default=default, label=label, sublabel=sublabel,
                         options=self.options, expander=expander)
        self.set_default_size(700, 500)
        self.combobox.connect('changed', self.change_encoding)
        self.change_encoding()
        self.created = False
        self.expander.set_expanded(True)

    def setup_motion_buttons (self):
        self.hbb = Gtk.HButtonBox()
        self.fb = Gtk.Button('Next Difference')
        self.pb = Gtk.Button('Previous Difference')
        self.pb.connect('clicked',lambda *args: self.move_to_difference(forward=False))
        self.fb.connect('clicked',lambda *args: self.move_to_difference(forward=True))
        self.hbb.add(self.pb)
        self.hbb.add(self.fb)
        self.evb.add(self.hbb)
        self.hbb.show_all()

    def get_option(self, widget):
        super().get_option(widget)
        self.change_encoding()

    def create_options (self):
        options = list(self.encodings.keys())
        masterlist = CheckEncoding.encodings + CheckEncoding.all_encodings
        options.sort(key=lambda x: masterlist.index(x))
        return options

    def create_expander(self):
        self.evb = Gtk.VBox(vexpand=True)
        self.tv = Gtk.TextView()
        self.tv.set_editable(False)
        self.buffer = self.tv.get_buffer()
        self.evb.pack_start(self.tv, expand=True, fill=True, padding=0)
        self.evb.show_all()
        return self.expander_label, self.evb

    def setup_buffers (self):
        self.encoding_buffers={}
        for k,t in list(self.encodings.items()):
            self.encoding_buffers[k]=Gtk.TextBuffer()
            self.highlight_tags = [self.encoding_buffers[k].create_tag(background='yellow')]
            self.line_highlight_tags = [self.encoding_buffers[k].create_tag(background='green')]
            self.set_buffer_text(self.encoding_buffers[k],t)

    def change_encoding (self, _widget=None):
        if self.cursor_already_set:
            im=self.buffer.get_insert()
            ti=self.buffer.get_iter_at_mark(im)
            offset=ti.get_offset()
        self.tv.set_buffer(self.encoding_buffers[self.ret])
        self.buffer = self.encoding_buffers[self.ret]
        debug('changed text to encoding %s'%self.ret,0)

    def move_to_difference (self, forward=True):
        dkeys = list(self.diff_lines.keys())
        dkeys.sort()
        if forward:
            self.current_error += 1
        else:
            self.current_error = self.current_error - 1
        if self.current_error > len(dkeys): self.current_error = 0
        if self.current_error < 0: self.current_error = len(dkeys)-1
        mark=self.buffer.create_mark(
            None,
            self.buffer.get_iter_at_line_index(dkeys[self.current_error],0),
            False,
            )
        self.tv.scroll_to_mark(mark,0)

    def set_buffer_text (self, buffer, text):
        """Set buffer text to show encoding differences."""
        lines = text.splitlines()
        totl = len(lines)
        shown = []
        for line,diffs in list(self.diff_lines.items()):
            if line in shown: continue
            start_at = line - self.context_lines
            if start_at < 0: start_at = 0
            end_at = line + self.context_lines
            if end_at >= totl: end_at = totl-1
            if start_at != 0:
                buffer.insert_with_tags(buffer.get_end_iter(),
                                        '\n...\n',
                                        )
            for n in range(start_at,end_at):
                if n in shown:
                    continue
                shown.append(n)
                l = lines[n]
                if n==line:
                    start = 0
                    for sdiff,ediff in diffs:
                        buffer.insert_with_tags(buffer.get_end_iter(),
                                                l[start:sdiff],
                                                *self.line_highlight_tags)
                        buffer.insert_with_tags(buffer.get_end_iter(),
                                                l[sdiff:ediff],
                                                *self.highlight_tags)
                        start = ediff
                    buffer.insert_with_tags(buffer.get_end_iter(),
                                            l[start:],
                                            *self.line_highlight_tags)
                else:
                    buffer.insert_with_tags(buffer.get_end_iter(),l)

    def diff_texts(self):
        """Compare different encoding for characters where they differ."""
        encoded_buffers = list(self.encodings.values())
        # Sort by number of newlines (most first)
        encoded_buffers.sort(key=lambda x: len(x.splitlines()), reverse=True)
        enc1 = encoded_buffers[0]
        enc_rest = [e.splitlines() for e in encoded_buffers[1:]]

        for linenum, line in enumerate(enc1.splitlines()):
            other_lines = [len(e) > linenum and e[linenum] for e in enc_rest]
            # Remove any Falses returned by above
            other_lines = [x for x in other_lines if not isinstance(x, bool)]

            # If not all lines are the same, create a diff marking where they
            # differ.
            if not all(line == ol for ol in other_lines):
                ranges = []
                for chnum, ch in enumerate(line):
                    # Check that the lines are the same. If not, mark where
                    if not all([len(line) > chnum and ch == line[chnum]
                                for line in other_lines]):
                        if ranges and ranges[-1][1] == chnum:
                            ranges[-1][1] = chnum+1
                        else:
                            ranges.append([chnum, chnum+1])
                self.diff_lines[linenum] = ranges


def getEncoding(*args, **kwargs):
    dialog = EncodingDialog(*args, **kwargs)
    result = dialog.run()
    if (not result) and dialog.encodings:
        return dialog.options[0]
    elif not result:
        return 'ascii'
    else:
        return result
