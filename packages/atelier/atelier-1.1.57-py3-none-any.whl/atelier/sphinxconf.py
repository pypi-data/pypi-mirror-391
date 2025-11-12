# -*- coding: utf-8 -*-
# Copyright 2011-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from pathlib import Path
from rstgen import sphinxconf
from rstgen.utils import srcref_url_template
from rstgen.sphinxconf import interproject
from atelier.projects import get_project_from_path
import atelier
import rstgen


def configure(globals_dict, project=None, **kwargs):

    docs_root = Path(globals_dict['__file__']).parent.absolute()
    if project is None:
        project = get_project_from_path(docs_root.parent)
        if project is None:
            sphinxconf.configure(globals_dict, **kwargs)
            interproject.configure(globals_dict)
            return
    atelier.current_project = project
    project.load_info()

    rstgen.set_config_var(public_url=project.get_public_docs_url('docs'))
    # print("20220710 sphinxconf.configure()", project.get_xconfig('use_dirhtml'))
    rstgen.set_config_var(use_dirhtml=project.get_xconfig('use_dirhtml'))
    rstgen.set_config_var(
        selectable_languages=project.get_xconfig('selectable_languages'))

    sphinxconf.configure(globals_dict, **kwargs)

    globals_dict['html_context'].update(SETUP_INFO=project.SETUP_INFO,
                                        project=project)

    # project.load_info()
    version = project.SETUP_INFO.get('version', None)
    if version:
        globals_dict.update(release=version)
        globals_dict.update(version='.'.join(version.split('.')[:2]))

    if 'name' in project.SETUP_INFO:
        globals_dict['extensions'] += [
            'sphinx.ext.autodoc', 'sphinx.ext.autosummary'
        ]
    # else:
    #     raise Exception(f"No 'name' in SETUP_INFO of {project}")

    if project.main_package:
        root_mod, tpl = srcref_url_template(project.main_package)
        if tpl:
            globals_dict['extlinks'].update(srcref=(tpl, '(source %s)'))

    interproject.configure(globals_dict)
