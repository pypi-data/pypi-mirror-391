.. doctest docs/rstgen.rst

===================================
``rstgen`` : Generating Sphinx docs
===================================

.. currentmodule:: rstgen

rstgen is a library of utilities to programmatically generate chunks of
`reStructuredText <https://docutils.sourceforge.io/rst.html>`__.   It also
contains a series of Sphinx extensions (in the :mod:`rstgen.sphinxconf`
package).  We use it for making the docs for :mod:`atelier`, :mod:`rstgen`,
:mod:`etgen` and :mod:`lino`.

.. contents::
  :local:

>>> from rstgen import *


Headers
=======

.. function:: header(level, text)

Render the `text` as a header with the specified `level`.

It uses and assumes the following system of header levels::

   =======
   Level 1
   =======

   -------
   Level 2
   -------

   ~~~~~~~
   Level 3
   ~~~~~~~

   Level 4
   =======

   Level 5
   -------

   Level 6
   ~~~~~~~



Tables
======

.. function:: table(headers, rows=tuple(), **kw)

Render the given headers and rows as an reStructuredText formatted table.

- `headers` is an iterable of strings, one for each column
- `rows` is an iterable of rows, each row being an iterable of strings.

.. rubric:: Usage examples

Here is the data we are going to render into different tables:

>>> headers = ["Country", "City", "Name"]
>>> rows = []
>>> rows.append(["Belgium", "Eupen", "Gerd"])
>>> rows.append(["Estonia", "Vigala", "Luc"])
>>> rows.append(["St. Vincent and the Grenadines", "Chateaubelair", "Nicole"])

The simplest use case of :func:`table`:

>>> print(table(headers, rows))
================================ =============== ========
 Country                          City            Name
-------------------------------- --------------- --------
 Belgium                          Eupen           Gerd
 Estonia                          Vigala          Luc
 St. Vincent and the Grenadines   Chateaubelair   Nicole
================================ =============== ========
<BLANKLINE>

You can get the same result by using the :class:`Table` class directly:

>>> t = Table(headers)
>>> print(t.to_rst(rows))
================================ =============== ========
 Country                          City            Name
-------------------------------- --------------- --------
 Belgium                          Eupen           Gerd
 Estonia                          Vigala          Luc
 St. Vincent and the Grenadines   Chateaubelair   Nicole
================================ =============== ========
<BLANKLINE>


A table without headers:

>>> print(table(headers, rows, show_headers=False))
================================ =============== ========
 Belgium                          Eupen           Gerd
 Estonia                          Vigala          Luc
 St. Vincent and the Grenadines   Chateaubelair   Nicole
================================ =============== ========
<BLANKLINE>


If there is at least one cell that contains a newline character,
the result will be a complex table:

>>> rows[2][0] = "St. Vincent\nand the Grenadines"
>>> print(table(headers, rows))
+--------------------+---------------+--------+
| Country            | City          | Name   |
+====================+===============+========+
| Belgium            | Eupen         | Gerd   |
+--------------------+---------------+--------+
| Estonia            | Vigala        | Luc    |
+--------------------+---------------+--------+
| St. Vincent        | Chateaubelair | Nicole |
| and the Grenadines |               |        |
+--------------------+---------------+--------+
<BLANKLINE>


.. rubric:: Empty tables

A special case is a table with no rows.  For ``table(headers, [])``
the following output would be logical::

    ========= ====== ======
     Country   City   Name
    --------- ------ ------
    ========= ====== ======

But Sphinx would consider this a malformed table.  That's why we
return a blank line when there are no rows:

>>> print(table(headers, []))
<BLANKLINE>
<BLANKLINE>



Bullet lists
===============

.. function::  ul(items, bullet="-")

    Render the given `items` as a `bullet list
    <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists>`_.

    `items` must be an iterable whose elements are strings.

If at least one item contains more than one paragraph,
then all items are separated by an additional blank line.

>>> print(ul(["Foo", "Bar", "Baz"]))
- Foo
- Bar
- Baz
<BLANKLINE>
>>> print(ul([
...   "Foo", "An item\nwith several lines of text.", "Bar"]))
- Foo
- An item
  with several lines of text.
- Bar
<BLANKLINE>
>>> print(ul([
...   "A first item\nwith several lines of text.",
...   "Another item with a nested paragraph:\n\n  Like this.\n\nWow."]))
<BLANKLINE>
- A first item
  with several lines of text.
