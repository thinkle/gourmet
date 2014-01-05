import sys

import pdf_exporter_plugin
plugins = [pdf_exporter_plugin.PdfExporterPlugin]

# pypoppler -- the python bindings for our PDF display library,
# which we require for printing -- doesn't work under Windows.
if sys.platform == "win32":
    import print_plugin
    plugins.append(print_plugin.PDFPrintPlugin)