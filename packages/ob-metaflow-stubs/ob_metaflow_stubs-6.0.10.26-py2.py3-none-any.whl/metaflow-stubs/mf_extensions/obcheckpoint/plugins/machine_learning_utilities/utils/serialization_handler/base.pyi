######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.8.1+obcheckpoint(0.2.8);ob(v1)                                                    #
# Generated on 2025-11-14T01:56:44.163007                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing


class SerializationHandler(object, metaclass=type):
    def serialze(self, *args, **kwargs) -> typing.Union[str, bytes]:
        ...
    def deserialize(self, *args, **kwargs) -> typing.Any:
        ...
    ...

