.. doctest docs/usage.rst
.. _atelier.usage:

=====
Usage
=====

Installation
============

Installation is easy::

    pip install atelier



How it works
=============

To install the :mod:`atelier` package you must say::

  $ pip install atelier

.. _invoke: http://www.pyinvoke.org/

Installing :mod:`atelier` also installs the invoke_ package, which installs the
command :cmd:`inv` into your :envvar:`PATH`. When you run :cmd:`inv` (or its
alias :cmd:`invoke`) from a project directory or a subdirectory, then invoke_
reads the :xfile:`tasks.py` in the root directory of your project.

.. command:: inv

The :cmd:`inv` command is a kind of make tool that is configured using
:xfile:`tasks.py` file.

.. xfile:: tasks.py

A configuration file for the invoke_ package. It must define a variable named
``ns``, which must be an instance of an invoke namespace.

To activate atelier for your project, you create a :xfile:`tasks.py` file in
your project's root directory, and define the variable ``ns`` by calling
:func:`atelier.invlib.setup_from_tasks`.

Your :file:`tasks.py` should have at least the following two lines::

  from atelier.invlib import setup_from_tasks
  ns = setup_from_tasks(globals())

You can specify :ref:`project configuration settings <atelier.prjconf>` directly
in your project's :xfile:`tasks.py` file. Example content::

    from atelier.invlib import setup_from_tasks
    ns = setup_from_tasks(globals(), "mypackage",
        tolerate_sphinx_warnings=True,
        revision_control_system='git')

.. xfile:: .invoke.py

You can specify *user-wide* :ref:`project configuration settings
<atelier.prjconf>` in a file named :xfile:`.invoke.py`, which must be in your
home directory.

You can also define *system-wide* default configuration files.  See the `Invoke
documentation <https://docs.pyinvoke.org/en/latest/concepts/configuration.html>`_
for more information.


.. _atelier.config:

The ``config.py`` file
======================

.. xfile:: ~/.atelier/config.py
.. xfile:: ~/_atelier/config.py
.. xfile:: /etc/atelier/config.py

If you have more than one project, then you define the global projects
list in a configuration file named :xfile:`~/.atelier/config.py`,
which contains something like::

  add_project('/home/john/myprojects/p1')
  add_project('/home/john/myprojects/second_project', 'p2')

where the first argument to :func:`add_project <atelier.projects.add_project>`
is the name of a directory that is expected to contain a :xfile:`tasks.py`.

The optional second argument is a **nickname** for that project. If no
nickname is specified, the nickname will be the leaf name of that
directory.

It is allowed but not recommended to have several projects with a same
nickname.

When you have no :xfile:`config.py <~/.atelier/config.py>` file,
Atelier will operate in single project mode: the :xfile:`tasks.py`
causes on the fly creation of a single project descriptor.


Your projects' ``setup.py`` files
=================================

If a project has a :file:`setup.py` file, then atelier uses it.

.. envvar:: SETUP_INFO
.. xfile:: setup.py

The :xfile:`setup.py` file of a Python project can be as simple as
this:

.. literalinclude:: p1/setup.py

But for atelier there are two additional required conventions:

- The :xfile:`setup.py` file must define a name :envvar:`SETUP_INFO`, which must
  be a :class:`dict` containing the keyword arguments to be passed to the
  :func:`setup` function.

- The :xfile:`setup.py` file should call the :func:`setup` function *only if*
  invoked from a command line, i.e. only ``if __name__ == '__main__'``.

So the above minimal :xfile:`setup.py` file becomes:

.. literalinclude:: p2/setup.py

Atelier tries to verify these conditions and raises an exception if
the :xfile:`setup.py` doesn't comply:

>>> from atelier.projects import get_project_from_path
>>> from pathlib import Path
>>> prj = get_project_from_path(Path('docs/p1'))
>>> prj.load_setup_file()  #doctest: +ELLIPSIS
Traceback (most recent call last):
...
Exception: Oops, ...docs/p1/setup.py called sys.exit().
Atelier requires the setup() call to be in a "if __name__ == '__main__':" condition.

>>> prj = get_project_from_path(Path('docs/p3'))
>>> prj.load_setup_file()  #doctest: +ELLIPSIS
Traceback (most recent call last):
...
Exception: Oops, ...docs/p3/setup.py doesn't define a name SETUP_INFO.

