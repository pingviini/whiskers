Whiskers
========

    "Vibrissae (singular: vibrissa), or whiskers, are specialized hairs (or, in
    certain bird species, specialized feathers) usually employed for tactile
    sensation." - Wikipedia

Whiskers is a Pyramid application for storing information about your buildouts.
It is intended to use with buildout.sendpickedversions (PyPI_, Github_)
extension.

Reason behind Whiskers
----------------------

Why? Shortly to automate your workflow.

Think an environment where you're managing tens or hundereds of buildouts - say
Plone instances. Most of them have probably almost same packages and almost same
versions. Now you make an critical fix to some custom package and you need to
know which buildouts you have to update. Whikers helps you here by knowing what
is required and where.

Installation using virtualenv
-----------------------------

::

    virtualenv whiskers --no-site-packages
    cd whiskers
    bin/pip install whiskers
    wget https://github.com/pingviini/whiskers/raw/master/production.ini
    bin/pserve production.ini

Future
------

Whiskers is currently just storing buildout information. Future
plans involve at least following features:

* Have a buildout history so you can follow what packages have
  been updated, added or removed.

.. _PyPI: http://pypi.python.org/pypi/buildout.sendpickedversions
.. _Github: http://github.com/pingviini/buildout.sendpickedversions
