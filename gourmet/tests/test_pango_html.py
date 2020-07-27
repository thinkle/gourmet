from gourmet.gtk_extras.pango_html import PangoToHtml


def test_convert_colors_to_html():
    val = "0:0:0"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#000000"

    val = "ffff:0:0"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#ff0000"

    val = "0:ffff:0"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#00ff00"

    val = "0:0:ffff"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#0000ff"

    val = "ffff:ffff:ffff"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#ffffff"

    val = "0:00000000:ffff"  # add some arbitrary amounts of leading zeroes
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#0000ff"

    val = "ff00:d700:0000"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#fed600"  # Gold

    val = "ffff:1414:9393"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#ff1493"  # Deep Pink

    val = "4747:5f5f:9494"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#475f94"  # Some Blue

    val = "00fd:ffdc:ff5c"
    ret = PangoToHtml.pango_to_html_hex(val)
    assert ret == "#00fefe"  # Some other blue


def test_pango_markup_to_html():
    # These are examples found throughout the application

    pango_markup = b'GTKTEXTBUFFERCONTENTS-0001\x00\x00\x07Z <text_view_markup>\n <tags>\n  <tag id="12" priority="12">\n  </tag>\n  <tag id="2" priority="2">\n   <attr name="style" type="PangoStyle" value="PANGO_STYLE_ITALIC" />\n  </tag>\n  <tag id="8" priority="8">\n  </tag>\n  <tag id="3" priority="3">\n  </tag>\n  <tag id="7" priority="7">\n   <attr name="background-gdk" type="GdkColor" value="0:0:ffff" />\n  </tag>\n  <tag id="4" priority="4">\n   <attr name="style" type="PangoStyle" value="PANGO_STYLE_ITALIC" />\n   <attr name="weight" type="gint" value="700" />\n  </tag>\n  <tag id="5" priority="5">\n   <attr name="style" type="PangoStyle" value="PANGO_STYLE_ITALIC" />\n   <attr name="weight" type="gint" value="700" />\n   <attr name="underline" type="PangoUnderline" value="PANGO_UNDERLINE_SINGLE" />\n  </tag>\n  <tag id="0" priority="0">\n   <attr name="weight" type="gint" value="700" />\n  </tag>\n  <tag id="1" priority="1">\n  </tag>\n  <tag id="6" priority="6">\n  </tag>\n  <tag id="9" priority="9">\n   <attr name="foreground-gdk" type="GdkColor" value="0:0:ffff" />\n  </tag>\n  <tag id="11" priority="11">\n   <attr name="background-gdk" type="GdkColor" value="0:0:ffff" />\n   <attr name="foreground-gdk" type="GdkColor" value="ffff:ffff:ffff" />\n  </tag>\n  <tag id="10" priority="10">\n  </tag>\n </tags>\n<text><apply_tag id="0">This is bold</apply_tag><apply_tag id="1">. </apply_tag><apply_tag id="2">This is italic</apply_tag><apply_tag id="3">\n            </apply_tag><apply_tag id="4">This is bold, italic, and </apply_tag><apply_tag id="5">underlined!</apply_tag><apply_tag id="6">\n            </apply_tag><apply_tag id="7">This is a test of bg color</apply_tag><apply_tag id="8">\n            </apply_tag><apply_tag id="9">This is a test of fg color</apply_tag><apply_tag id="10">\n            </apply_tag><apply_tag id="11">This is a test of fg and bg color</apply_tag><apply_tag id="12">\n           +</apply_tag></text>\n</text_view_markup>\n'  # noqa
    expected = '<b>This is bold</b>. <i>This is italic</i>\n            <i><b>This is bold, italic, and </b></i><i><b><u>underlined!</u></b></i>\n            <span background="#0000ff">This is a test of bg color</span>\n            <span foreground="#0000ff">This is a test of fg color</span>\n            <span background="#0000ff"><span foreground="#ffffff">This is a test of fg and bg color</span></span>\n           +'  # noqa

    ret = PangoToHtml().feed(pango_markup)
    assert ret == expected

    links = {'a link': 'foo', 'fancy, fancy': 'fancy_desc',
             'recipe link': '123:foo', '¼ recipe boogoochooboo': '456:boo'}
    pango_markup = b'GTKTEXTBUFFERCONTENTS-0001\x00\x00\x07\xfa <text_view_markup>\n <tags>\n  <tag id="13" priority="13">\n   <attr name="weight" type="gint" value="700" />\n  </tag>\n  <tag id="14" priority="14">\n  </tag>\n  <tag id="0" priority="0">\n  </tag>\n  <tag id="1" priority="1">\n   <attr name="style" type="PangoStyle" value="PANGO_STYLE_ITALIC" />\n  </tag>\n  <tag id="2" priority="2">\n  </tag>\n  <tag id="3" priority="3">\n   <attr name="underline" type="PangoUnderline" value="PANGO_UNDERLINE_SINGLE" />\n  </tag>\n  <tag id="5" priority="5">\n   <attr name="foreground-gdk" type="GdkColor" value="0:0:ffff" />\n   <attr name="underline" type="PangoUnderline" value="PANGO_UNDERLINE_SINGLE" />\n  </tag>\n  <tag id="9" priority="9">\n   <attr name="foreground-gdk" type="GdkColor" value="0:0:ffff" />\n   <attr name="underline" type="PangoUnderline" value="PANGO_UNDERLINE_SINGLE" />\n  </tag>\n  <tag id="6" priority="6">\n  </tag>\n  <tag id="8" priority="8">\n  </tag>\n  <tag id="10" priority="10">\n  </tag>\n  <tag id="7" priority="7">\n   <attr name="foreground-gdk" type="GdkColor" value="0:0:ffff" />\n   <attr name="underline" type="PangoUnderline" value="PANGO_UNDERLINE_SINGLE" />\n  </tag>\n  <tag id="4" priority="4">\n  </tag>\n  <tag id="11" priority="11">\n   <attr name="foreground-gdk" type="GdkColor" value="0:0:ffff" />\n   <attr name="underline" type="PangoUnderline" value="PANGO_UNDERLINE_SINGLE" />\n  </tag>\n <tag id="12" priority="12">\n </tag>\n </tags>\n<text><apply_tag id="0">This is some text\n Some </apply_tag><apply_tag id="1">fancy</apply_tag><apply_tag id="2">, </apply_tag><apply_tag id="3">fancy</apply_tag><apply_tag id="4">, text.\n This is </apply_tag><apply_tag id="5">a link</apply_tag><apply_tag id="6">, a\n </apply_tag><apply_tag id="7">fancy, fancy</apply_tag><apply_tag id="8"> link.\n\n </apply_tag><apply_tag id="9">recipe link</apply_tag><apply_tag id="10">\n\n </apply_tag><apply_tag id="11">\xc2\xbc recipe boogoochooboo</apply_tag><apply_tag id="12">\n\n </apply_tag><apply_tag id="13">Yeah!</apply_tag><apply_tag id="14">\n </apply_tag></text>\n</text_view_markup>\n'  # noqa
    expected = 'This is some text\n Some <i>fancy</i>, <u>fancy</u>, text.\n This is <a href="foo">a link</a>, a\n <a href="fancy_desc">fancy, fancy</a> link.\n\n <a href="123:foo">recipe link</a>\n\n <a href="456:boo">¼ recipe boogoochooboo</a>\n\n <b>Yeah!</b>\n '  # noqa

    ret = PangoToHtml().feed(pango_markup, links)
    assert ret == expected

    pango_markup = b'GTKTEXTBUFFERCONTENTS-0001\x00\x00\x01i <text_view_markup>\n <tags>\n  <tag name="italic" priority="1">\n   <attr name="style" type="PangoStyle" value="PANGO_STYLE_ITALIC" />\n  </tag>\n  <tag name="bold" priority="0">\n   <attr name="weight" type="gint" value="700" />\n  </tag>\n </tags>\n<text>ddf<apply_tag name="bold">fd<apply_tag name="italic">df</apply_tag>fd</apply_tag>dff</text>\n</text_view_markup>\n'  # noqa
    expected = 'ddf<b>fd<i>df</i>fd</b>dff'

    ret = PangoToHtml().feed(pango_markup)
    assert ret == expected
