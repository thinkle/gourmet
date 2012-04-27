#!/bin/sh
intltool-update --pot --gettext-package=gourmet
for f in *.po
do
echo Merging new translations into $f
msgmerge -U $f gourmet.pot
done
