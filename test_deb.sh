echo Run dpkg-buildpackage
sudo dpkg-buildpackage -S -k5DCF5DF9 -IVM -Ifoo -Ipyc -Idist
sudo dpkg-buildpackage -k5DCF5DF9 -IVM -Ifoo -Ipyc -Idist
echo dpkg-buildpackage done
LATEST_DEB=`ls -t ../*.deb | head -1`
echo REMOVE OLD STUFF
sudo rm -rf /usr/share/gourmet/ /usr/local/share/gourmet/ /usr/local/lib/python2.*/*-packages/gourmet/ /usr/lib/python2.*/*-packages/gourmet/ /tmp/foobar
echo Install our new package
sudo dpkg -i $LATEST_DEB
echo 'Test gourmet'
/usr/bin/gourmet --gourmet-directory=/tmp/foobar
