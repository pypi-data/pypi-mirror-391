.. _atelier.prjconf:

==============================
Project configuration settings
==============================

The following settings are available in your :xfile:`tasks.py` when it uses
:mod:`atelier.invlib`.

Code examples in this document use the atelier project

>>> from atelier.projects import get_project_from_module
>>> prj = get_project_from_module('atelier')


.. obsolete:
    'help_texts_source': None,
    'help_texts_module': None,
    'apidoc_exclude_pathnames': [],
    'blog_root': root_dir / 'docs',
    'long_date_format': "%Y%m%d (%A, %d %B %Y)",

Blogging
========

.. envvar:: blog_root

  The doctree where :cmd:`inv blog` should create blog entries.

  Default value is ``root_dir / 'docs'``.

.. envvar:: multiple_blog_entries_per_day

  Whether blog entries are named :file:`yyyy/mmdd.rst` (default) or
  :file:`yyyy/mmdd_HHMM.rst` (support multiple blog entries per day).


General
=======

.. envvar:: project_name

  The nickname to use for this project.

  Default value is `str(root_dir.name)`

.. envvar:: editor_command

    A string with the command name of your text editor. Example::

      editor_command = "emacsclient -n {0}"

    The ``{0}`` will be replaced by the filename.

    Used by :cmd:`inv blog`.

    Note that this must be a *non waiting* command, i.e. which
    launches the editor on the specified file in a new window and then
    returns control to the command line without waiting for that new
    window to terminate.




Internationalization
====================

.. envvar:: locale_dir

    The name of the directory where :cmd:`inv mm` et al should write their
    catalog files.

Deploy
======

.. envvar:: sdist_dir

    The template for the local directory where :cmd:`inv sdist` should
    store the packages.  Any string ``{prj}`` in this template will be
    replaced by the projects Python name.  The resulting string is
    passed as the `--dist-dir` option to the :cmd:`setup.py sdist`
    command.

.. envvar:: pypi_dir

    Where to store temporary files for :cmd:`inv dist`.

    Default value is ``root_dir / '.pypi_cache'``.


Settings for rstgen
===================

The atelier config also forwards the rstgen settings :envvar:`use_dirhtml`,
:envvar:`selectable_languages` and :envvar:`public_url`.


Miscellaneous
=============

.. envvar:: build_dir_name

  Where :cmd:`inv bd` should store the generated html files.

  Default value is ``'.build'``, but e.g. ablog needs ``'_build'``.


.. envvar:: docs_rsync_dest

    A Python template string that defines the rsync destination for
    publishing your projects documentation.

    Used by :cmd:`inv pd`.

    Example::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/{prj}_{docs}'

    The ``{prj}`` in this template will be replaced by the internal
    name of this project, and ``{{docs}}`` by the name of the doctree
    (taken from :envvar:`doc_trees`).

    For backward compatibility the following (deprecated) template is
    also still allowed::

      env.docs_rsync_dest = 'luc@example.org:~/public_html/%s'

    The ``%s`` in this template will be replaced by a name `xxx_yyy`,
    where `xxx` is the internal name of this project and `yyy` the
    name of the doctree (taken from :envvar:`doc_trees`).

.. envvar:: rsync_command

    The Python template for the command to run for uploading a build doctree to
    the :envvar:`docs_rsync_dest`).

    Used by :cmd:`inv pd`.

    Default value::

        rsync_command = "rsync -e ssh -r --verbose --progress --delete "
            "--times --omit-dir-times --exclude .doctrees ./ {dest_url}")

    Where ``{dest_url}`` is the value of :envvar:`docs_rsync_dest`.

.. envvar:: srcref_url

    The URL template to use for :rst:role:`srcref` roles.

    If the project has a main package which has an attribute
    :envvar:`srcref_url`, then this value will be used.

