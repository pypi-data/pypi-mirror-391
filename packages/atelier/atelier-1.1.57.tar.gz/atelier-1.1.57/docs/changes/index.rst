.. _atelier.changes:

==============================================================
Changes in :mod:`atelier`, :mod:`rstgen` and :mod:`sphinxfeed`
==============================================================

2024-11-24
==========

Fixed a behaviour in :func:`rstgen.sphinxconf.configure` that could cause
`pkg_resources <https://setuptools.pypa.io/en/latest/pkg_resources.html>`__ to
raise :message:`AttributeError: 'PosixPath' object has no attribute
'startswith'`. And :func:`atelier.sphinxconf.configure` now supports getting
called from a :xfile:`conf.py` file that is located outside of any atelier
project.


2024-11-15
==========

:cmd:`inv mm` no longer specifies the version and project name when it runs
:cmd:`pybabel extract`.

2024-09-11
==========

:cmd:`inv sdist` and :cmd:`inv release` both showed a list of published
versions. But the PyPI service "package_releases" has been deprecated for years
and `is now being deactivated
<https://github.com/pypi/warehouse/issues/16642>`__. That's actually okay, we
simply don't show the list of releases any more.

2024-07-20
==========

:cmd:`inv mm` no longer uses the :xfile:`setup.py` file but the ``pybabel``
command-line interface. The `message_extractors` keyword in :xfile:`setup.py` is
now ignored and :cmd:`inv mm` requires a file named
:xfile:`message_extractors.ini`. For background information see the Babel docs
about `Working with Message Catalogs
<https://babel.pocoo.org/en/latest/messages.html>`__.

2024-06-11
==========

:cmd:`inv install` no longer fails when the repository has no
:xfile:`requirements.txt` file.

New command :cmd:`inv pull`  pulls the latest changes, including those from
upstream if there is one. Runs either "git pull" or "git fetch upstream" followed
by "git merge upstream/master".

2024-04-19
==========

