######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.8.1+obcheckpoint(0.2.8);ob(v1)                                                    #
# Generated on 2025-11-14T01:56:44.085637                                                            #
######################################################################################################

from __future__ import annotations

import abc
import metaflow
import typing
if typing.TYPE_CHECKING:
    import abc
    import metaflow.plugins.secrets

from . import SecretsProvider as SecretsProvider

class InlineSecretsProvider(metaflow.plugins.secrets.SecretsProvider, metaclass=abc.ABCMeta):
    def get_secret_as_dict(self, secret_id, options = {}, role = None):
        """
        Intended to be used for testing purposes only.
        """
        ...
    ...

