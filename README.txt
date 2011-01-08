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

Loading data
============
 
python openhdi/importer.py indicator data/indicator.csv
python openhdi/importer.py dataset data/datasets.csv