Fixed :ticket:`5562` (Sphinx warning "cannot cache unpickable configuration
value"). :func:`rstgen.sphinxconf.configure` now sets
:envvar:`suppress_warnings` to ``['config.cache', 'image.nonlocal_uri']``.

2024-04-16
==========

New command-line option :option:`inv prep --verbose`. For temporary use in book
as part of :ticket:`5542` (Two VAT doctests fail because generated VAT numbers
differ).

2024-03-14
==========

:cmd:`per_project` caused an `argh.assembling.ArgumentNameMappingError` with
newer versions of ``argh`` because there had been `some breaking changes
<https://argh.readthedocs.io/en/latest/changes.html>`__

2023-12-10
==========

New variable :envvar:`default_branch`.

2023-03-14
==========

It is now possible to have a :xfile:`README.rst` that is **not** getting
overwritten by :cmd:`inv bd` (more precisely by by :cmd:`inv readme`, which is
triggered by by :cmd:`inv bd`): when your :setting:`long_description` starts with
``"===="``, then :cmd:`inv readme` won't care about overwriting your
:xfile:`README.rst`.

2023-01-15
==========

New function :func:`rstgen.sphinxconf.sigal_image.parse_image_spec` will be used
also by the [image] memo command in Lino.

2022-12-25
==========

.. program:: inv prep

When specifying :option:`--start` or :option:`--after` to the :cmd:`inv prep`
command, you must now give only the last part of the project name. Instead of
saying ``inv prep -a lino_book.projects.cosi5`` you must now
say ``inv prep -a cosi5``.

2022-12-24
==========

The :rst:dir:`sigal_image` directive has a new format "tiny".

2022-12-10
==========

:func:`atelier.invlib.tasks.run_in_demo_projects`, when called with `bare=True`,
(inconsistently) returned `None` when there were no demo projects.


2022-10-30
==========

Release to pypi: :mod:`rstgen`.

2022-10-19
==========

The :cmd:`inv test` command now calls doctest with
``REPORT_ONLY_FIRST_FAILURE``.

2022-10-10
==========

Fixed a bug that caused PosixPath has no attribute 'format'

Release to pypi

2022-09-18
==========

:envvar:`test_command`:  now runs :cmd:`python -m unittest discover -s tests`
only when a directory named :file:`tests` exists. Because under certain
circumstances (Python 3.10?) :cmd:`unittest discover` also searches the whole
:envvar:`PYTHONPATH` for a package named ``tests`` and that's not what we want
to happen.

2022-08-17
==========

Release to PyPI: atelier

2022-08-10
==========

.. program:: inv prep

The :cmd:`inv prep` command now accepts a new option :option:`--after`.


2022-07-26
==========

Fix :message:`NameError("name 'lng' is not defined")`

Release to PyPI: :mod:`rstgen`

2022-07-14
==========

The :cmd:`inv prep` command now runs less verbosely. It prints the output of
each subprocess only when it failed.
The :cmd:`inv install` command has a new command line interface.

2022-07-10
==========

New attribute :attr:`atelier.projects.Project.published` and a method
:meth:`atelier.projects.Project.set_published`.

Fixed :ticket:`4558` (sphinxfeed links don't work when use_dirhtml is true).
This also required changes in our branch of :mod:`sphinxfeed`, which now depends
on :mod:`rstgen`.

:rst:dir:`sigal_image` now uses height 10em instead of width 30% for specifying
the size of thumbnail images.


2022-06-09
==========

Miscellaneous bugfixes and optimizations after `2022-05-24`_

Released atelier and rstgen to PyPI.


2022-05-24
==========

Move some utility functions from :mod:`atelier.utils` to :mod:`rstgen.utils`
(because we don't want :manage:`makehelp` on a Lino production site to depend on
atelier):
:func:`dict_py2 <rstgen.utils.dict_py2>`,
:func:`list_py2 <rstgen.utils.list_py2>`,
:func:`tuple_py2 <rstgen.utils.tuple_py2>`,
:func:`rmu <rstgen.utils.rmu>`
and :func:`sixprint <rstgen.utils.sixprint>`

Release to PyPI.

Also move :mod:`atelier.sphinxconf` to :mod:`rstgen.sphinxconf`.

Release to PyPI.


2022-04-18
==========

Add a new button template :file:`languages-button.html` for insipid theme.

Release to PyPI.


2022-03-14
==========

Try a quick workaround for supporting language 'et' by modifying
:attr:`docutils.languages.LanguageImporter.packages` (didn't work).

Release to PyPI.


2022-03-13
==========

The :rst:dir:`sigal_image` directive with format ``thumb`` now sets the width of
the image to "30%" instead of "280pt". Because "280pt" didn't yield a good
result on a mobile device.

2022-02-08
==========

Bugfix: The :rst:role:`count` didn't restart at 1 for each new document.

2022-01-26
==========

New role :rst:role:`count`.

Removed the link to source code of a module in the autodoc API (because in
Sphinx 4.4 it caused warnings like  ...lino/lino/__init__.py:docstring of
lino:25: WARNING: hardcoded link '.../master/lino/__init__.py' could be replaced
by an extlink (try using ':srcref:`lino/__init__.py`' instead) )

Release to PyPI : atelier 1.1.41


2021-11-09
==========

The :rst:dir:`refstothis` directive now supports multiple targets.

2021-11-02
==========

New config setting :envvar:`multiple_blog_entries_per_day`.

New config setting :envvar:`rsync_command`.

2021-08-31
==========

The :cmd:`inv pd` command now uses the `--omit-dir-times` option of rsync.

2021-07-21
==========

Added a new command :cmd:`inv update-fixtures` and a new config key
:envvar:`fixtures_updater`.

2021-07-15
==========

Added an option ``--batch`` for :cmd:`inv release`.

2021-06-21
==========

Added two new flags on :cmd:`inv install` of the form :cmd:`inv install --list`
(which installs the required python packages and also list and writes them into
:file:`requirements-install.txt`) and :cmd:`inv install --list-only` (the later
is self explanatory).


2021-06-05
==========

Release to PyPI : atelier 1.1.40

2021-06-04
==========

Fixed a misbehaviour that caused atelier to fail with Sphinx 4: avoid extlinks
with an empty url template.


2021-06-02
==========

Bugfix: :meth:`atelier.projects.Project.get_xconfig`: ignored the hard-coded
default values for projects with a main_module  that was installed from PyPI
(i.e. without a :xfile:`tasks.py` file).

Release to PyPI: atelier 1.1.39


2021-05-29
==========

:func:`rstgen.sphinxconf.configure` no longer imposes a hard-coded theme.  When
you set :data:`html_theme` before calling :func:`configure
<rstgen.sphinxconf.configure>`, then it fills default values to
:data:`html_theme_options` for four themes (insipid, alabaster, pydata and rtd).
The default value is insipid.

2021-05-28
==========

Fix a packaging issue that caused sphinx build warnings "html_static_path entry
'.../site-packages/atelier/sphinxconf/static' does not exist" when atelier was
not installed from source code.

Release to PyPI: atelier 1.1.38


2021-05-21
==========

Miscellaneous changes since 2021-05-03 regarding the documentation framework.
Add dependency to gitpython. See git history for details.

The :func:`rstgen.sphinxconf.configure` now adds the 'sphinx.ext.autodoc' and
'sphinx.ext.autosummary' extensions only when the project's :envvar:`SETUP_INFO`
contains a 'name' key. It's a good thing to avoid loading autodoc when it is not
needed, but this didn't fix my problem.

Release to PyPI: atelier 1.1.37

2021-05-03
==========

Release to PyPI: atelier 1.1.36

2021-05-01
==========

The :cmd:`per_project` command is now packaged using ``entry_points`` (no longer
using ``scripts``). One advantage is that it doesn't break when atelier is
installed from a clone using :cmd:`pip install -e` and the version number
changes. The ``srcref_url`` is no longer used.

Release to PyPI: atelier 1.1.35

Fix failure when `public_url` is unknown.


2021-04-28
==========

Oops, the templates were not included in the 1.1.32 and 1.1.33 pip packages.

Release to PyPI: atelier 1.1.33 and 1.1.34


2021-04-27
==========

New project setting :envvar:`make_docs_command`.

Release to PyPI: atelier 1.1.32


2021-04-25
==========

Calling :func:`rstgen.sphinxconf.configure` in a Sphinx :xfile:`conf.py` file
now also supports usage of :envvar:`selectable_languages`, and the insipid theme
is now activated.

Release to PyPI: atelier 1.1.31


2021-04-25
==========

When :envvar:`selectable_languages` is given, :cmd:`inv bd` will now
automatically loop over the source directories. Removed the configuration
setting :envvar:`build_docs_command` because it is no longer needed.

The :cmd:`inv check` command now detects more inconsistencies.


2021-04-23
==========

Release to pypi: atelier 1.1.30.

2021-04-12
==========

Calling :func:`rstgen.sphinxconf.configure`  in a Sphinx :xfile:`conf.py` file
now also adds the project's :data:`SETUP_INFO` to the :attr:`html_context`.

2021-04-07
==========

Calling :func:`rstgen.sphinxconf.configure` in a Sphinx :xfile:`conf.py` file
now also sets :attr:`atelier.current_project`. New project config option
:envvar:`selectable_languages`. Miscellaneous internal optimizations. New
experiemental command :cmd:`inv check` to detect certain types of configuration
errors.

2021-03-18
==========

Bugfix: After creating a new blog entry with :cmd:`inv blog`, it didn't touch
the year index file. Note that you still need to manually touch the file that
contains your :rst:dir:`blogger_latest` directive in order to have the new blog
entry get listed there.

2021-03-11
==========

Added a new directive :rst:dir:`blogger_latest` in
:mod:`rstgen.sphinxconf.blog`.

Moved from GitHub to GitLab. New project home page is
https://gitlab.com/lino-framework/atelier

Release version 1.1.29 to PyPI.

2021-03-07
==========

Fixed `AttributeError: 'PosixPath' object has no attribute 'set_times'`.


2021-03-06
==========

:func:`atelier.test.make_docs_suite` now supports multiple exclude patterns.

:mod:`rstgen` now also uses :mod:`pathlib` instead of :mod:`unipath`.


2021-03-03
==========

New configuration setting :envvar:`build_docs_command`.
New directive :rst:dir:`cards`.
Change unipath to pathlib.  Remove unipath dependency.
Improve support for long language codes.

Release version 1.1.28 to PyPI.


2021-01-18
==========

New command-line option `--dirty` for :cmd:`per_project` to show only projects
with a dirty git status.

The :cmd:`inv clean` command no longer asks for every individual `.pyc` file,
just one :message:`OK to remove <count> __pycache__ directories?`


.. toctree::
   :maxdepth: 2

   old
