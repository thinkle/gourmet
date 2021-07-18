"""This test may leave marks in the user preferences file."""
import os
os.environ['LANGUAGE'] = 'de_DE.utf-8'  # must happend before Gourmet import

from gourmet.gglobals import gourmetdir
from gourmet.plugins.import_export.pdf_plugin.pdf_exporter import PdfPrefGetter  # noqa: import not at top of file

def test_get_args_from_opts(tmp_path):
    gourmetdir = tmp_path
    pref_getter = PdfPrefGetter()

    options = (['Papiergröße:', 'Letter'],
               ['_Ausrichtung:', 'Hochformat'],
               ['_Schriftgröße:', 10],
               ['Seiten-Layout', 'Eben'],
               ['Linker Rand:', 70.86614173228347],
               ['Rechter Rand:', 70.86614173228347],
               ['Oberer Rand:', 70.86614173228347],
               ['Unterer Rand:', 70.86614173228347])

    expected = {'pagesize': 'letter',
				'pagemode': 'portrait',
				'base_font_size': 10,
				'mode': ('column', 1),
				'left_margin': 70.86614173228347,
				'right_margin': 70.86614173228347,
				'top_margin': 70.86614173228347,
				'bottom_margin': 70.86614173228347} 

    ret = pref_getter.get_args_from_opts(options)

    assert ret == expected
