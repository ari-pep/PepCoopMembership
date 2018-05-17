.. _setup_and_requirements:

----------------------
Setup and Requirements
----------------------

To fetch the sources, you need **git**.
::

   apt-get install git-core
   git clone git@github.com:C3S/c3sMembership.git
   cd c3sMembership

Set up a virtual Python environment,
then install c3sMembership for development and fetch the dependencies.
::

   apt-get install python-virtualenv python-pip build-essential python-dev
   apt-get install libxml2-dev libxslt1-dev
   # python-virtualenv: for virtualenv
   # python-pip: for pip
   # build-essential & python-dev: build stuff, e.g. crypto
   # libxml2-dev libxslt1-dev: xml manupulation (internal)

   # and if you want to generate pdfs with pdflatex (very useful :-)) :
   aptitude install texlive-latex-base texlive-latex-recommended texlive-lang-german \
       texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-xetex
   # oh my god... 235 MB of archives will be downloaded, setup 'costs' 693 MB
   # NOTE: you have to set paper size during configuration: we use A4

   virtualenv env
   env/bin/python setup.py develop
   # this will take a little while.
   # if it does not finish successfully, check network & try again.



----------------------
Run during Development
----------------------


While developing the app, you should always run the app locally,
as Pyramid has excellent functionality facilitating development.
You can run the app in *reload* mode,
so whenever you change code the app is restarted, reloading the code.
It will imediately halt when errors are introduced.
::

    env/bin/pserve development.ini --reload
    Starting server in PID 21338.
    serving on http://0.0.0.0:6543
    /home/christoph/Code/c3sMembership/c3smembership/invite_members.py changed; reloading...
    -------------------- Restarting --------------------
    Starting server in PID 21459.
    serving on http://0.0.0.0:6543

Just visit the URL given with a browser to see the apps HTML frontend.

Check settings in *development.ini* for further settings,
e.g. reload of templates, debugging, etc.

Deployment is done with Apache2 and mod_wsgi, see :ref:`sec_deployment`.

