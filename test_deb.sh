echo Run dpkg-buildpackage
sudo dpkg-buildpackage
echo dpkg-buildpackage done
LATEST_DEB=`ls -t ../*.deb | head -1`
echo REMOVE OLD STUFF
sudo rm -rf /usr/share/gourmet/ /usr/lib/python2.*/site-packages/gourmet/ /tmp/foobar
echo Install our new package
sudo dpkg -i $LATEST_DEB
echo 'Test gourmet'
gourmet --gourmet-directory=/tmp/foobar