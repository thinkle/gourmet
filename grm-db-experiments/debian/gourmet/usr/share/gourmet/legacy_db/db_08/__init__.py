# Database backend stuff should all be in this directory.
#
# rdatabase is the base class subclassed by different DB backends.
# rmetakit is our stable backend
# rsqlite and rmysql are experimental SQL backends.
#
# PythonicSQL is a base class for experimental glue between SQL and metakit-y object
# oriented DB access.
# pythonic_sqlite and pythonic_mysql are derived classes from PythonicSQL to handle
# interaction with each of these sql variants. Other SQL subclasses should be easy to
# implement.
