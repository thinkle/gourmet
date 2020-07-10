from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag


class PangoToHtml(HTMLParser):
    """Decode a subset of Pango markup and serialize it as HTML.

    Because Pango can only deserialize a subset of HTML, the encoding here uses
    a subset of HTML. Moreover, only the Pango markup used within Gourmet is
    handled, although expanding it is not difficult.

    Due to the way that Pango attributes work, the HTML is not necessarily the
    simplest. For example italic tags may be closed early and reopened if other
    attributes, eg. bold, are inserted mid-way:

        <i> italic text </i><i><u>and underlined</u></i>

    This means that the HTML resulting from the conversion by this object may
    differ from the original that was fed to the caller.
    """
    def __init__(self):
        super().__init__()
        self.markup_text: str = ''  # the resulting content
        self.current_closing_tags: Optional[str] = None  # used during parsing

        # The key is the Pango id of a tag, and the value is a tuple of opening
        # and closing html tags for this id.
        self.tags: Dict[str: Tuple[str, str]] = {}

    tag2html: Dict[str, Tuple[str, str]] = {
        "PANGO_STYLE_ITALIC": ("<i>", "</i>"),  # Pango doesn't do <em>
        "700": ("<b>", "</b>"),  # TODO: Use the proper enum
        "PANGO_UNDERLINE_SINGLE": ("<u>", "</u>"),
        "foreground-gdk": (r'<span foreground="{}">', "</span>"),
        "background-gdk": (r'<span background="{}">', "</span>")
    }

    @staticmethod
    def pango_to_html_hex(val: str) -> str:
        """Convert 32 bit Pango color hex string to 16 html.

        Pango string have the format 'ffff:ffff:ffff' (for white).
        These values get truncated to 16 bits per color into a single string:
        '#FFFFFF'.
        """
        red, green, blue = val.split(":")
        red = hex(255 * int(red, base=16) // 65535)[2:].zfill(2)
        green = hex(255 * int(green, base=16) // 65535)[2:].zfill(2)
        blue = hex(255 * int(blue, base=16) // 65535)[2:].zfill(2)
        return f"#{red}{green}{blue}"

    def feed(self, data: bytes) -> str:
        """Convert a buffer (text and and the buffer's iterators to html string.

        Unlike an HTMLParser, the whole string must be passed at once, chunks
        are not supported.
        """

        # Remove the Pango header: it contains a length mark, which we don't
        # care about, but which does not necessarily decodes as valid char.
        header_end = data.find(b"<text_view_markup>")
        data = data[header_end:].decode()

        # Get the tags
        tags_begin = data.index("<tags>")
        tags_end = data.index("</tags>") + len("</tags>")
        tags = data[tags_begin:tags_end]
        data = data[tags_end:]

        # Get the textual content
        text_begin = data.index("<text>")
        text_end = data.index("</text>") + len("</text>")
        text = data[text_begin:text_end]

        # The remaining is serialized Pango footer, which we don't need.

        # Convert the tags to html. As our tags are anonymous, we must keep
        # track of them by their ids. Although anonymous tags are integers, we
        # still keep them as strings, would some changes elsewhere add str ids.

        # We know that only a subset of HTML is handled in Gourmet:
        # italics, bold, underlined, normal, and links (coloured and underlined)
        soup = BeautifulSoup(tags, features="lxml")
        tags = soup.find_all("tag")

        tags_list = {}
        for tag in tags:
            opening_tags = ""
            closing_tags = ""
            tag_name = tag.attrs['id']

            attributes = [c for c in tag.contents if isinstance(c, Tag)]
            for attribute in attributes:
                vtype = attribute['type']
                value = attribute['value']
                name = attribute['name']

                if vtype == "GdkColor":  # Convert colours to html
                    if name in ['foreground-gdk', 'background-gdk']:
                        opening, closing = self.tag2html[name]
                        hex_color = self.pango_to_html_hex(value)
                        opening = opening.format(hex_color)
                    else:
                        continue  # no idea!
                else:
                    opening, closing = self.tag2html[value]

                opening_tags += opening
                closing_tags = closing + closing_tags   # closing tags are FILO

            tags_list[tag_name] = opening_tags, closing_tags

            if opening_tags:
                tags_list[tag_name] = opening_tags, closing_tags

        self.tags = tags_list

        # Create a single output string that will be sequentially appended to
        # during feeding of text. It can then be returned once we've parse all
        self.markup_text = ""
        self.current_closing_tags = None
        super().feed(text)
        return self.markup_text

    def handle_starttag(self, tag: str, attrs: List[str]) -> None:
        if tag == "apply_tag":
            id_ = dict(attrs).get('id')
            tags = self.tags.get(id_)
            if tags is not None:
                self.current_closing_tags = tags[1]
                for t in tags[0]:
                    self.markup_text += t

    def handle_data(self, data: str) -> None:
        self.markup_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "apply_tag" and self.current_closing_tags is not None:
            for t in self.current_closing_tags:
                self.markup_text += t
            self.current_closing_tags = None