.. envvar:: intersphinx_urls

    A dict which maps doctree names to the URL where they are published.
    This is used when this project's documentation is added to a
    doctree using :mod:`rstgen.sphinxconf.interproject`.

    If the project has a main package which defines an attribute
    :envvar:`intersphinx_urls`,
    then this will override any value define in :xfile:`tasks.py`.

.. envvar:: doc_trees

    A list of directory names (relative to your project directory)
    containing Sphinx document trees.

    Default value is ``['docs']``

    >>> prj.get_xconfig('doc_trees')
    ['docs']

    If the project has a main package which defines an attribute
    :envvar:`doc_trees`,
    then this will override any value define in :xfile:`tasks.py`.

.. envvar:: cleanable_files

    A list of wildcards to be cleaned by :cmd:`inv clean`.

.. envvar:: tolerate_sphinx_warnings

    Whether `sphinx-build` should tolerate warnings.

.. envvar:: languages

    A list of language codes for which gettext translations and userdocs are
    being maintained.  Used by:cmd:`inv mm`.

.. envvar:: revision_control_system

    The revision control system used by your project.  Allowed values
    are `'git'`, `'hg'` or `None`.  Used by :cmd:`inv ci`, :cmd:`inv
    release`, :cmd:`per_project`.

.. envvar:: default_branch

  The name of the default branch. This is "master" by default (`source
  <https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell>`__). But
  GitHub replaced "master" with "main" in October 2020 in order to "remove
  unnecessary references to slavery and replace them with more inclusive terms."
  (`source
  <https://www.zdnet.com/article/github-to-replace-master-with-main-starting-next-month>`__).

  For newer GitHub repositories you must set this to ``main`` in your
  :xfile:`tasks.py`. The variable is currently used only by the
  :xfile:`show-source.html` template.


.. envvar:: use_mercurial

    **No longer used.** Use :envvar:`revision_control_system` instead.)


.. envvar:: demo_projects

    The list of :term:`demo projects <demo project>` defined in this repository.

    Every item of this list is the full Python path of a package that must have
    a :xfile:`manage.py` file.

.. envvar:: prep_command

    A shell command to be run in in the project's root directory when :cmd:`inv
    prep` is invoked.  The default value is empty.

    Default value is empty.

    >>> prj.get_xconfig('prep_command')
    ''

.. envvar:: demo_prep_command

    The shell command to be run in every :envvar:`demo project <demo_projects>`
    when :cmd:`inv prep` is invoked.

    The default value is ``manage.py prep --noinput --traceback``, that is, it
    runs :cmd:`pm prep`.

    >>> prj.get_xconfig('demo_prep_command')
    'manage.py prep --noinput --traceback'

.. envvar:: test_command

    The command to be run by :cmd:`inv test`.

    Default value runs :cmd:`python -m unittest discover -s tests` (unless there
    is no directory named :file:`tests`, in which case it does nothing):

    >>> prj.get_xconfig('test_command')
    'if [ -d tests ]; then python -m unittest discover -s tests; fi'

    The command will always be invoked from the projects root dir.

.. envvar:: make_docs_command

  An optional command to run when :cmd:`inv bd` is invoked.  It can be used for
  generating :file:`.rst` files even before :cmd:`sphinx-build` is run.

  Default value is an empty string.


.. envvar:: build_docs_command

  Removed since 20210425. The command to run by :cmd:`inv bd`.

  Default value is an empty string.

  If this is empty, the default behaviour is to run sphinx-build in each
  :envvar:`doc_trees`.

.. envvar:: coverage_command

    The command to be run under coverage by :cmd:`inv cov`.

    Default value runs :cmd:`inv prep`, then :cmd:`inv test` then :cmd:`inv clean -b`
    and finally :cmd:`inv bd`.

    >>> prj.get_xconfig('coverage_command')
    '`which invoke` prep test clean --batch bd'

.. envvar:: fixtures_updater

    A callable that will be called when you say :cmd:`inv update-fixtures`.
