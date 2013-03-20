Whiskers DB model reasoning
===========================

Whiskers DB has four tables:

Host
    Stores information about hosts where buildouts are ran. Stored rows are
    name (host name), ipv4 (ip-address) and relation to buildouts (list of
    buildout ids).

Buildout
    Stores information about buildout.

Package
    Contains information about individual package and its requirements.
    Contains information about the final version and required version.

Version
    Contains version numbers referenced by packages.


Versions
--------

Usually each package has a version number. Version can be specified by several
routes:

 * by another packages requirements (setup.py)
 * by buildout (versions)
 * by not specifying it at all and easy_install picks one for you.

Package version can be specified both setup.py and buildout versions and they
can be different (although only one version is fetched).

Lets assume we have package called dummy which has one requirement to another
package called dummy_requirement version > 0.2 . We have added dummy to our
buildout.cfg:s eggs list and specified there that dummy_requirement version
is pinned to 0.4 and dummy should be version 1.0.

When we run buildout with buildout.sendpickedversions extension we should get
data which tells us that:

 1) Buildout has dummy version 1.0
 2) Buildout has dummy_requirement version 0.4
 3) dummy_requirement is required by dummy package AND
 4) Required version of dummy_requirement package was > 0.2

Whiskers should store all above to DB:
 * Whiskers stores three new rows to the version table containing versions
   0.2, 0.4 and 1.0.
 * Whiskers stores two new packages to packages table (dummy and
   dummy_requirement)
 * dummy_requirement packages should have:
   * version set to 0.4
   * required_by should be list containing dummy packages id
   * required_version 

dummy -> requires dummy_require > 0.2
buildout pins dummy_require = 0.4

Requirement table stores required version, picked version and package name
Package requirements consists list of requirement objects.
