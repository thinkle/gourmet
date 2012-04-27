#!/bin/sh
for f in *.po
do
    lang=`basename $f .po`
    if [ ! -d "$lang/LC_MESSAGES" ]; then
        mkdir $lang && cd $lang
        if [ ! -d "LC_MESSAGES" ]; then
            mkdir LC_MESSAGES && cd LC_MESSAGES
            cd ..
        fi
        cd ..
    fi
    msgfmt -o $lang/LC_MESSAGES/gourmet.mo $f
done
