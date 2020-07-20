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
