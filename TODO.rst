TODO
====

Tasks to do before releasing new version (not priorized in any way):

 * Moar tests.
 * REST API by using Cornice.
 * Optimize SQLite related code.
   ("SQLite is capable of being extremely fast. If you are seeing speeds
   slower than other DB systems such as MySQL or PostGres, then you are
   not utilizing SQLite to its full potential. Optimizing for speed
   appears to be the second priority of D. Richard Hipp, the author and
   maintainer of SQLite. The first is data integrity and verifiability." -
   http://web.utk.edu/~jplyon/sqlite/SQLite_optimization_FAQ.html)
 * Not whiskers related, but still important - support for zc.buildout 2.x in
   buildout.sendpickedversions.
 * Settings for how many buildout versions we store.
 * Buildouts view should show only one buildout version - there's room for
   loading history via some ajaxy magic.
