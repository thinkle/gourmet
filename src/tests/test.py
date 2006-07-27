# Convenience for importing gourmet stuff from our local directory...
import os.path, sys

base_path = os.path.split(__file__)[0]


sys.path.append(
    os.path.realpath(

    os.path.join(base_path,
                 os.path.join('..','lib')
                 )
    )
    )


