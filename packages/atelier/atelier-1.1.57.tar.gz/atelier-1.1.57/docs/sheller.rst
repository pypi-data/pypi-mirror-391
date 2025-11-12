===========
The Sheller
===========

>>> from atelier.sheller import Sheller
>>> shell = Sheller('.')
>>> shell('inv prep --foo')
No idea what '--foo' is!

>>> shell('inv prep')
<BLANKLINE>

If there were :envvar:`demo_projects` defined, :cmd:`inv prep` would output::

  Run `manage.py prep --noinput --traceback` in X demo projects: DONE