<BLANKLINE>
- Another item with a nested paragraph:
<BLANKLINE>
    Like this.
<BLANKLINE>
  Wow.
<BLANKLINE>


Ordered lists
=============

.. function:: ol(items, bullet="#.")

    Render the given `items` as an ordered (numbered) list.

`items` must be an iterable whose elements are strings.

>>> print(ol(["Foo", "Bar", "Baz"]))
#. Foo
#. Bar
#. Baz
<BLANKLINE>
>>> print(ol([
...   "Foo", "An item\nwith several lines of text.", "Bar"]))
#. Foo
#. An item
   with several lines of text.
#. Bar
<BLANKLINE>
>>> print(ol([
...   "A first item\nwith several lines of text.",
...   "Another item with a nested paragraph:\n\n  Like this.\n\nWow."]))
<BLANKLINE>
#. A first item
   with several lines of text.
<BLANKLINE>
#. Another item with a nested paragraph:
<BLANKLINE>
     Like this.
<BLANKLINE>
   Wow.
<BLANKLINE>



Miscellaneous
=============

.. function:: boldheader(title)

  Render the given text as a bold string, prefixed and followed by newlines.

.. function:: attrtable(rows, cols)

  Render the attributes of each object to a table.

  Arguments:

  - rows: an iterator of objects
  - cols: a string with a space-separated list of attribute names


.. function:: toctree(*children, **options)

    Return a `toctree` directive with specified `options` and `children`.

Usage examples:

>>> toctree('a', 'b', 'c', maxdepth=2)
'\n\n.. toctree::\n    :maxdepth: 2\n\n    a\n    b\n    c\n'

>>> toctree('a', 'b', 'c', hidden=True)
'\n\n.. toctree::\n    :hidden:\n\n    a\n    b\n    c\n'



Link to the source code
=======================

The :func:`rstgen.utils.srcref` function is no longer used. The content of this
section is obsolete.

Return the source file name of a Python module, for usage by the
:rst:dir:`srcref` role.

Example:

>>> from rstgen.utils import srcref
>>> import atelier
>>> print(srcref(atelier))  #doctest: +SKIP
https://gitlab.com/lino-framework/atelier/blob/master/atelier/__init__.py

It doesn't need to be the main package:

>>> from atelier.invlib import utils
>>> print(srcref(utils))  #doctest: +SKIP
https://gitlab.com/lino-framework/atelier/blob/master/atelier/invlib/utils.py

The package must have an attribute ``SETUP_INFO``, which must be a `dict`
containing an item ``url`` And :func:`srcref` then assumes that
``SETUP_INFO['url']`` is the base URL of the source repository.

For modules that don't follow this convention, :func:`srcref` returns `None`.

>>> import pathlib
>>> print(srcref(pathlib))
None

Returns `None` if the source file is empty (which happens e.g. for
:file:`__init__.py` files whose only purpose is to mark a package).

Configuration settings
======================

The :mod:`rstgen` module provides the following configuration settings:

.. envvar:: public_url

  The canonical public URL where this website is to be published.

.. envvar:: use_dirhtml

    Whether `sphinx-build
    <http://sphinx-doc.org/invocation.html#invocation-of-sphinx-build>`__
    should use ``dirhtml`` instead of the default ``html`` builder.

.. envvar:: selectable_languages

    A tuple or list of language codes for which there is a doctree.

    It is used to build multilingual websites.  Caution: this is tricky.

    The first specified language is the default language, whose source tree is
    :file:`docs`.  For every remaining language ``xx`` there must be a source
    tree named :file:`xxdocs`. These non-default source trees will be built
    below the default source tree.

    When :envvar:`selectable_languages` is `['en', 'de']` and
    :envvar:`doc_trees` has its default value `['docs']`, then atelier expects
    two Sphinx source trees :file:`docs` and :file:`dedocs`.  The output of
    :file:`docs` will be under the normal location :file:`docs/.build`, but  the
    output of :file:`dedocs` will be under :file:`docs/.build/de`.


.. function:: set_config_var(**kwargs)

.. function:: get_config_var(k)

.. class:: Table

    The object used by :func:`table` when rendering a table.

    .. method:: write(self, fd, data=[])

      Write this table to the specified stream `fd`.

    .. method:: to_rst

      Return this table as a string in reSTructuredText format.



Related work
============

Kevin Horn wrote and maintains a comparable library, also called
`rstgen <https://bitbucket.org/khorn/rstgen/src>`_. (TODO: Check
whether we should join our efforts.)
