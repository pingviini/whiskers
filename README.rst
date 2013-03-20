========
Whiskers
========

    "Vibrissae (singular: vibrissa), or whiskers, are specialized hairs (or, in
    certain bird species, specialized feathers) usually employed for tactile
    sensation." - Wikipedia

Whiskers is a Pyramid application for storing information about your buildouts.
It is intended to use with buildout.sendpickedversions (PyPI_, Github_)
extension.

.. image:: https://travis-ci.org/pingviini/whiskers.png?branch=master

Reason behind Whiskers
======================

Why? Shortly to automate your workflow.

Think an environment where you're managing tens or hundereds of buildouts - say
Plone instances. Most of them have probably almost the same packages and 
versions. Now you make an critical fix to some custom package and you need to
know which buildouts you have to update. Whiskers helps you here by knowing
what is required and where.

Installation
============

Requirements
------------

Python 2.6, 2.7, 3.2 or 3.3


Pip
---

::

    virtualenv --no-site-packages -p /path/to/python whiskers
    cd whiskers
    bin/pip install whiskers
    wget https://github.com/pingviini/whiskers/raw/master/production.ini
    bin/pserve production.ini

Github
------

::

    virtualenv --no-site-packages -p /path/to/python whiskers
    git clone git://github.com/pingviini/whiskers.git
    cd whiskers
    python setup.py install
    bin/pserve production.ini


Usage
=====

To get some data to Whiskers you should set up buildout.sendpickedversions for
your buildouts. Just add following lines to your buildout.cfg: ::

    [buildout]
    extensions = buildout.sendpickedversions
    send-data-url = http://localhost:6543
    ...

Above configuration assumes you have Whiskers running on localhost.

Run buildout and it should say in last lines something like this: ::

    ...
    root: Sending data to remote url (http://localhost:6543/)
    Added buildout information to Whiskers.

Open web browser and go to http://localhost:6543/buildouts and you should see
your buildout data.


Having trouble
==============

Both Whiskers and buildout.sendpickedversions have been updated to work
nicely together. Make sure you are using latest version of
buildout.sendpickedversions when you've set up Whiskers 1.x.

Older version of buildout.sendpickedversions (0.x) is incompatible with
Whiskers 1.x. Same goes to other way too - Whiskers 0.x doesn't work with
buildout.sendpickedversions 1.x.


Found a bug
===========

Please kill it (or add a new issue to github). Code is out there for you.

Seriously - I'm more than willing accepting new contributions.


.. _PyPI: http://pypi.python.org/pypi/buildout.sendpickedversions
.. _Github: http://github.com/pingviini/buildout.sendpickedversions
