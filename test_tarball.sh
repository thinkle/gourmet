echo Run python setup.py sdist
python setup.py sdist
echo setup.py done
LATEST_TARBALL=`ls -t dist/ | head -1`
TOP_DIR=$PWD
UNTAR_DIR=`python -c "print \"$LATEST_TARBALL\"[0:-7]"`
echo Move to tmp
cd /tmp/
echo Untar our latest package
tar -zxf $TOP_DIR/dist/$LATEST_TARBALL
cd $UNTAR_DIR
echo REMOVE OLD STUFF
sudo rm -rf /usr/share/gourmet/ /usr/lib/python2.5/site-packages/gourmet/ /tmp/foobaz
echo Install our new tarball
sudo python setup.py install
echo 'Testing gourmet'
gourmet -v --gourmet-directory=/tmp/foobaz
