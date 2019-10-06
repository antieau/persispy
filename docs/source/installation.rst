
How To Get It
=============


To obtain the github repository, run the following code::

    git clone https://github.com/benjaminantieau/persispy


New contributions are via the :ref:`develop <develop>` branch.

Required packages
-----------------

Several of the features depend on certain packages. See :ref:`additional features` for more information.


Installing
==========

At the command line::

    easy_install persispy

Or, if you have virtualenvwrapper installed::

    mkvirtualenv persispy
    pip install persispy
   
Alternatively, we can also use the makefile magic. The makefile also features several useful functions. If you plan on :ref:`contributing <develop>`, it is worth your while to check out these extra functions.::
    
    make help
    make install
    
Installing additional features
-------------------
If you want either plotting or phc functionality, then your system will need

- Plotting from matplotlib requires

    - texlive-latex-extra 
    - libffi-dev
    - libfreetype6-dev

- Polynomial homotopy continuation sampling from PHCpack requires

    - python3-dev
    - gnat 
    - openmpi*

The makefile provides the dependencies with::

    make phc
    make plot


