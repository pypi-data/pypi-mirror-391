# -*- coding: utf-8 -*-
# fmt: off
import datetime
import atelier

from atelier.sphinxconf import configure ; configure(globals())
from rstgen.sphinxconf import configure ; configure(globals())
# from rstgen.sphinxconf.interproject import configure ; configure(globals())

extensions += ['rstgen.sphinxconf.complex_tables']
extensions += ['sphinx.ext.autosummary']


# General information about the project.
project = "atelier"
copyright = '2002-{} Rumma & Ko Ltd'.format(datetime.date.today().year)
html_title = project

# 20210501 extlinks.update(srcref=(atelier.srcref_url, ''))

# The full version, including alpha/beta/rc tags.
#~ release = file(os.path.join(os.path.dirname(__file__),'..','VERSION')).read().strip()
release = atelier.__version__

# The short X.Y version.
version = '.'.join(release.split('.')[:2])
#~ version = lino.__version__

#~ print version, release

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#~ html_logo = 'logo.jpg'
#~ html_logo = 'lino-logo-2.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#~ html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['.static']

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#~ html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {
#    '**': ['globaltoc.html', 'searchbox.html', 'links.html'],
# }

#
# extlinks = {
#   #~ 'issue': ('http://code.google.com/p/lino/issues/detail?id=%s', 'Issue '),
#   # 'checkin': ('http://code.google.com/p/python-atelier/source/detail?r=%s', 'Checkin '),
#   'srcref': (atelier.srcref_url, ''),
#   'djangoticket': ('http://code.djangoproject.com/ticket/%s', 'Django ticket #'),
# }
#
#
# autosummary_generate = True
#
# todo_include_todos = True
#
# #~ New in version 1.1
# gettext_compact = True
#
#
extlinks.update(ticket=('https://jane.mylino.net/#/api/tickets/AllTickets/%s',
                        '#%s'))
extlinks.update(srcref=(atelier.srcref_url, None))

#
# suppress_warnings = ['image.nonlocal_uri']
#
#
# from rstgen.sphinxconf import interproject
# interproject.configure(
#     globals(), "etgen rstgen",
#     django=('https://docs.djangoproject.com/en/5.2/', 'https://docs.djangoproject.com/en/dev/_objects/'),
#     sphinx=('https://www.sphinx-doc.org/en/master/', None))

intersphinx_mapping['sphinx'] = ('https://www.sphinx-doc.org/en/master/', None)
