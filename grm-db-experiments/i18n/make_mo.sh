#!/bin/sh

echo $1
mkdir -p $1/LC_MESSAGES
msgfmt -o $1/LC_MESSAGES/gourmet.mo $1.po
