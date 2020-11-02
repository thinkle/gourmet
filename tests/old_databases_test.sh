cp -R old_databases /tmp/old_databases
for folder in /tmp/old_databases/*
do
    echo Testing Gourmet\'s update from $folder
    gourmet --gourmet-directory=$folder
    echo Done with test.
done
rm -r /tmp/old_databases