>>> prj = get_project_from_path(Path('docs/p2'))
>>> print(prj.SETUP_INFO)
None
>>> prj.load_setup_file()  #doctest: +ELLIPSIS
>>> prj.SETUP_INFO == {'version': '1.0.0', 'name': 'foo'}
True
>>> prj.SETUP_INFO == dict(name="foo", version="1.0.0")
True


Defining shell aliases
======================

Under Linux you can easily define abbreviations for certain commands which you
use often. These are called **shell aliases**.  There are several ways for
defining them, we recommend to write them into your :xfile:`~/.bash_aliases`.

.. xfile:: ~/.bash_aliases

    Conventional name for the file that holds your shell aliases.  See
    `Configuring your login sessions with dot files
    <http://mywiki.wooledge.org/DotFiles>`_.

After editing your :xfile:`~/.bash_aliases` you must open a new terminal in
order to see the changes.


The :cmd:`per_project` command
==============================

Installing the :mod:`atelier` package will add the :cmd:`per_project` command to
your :envvar:`PATH`.

.. program:: per_project

.. command:: per_project

  Usage::

    $ per_project [options] CMD ...

  Run the given shell command ``CMD`` in the root directory of each project.

The projects are processed in the order defined in your
:xfile:`~/.atelier/config.py` file.

Special case: When CMD starts with the word ``git``, then skip all projects
that don't have their :envvar:`revision_control_system` set to ``'git'``.

Options:

.. option:: --showlist, -l

  Print a list of all projects to ``stdout``. Does
  not run any command.

.. option:: --dirty, -d

- Print or process only projects that have a dirty
  git status. i.e. only those which have :envvar:`revision_control_system`
  set to ``'git'`` and which have local modifications.

.. option:: --start PRJNAME, -s PRJNAME

  Start at project ``PRJNAME``. This is useful
  e.g. when you have been running the test suite on all your projects
  and one project failed. After repairing that failure you want to
  continue the started loop without repeating previous test suites
  again.

.. option:: --after PRJNAME, -a PRJNAME

  Start after project PRJNAME (like :option:`--start`, but without the named project).

.. option:: --until PRJNAME

  Stop after project PRJNAME.

.. option:: --reverse

  Loop over the projects in reverse order.

.. option:: --voice

  Speak the result through speakers when terminated.

Note that the first argument that is not an option (i.e. not starting with a
``-``) marks the beginning of the shell command to be executed. Any ``-`` after
that is considered a part of the shell command.  So the following two lines are
*not* equivalent::

  $ per_project inv --help
  $ per_project --help inv

Usage examples::

  $ per_project -l
  $ per_project -ld
  $ per_project inv prep test
  $ per_project git st

See the `Demo projects included with the Developer Guide
<https://dev.lino-framework.org/dev/projects.html>`__ page of the Lino project
for more usage examples.


>>> from atelier.sheller import Sheller
>>> shell = Sheller()
>>> shell('per_project --help')
... #doctest: +REPORT_UDIFF +NORMALIZE_WHITESPACE
usage: per_project [-h] [-v] [--start START] [-a AFTER] [-u UNTIL] [--showlist] [-d] [-r] ...
<BLANKLINE>
Loop over all projects, executing the given shell command in the
root directory of each project.  See
https://atelier.lino-framework.org/usage.html
<BLANKLINE>
<BLANKLINE>
<BLANKLINE>
positional arguments:
  cmd                   The command to run on every project.
<BLANKLINE>
options:
  -h, --help            show this help message and exit
  -v, --voice           Speak the result through speakers when terminated. (default: False)
  --start START, -s START
                        Start from that project, skip those before. (default: -)
  -a AFTER, --after AFTER
                        Start after that project, skip those before. (default: -)
  -u UNTIL, --until UNTIL
                        Only until that project, skip those after. (default: -)
  --showlist, -l        Show list of projects. (default: False)
  -d, --dirty           Process only projects with a dirty git status. (default: False)
  -r, --reverse         Loop in reverse order. (default: False)




Glossary
========

.. glossary::

  demo project

    A functional project that can be run out of the box. Used for learning or
    testing.

    Demo projects are used by the test suite and the Sphinx documentation.  They
    must have been initialized with :cmd:`inv prep` before running :cmd:`inv
    test` or :cmd:`inv bd`.

    The list of demo projects for a given repository is defined by
    :envvar:`demo_projects` in the :xfile:`tasks.py` file.
