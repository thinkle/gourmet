from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag
from gi.repository import Pango


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
        self.markup_text: str = ""  # the resulting content
        self.current_opening_tags: str = ""  # used during parsing
        self.current_closing_tags: str = ""  # used during parsing

        # The key is the Pango id of a tag, and the value is a tuple of opening
        # and closing html tags for this id.
        self.tags: Dict[str: Tuple[str, str]] = {}

        # Optionally, links can be specified, in a {link text: target} format.
        self.links: Dict[str, str] = {}

        # Used as heuristics for parsing links, when applicable.
        self.is_colored_and_underlined: bool = False

    tag2html: Dict[str, Tuple[str, str]] = {
        Pango.Style.ITALIC.value_name: ("<i>", "</i>"),  # Pango doesn't do <em>
        str(Pango.Weight.BOLD.real): ("<b>", "</b>"),
        Pango.Underline.SINGLE.value_name: ("<u>", "</u>"),
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

    def feed(self, data: bytes, links: Optional[Dict[str, str]] = None) -> str:
        """Convert a buffer (text and and the buffer's iterators to html string.

        Unlike an HTMLParser, the whole string must be passed at once, chunks
        are not supported.

        Optionally, a dictionary of links, in the format {text: target}, can be
        specified. Links will be inserted if some text in the markup will be
        coloured, underlined, and matching an entry in the dictionary.
        """
        if links is not None:
            self.links = links

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

            # The tag may have a name, for named tags, or else an id
            tag_name = tag.attrs.get('id')
            tag_name = tag.attrs.get('name', tag_name)

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
        self.current_opening_tags = ""
        self.current_closing_tags = ""
        self.is_colored_and_underlined = False
        super().feed(text)
        return self.markup_text

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        # The only tag in pango markup is "apply_tag". This could be ignored or
        # made an assert, but we let our parser quietly handle nonsense.
        if tag == "apply_tag":
            attrs = dict(attrs)
            tag_name = attrs.get('id')  # A tag may have a name, or else an id
            tag_name = attrs.get('name', tag_name)
            tags = self.tags.get(tag_name)

            if tags is not None:
                self.current_opening_tags, self.current_closing_tags = tags

        if 'foreground' and '<u>' in self.current_opening_tags:
            self.is_colored_and_underlined = True

    def handle_data(self, data: str) -> None:
        target = self.links.get(data)

        if self.is_colored_and_underlined and target is not None:
            # Replace the markup tags with a hyperlink target
            data = f'<a href="{target}">{data}</a>'
        else:
            data = self.current_opening_tags + data + self.current_closing_tags

        self.markup_text += data

    def handle_endtag(self, tag: str) -> None:
        self.current_closing_tags = ""
        self.current_opening_tags = ""
        self.is_colored_and_underlined = False
