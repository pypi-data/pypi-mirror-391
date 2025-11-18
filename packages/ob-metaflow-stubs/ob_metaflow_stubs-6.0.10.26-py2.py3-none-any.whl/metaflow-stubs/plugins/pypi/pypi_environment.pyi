######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.8.1+obcheckpoint(0.2.8);ob(v1)                                                    #
# Generated on 2025-11-14T01:56:44.075901                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

