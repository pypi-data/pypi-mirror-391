# Copyright 2011-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
See :doc:`/index`.

.. autosummary::
   :toctree:

   invlib
   invlib.utils
   invlib.tasks
   jarbuilder
   projects
   test
   utils
   sheller

"""

__version__ = '1.1.57'

# intersphinx_urls = dict(docs="https://lino-framework.gitlab.io/atelier")
intersphinx_urls = dict(docs="https://atelier.lino-framework.org")
srcref_url = 'https://gitlab.com/lino-framework/atelier/blob/master/%s'
# doc_trees = ['docs']

current_project = None
"""
The currently loaded project.  An instance of
:class:`atelier.Project`.  This is set by :func:`atelier.invlib.setup_from_tasks`.
"""
