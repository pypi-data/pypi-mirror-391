.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.sphinx.d2 — Sphinx d2lang extension
.. :Created:   sab 10 ago 2024, 16:40:34
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2024, 2025 Lele Gaifax
..

========================
 metapensiero.sphinx.d2
========================

Sphinx d2lang extension
=======================

This is a very simple extension to Sphinx__ that implements a ``d2`` directive to draw diagrams using d2__.

__ http://www.sphinx-doc.org/
__ https://d2lang.com/

To use it, first of all you must register the extension within the Sphinx environment, adding
the full name of the package to the ``extensions`` list in the file ``conf.py``, for example::

  # Add any Sphinx extension module names here, as strings.
  extensions = ['metapensiero.sphinx.d2']

You can optionally define the following default settings:

d2_center
  Default value for the ``:center:`` option

d2_class
  Default ``CSS`` *class* of the diagram, when producing ``HTML``

d2_dark_theme
  Default value for the ``:dark_theme:`` option

d2_format
  Default value for the ``:format:`` option

d2_layout
  Default value for the ``:layout:`` option

d2_pad
  Default value for the ``:pad:`` option

d2_redirect_links_to_blank_page
  Default value for the ``:redirect_links_to_blank_page:`` option

d2_scale
  Default value for the ``:scale:`` option

d2_sketch
  Default value for the ``:sketch:`` option

d2_theme
  Default value for the ``:theme:`` option

At that point you can place ``d2`` directives in your documents. The ``d2`` script can be
specified either inline, as the content of the directive, or as a file, relative to the
document itself. The directive accepts the following options:

align
  the alignment of the generated image

alt
  the alternative textual description explaining the diagram

caption
  a short description of the diagram

center
  a boolean value, whether the diagram should be horizontally centered or not

class
  the ``CSS`` classes of the diagram

dark_theme
  an integer, the dark theme to be used

format
  the output format, by default ``svg``, but it can alternatively set to ``png``

layout
  the algorithm used to layout the diagram, either ``dagre`` (the default) or ``elk``

pad
  an integer number of pixels, by default 100

redirect_links_to_blank_page
  when generating ``SVG``, this forces all *local* ``link`` to be opened in a different browser tab

scale
  a float number, the relative scale to be used

sketch
  a boolean value, whether to enable the *sketch* mode

theme
  an integer, the theme to be used

width
  an integer value, the width of the containing ``figure``

Directive-specific options have higher priority on default settings.

.. note:: Boolean options such as ``center`` accept an optional argument: when it is missing, or
          when its lower case value is either ``1``, ``true``, ``yes``, ``on`` then the result
          is ``True``, otherwise ``False``.

.. hint:: The ``d2`` syntax allows specifying arbitrary `external links`__ to any object, that
          works when you render the diagram as ``SVG``: you can also use the usual Sphinx
          reference syntax too, provided that the ``link`` option is on its own line, such as::

            .. d2::

               x: I'm something {
                 link: :ref:`something`
               }

          The following does **not** currently work::

            .. d2::

               x: I'm something { link: :ref:`something` }

          __ https://d2lang.com/tour/interactive/#links

See ``example/index.rst`` for some usage examples.
