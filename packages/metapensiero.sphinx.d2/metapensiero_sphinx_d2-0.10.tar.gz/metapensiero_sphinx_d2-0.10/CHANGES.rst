.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sphinx.d2 — Changelog
.. :Created:   mar 13 ago 2024, 11:46:24
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2024, 2025 Lele Gaifax
..

Changes
-------

0.10 (2025-11-14)
~~~~~~~~~~~~~~~~~

* Fix usage of relative paths within diagrams (issue `#2`__)

  __ https://gitlab.com/metapensiero/metapensiero.sphinx.d2/-/issues/2


0.9 (2025-04-01)
~~~~~~~~~~~~~~~~

* Add ``scale`` option


0.8 (2025-02-22)
~~~~~~~~~~~~~~~~

* Add ``dark_theme`` option, thanks to Julien (MR `#1`__)

  __ https://gitlab.com/metapensiero/metapensiero.sphinx.d2/-/merge_requests/1


0.7 (2025-02-09)
~~~~~~~~~~~~~~~~

* Capture ``d2`` output and show it only in case of error


0.6 (2024-11-03)
~~~~~~~~~~~~~~~~

* Do not fail badly when ``d2`` is not found, or exits with an error code: rather, emit a
  warning and skip the diagram's node


0.5 (2024-08-22)
~~~~~~~~~~~~~~~~

* Use relative URIs also for the internal links within the rendered diagram


0.4 (2024-08-21)
~~~~~~~~~~~~~~~~

* Use relative URIs to point to rendered diagrams


0.3 (2024-08-17)
~~~~~~~~~~~~~~~~

* Ignore commented out links

* Absolutize internal reference URIs


0.2 (2024-08-17)
~~~~~~~~~~~~~~~~

* Fix syntax of some f-strings to be compatible with Python <3.12


0.1 (2024-08-16)
~~~~~~~~~~~~~~~~

* Initial work
