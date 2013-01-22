========
Whiskers
========

    "Vibrissae (singular: vibrissa), or whiskers, are specialized hairs (or, in
    certain bird species, specialized feathers) usually employed for tactile
    sensation." - Wikipedia

Whiskers is a Pyramid application for storing information about your buildouts.
It is intended to use with buildout.sendpickedversions (PyPI_, Github_)
extension.

.. image:: https://travis-ci.org/pingviini/whiskers.png?branch=refactor

Reason behind Whiskers
======================

Why? Shortly to automate your workflow.

Think an environment where you're managing tens or hundereds of buildouts - say
Plone instances. Most of them have probably almost same packages and almost same
versions. Now you make an critical fix to some custom package and you need to
know which buildouts you have to update. Whikers helps you here by knowing what
is required and where.

Installation
============

Whiskers 1.x is developed with Python 3.3 and tested with Python 3.2.
If you are for some reason tied to Python 2.x you can still use Whiskers 0.2.

Pip
---

::

    virtualenv --no-site-packages -p /path/to/python3.3
    cd whiskers
    bin/pip install whiskers
    wget https://github.com/pingviini/whiskers/raw/master/production.ini
    bin/pserve production.ini

Github
------

::
    virtualenv --no-site-packages -p /path/to/python3.3 whiskers
    git clone git://github.com/pingviini/whiskers.git
    cd whiskers
    python setup.py install
    bin/pserve production.ini


.. _PyPI: http://pypi.python.org/pypi/buildout.sendpickedversions
.. _Github: http://github.com/pingviini/buildout.sendpickedversions
