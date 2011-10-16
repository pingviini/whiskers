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

Second scenario is that you're using some CI tool to test your buildouts before
deploying them to production servers. We have exact same problem than in the
above example - somehow we need to know what tests our CI server needs to launch
to test every buildout which are affected by our changes in our custom package.

To add some more twist, we might have specific deployment environment (eg. rpm,
deb) and we need to package new releases with our package manager after all
tests pass.

With Whiskers you can...
------------------------

#. Check what is required and where
#. Launch Jenkins builds for all buildouts using specific package

Future
------

Whiskers is not ready. Currently it just stores buildout information. Future
plans involve at least following features:

* Have a buildout history so you can follow what packages have
  been updated, added or removed.
* Launch builds on CI server.


.. _PyPI: http://pypi.python.org/pypi/buildout.sendpickedversions
.. _Github: http://github.com/pingviini/buildout.sendpickedversions
