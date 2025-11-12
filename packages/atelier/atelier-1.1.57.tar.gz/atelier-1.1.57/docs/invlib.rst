.. _atelier.invlib:

======================================
``inv`` tasks defined by atelier
======================================

This document describes the :cmd:`inv` tasks provided by :mod:`atelier`
when you import :mod:`atelier.invlib` into your :xfile:`tasks.py` file.


.. contents::
  :local:



Commands for documenting
------------------------

.. command:: inv bd

    Build docs. Build all Sphinx HTML doctrees for this project.

    This runs :cmd:`inv readme`, followed by `sphinx-build html` in
    every directory defined in :envvar:`doc_trees`.  The exact options
    for `sphinx-build` depend also on
    :envvar:`tolerate_sphinx_warnings` and :envvar:`use_dirhtml`.

.. command:: inv pd

    Publish docs. Upload docs to public web server.

.. command:: inv blog

    Edit today's blog entry, create an empty file if it doesn't yet exist.

.. command:: inv readme

    Generate or update `README.txt` or `README.rst` file from
    `SETUP_INFO`.

Commands for internationalization
---------------------------------

.. command:: inv mm

    ("make messages")

    Extracts translatable messages from both code and userdocs, then initializes
    and updates all catalogs. Needs :envvar:`locale_dir` and :envvar:`languages`
    to be set.

Commands for deployment
-----------------------

.. command:: inv ci

    Checkin and push to repository, using today's blog entry as commit
    message.

    Asks confirmation before doing so.

    Does nothing in a project whose
    :envvar:`revision_control_system` is `None`.

    In a project whose :envvar:`revision_control_system` is
    ``'git'`` it checks whether the repository is dirty (i.e. has
    uncommitted changes) and returns without asking confirmation if
    the repo is clean.  Note that unlike ``git status``, this check
    does currently not (yet) check whether my branch is up-to-date
    with 'origin/master'.

.. command:: inv reg

    Register this project (and its current version) to PyPI.

.. command:: inv sdist

    Write a source distribution archive to your :envvar:`sdist_dir`.

.. command:: inv release

    Upload the source distribution archive previously created by
    :cmd:`inv sdist` to PyPI, i.e. publish an official version of your
    package.

    Before doing anything, it shows the status of your local repository (which
    should be clean) and a summary of the project status on PyPI.  It then asks
    a confirmation (unless you specified ``-b`` or ``--batch``).

    The release will fail if the project has previously been published on PyPI
    with the same version.

    If you specified ``-r`` or ``--branch`` (and
    :envvar:`revision_control_system` is ``'git'``), create and push a version
    branch "vX.Y.Z".

    This command requires that `twine
    <https://pypi.python.org/pypi/twine>`_ is installed.


Commands for testing
--------------------

.. command:: inv install

  Install required Python packages to your Python environment and/or to your
  :file:`requirements-install.txt` file.

  This may take some time because it runs :manage:`install` on every demo
  project defined by :envvar:`demo_projects`.

  .. option:: --batch

    Don't ask for confirmations.

  .. option:: --list

    Don't install anything, just list the requirements to `stdout`.


.. command:: inv prep

.. program:: inv prep

Run :cmd:`pm prep` on every :term:`demo project`.

Optionally run additional custom preparation tasks that need to run before
testing.

Both the :cmd:`inv test` and the :cmd:`inv bd` commands assume that :cmd:`inv
prep` has been run successfully, but they don't launch it automatically because
it can take some time and is not always necessary.

See also :envvar:`prep_command` and :envvar:`demo_prep_command`

.. option:: --after NAME

  Run :envvar:`demo_prep_command` only in the demo projects after the named one.

.. option:: --start NAME

  Run :envvar:`demo_prep_command` only in the demo projects starting at the
  named one.

.. option:: --verbose

  Whether to print all output. Default is to print only the names of the demo
  projects that are being prepared.


.. command:: inv test

    Run the test suite of this project.

    This is a shortcut for either ``python setup.py test`` or
    ``py.test`` or `` tox`` (depending on whether your project has a
    :xfile:`pytest.ini` or :xfile:`tox.ini` files or not and  ).


.. command:: inv cov

    Create a `coverage <https://pypi.python.org/pypi/coverage>`_ report.

    You can configure the command to use by setting :envvar:`coverage_command`.

.. command:: inv test_sdist

    Creates and activates a temporay virtualenv, installs your project
    and runs your test suite.

    - creates and activates a temporay virtualenv,
    - calls ``pip install --no-index -f <env.sdist_dir> <prjname>``
    - runs ``python setup.py test``
    - removes temporary files.

    Assumes that you previously did :cmd:`inv sdist` of all your
    projects related to this project.


Miscellaneous commands
----------------------

.. command:: inv clean

    Remove temporary and generated files:

    - Sphinx :file:`.build` files
    - All :file:`__pycache__` directories.
    - additional files specified in :envvar:`cleanable_files`

    Unless option ``--batch`` is specified, ask for an interactive
    user confirmation before removing these files.

.. command:: inv ct

    Display a list of commits in all projects during the last 24
    hours.

.. command:: inv check

    Perform an integrity check for this project. Experimental.

.. command:: inv update-fixtures

  Update fixtures that scrape from external data sources like wikidata.

  Runs the :envvar:`fixtures_updater` function.
