Authors: Guo Xu, Dirk Heine, Rufus Pollock, Friedrich Lindenberg

Install
=======

Grab the source using mercurial from http://bitbucket.org/rgrp/openhdi::

    hg clone http://bitbucket.org/rgrp/openhdi

Install the requirements (in a virtualenv)::

    # create a virtualenv
    virtualenv ../pyenv-openhdi
    # install the app requirements
    pip -E ../pyenv-openhdi install -r pip-requirements.txt

Install mongodb (used as the backend).

Run the app::

    python openhdi/app.py

Setup Database
==============
 
Run the following command::

  python openhdi/model.py load

If you want to delete everything (WARNING: irreversible)::

  python openhdi/model.py delete

