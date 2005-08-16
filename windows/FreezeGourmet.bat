:: In this script, you need to replace the first chunk with the location of your FreezePython.exe
:: --target-dir is where your frozen directory will go
:: The last argument C:\Python23\Scripts\Gourmet.pyw, is the script to freeze. This should be installed in
:: scripts/ by python setup.py install

set freezePythonExe="C:\Documents and Settings\tmhinkle\Desktop\cx_Freeze-3.0.1\FreezePython.exe"
set targetdir=C:\Python23\dist
set freezeTarget=C:\Python23\Scripts\Gourmet.pyw

%freezePythonExe% --target-dir=%targetdir% --base-binary=Win32GUI --include-modules=gourmet.defaults_en,gourmet.defaults_en_GB,gourmet.defaults_es,atk,tcl84,tk84,gtk,pango,gtk.glade,encodings,codecs,encodings.utf_8,encodings.string_escape %freezeTarget%