#!/bin/sh
sudo cp dist/gourmet-$1.tar.gz /usr/src/rpm/SOURCES/
sudo rpm -ba rpm/gourmet.fedora.spec