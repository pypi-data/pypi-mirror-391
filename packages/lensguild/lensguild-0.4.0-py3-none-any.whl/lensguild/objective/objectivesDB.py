from __future__ import annotations
from typing import Final, Mapping
from types import MappingProxyType
from allytools.frozen import FrozenDB
from lensguild.objective.objective import Objective
from lensguild.objective.Sunex import *
from lensguild.objective.Commonlands import *

_REGISTRY: dict[str, Objective] = {
    "DSL934_F3_0_NIR": DSL934_F3_0_NIR,
    "DSL934_F4_0_NIR": DSL934_F3_0_NIR,
    "DSL935_F4_8_NIR": DSL935_F4_8_NIR,
    "DSL935_F3_0_NIR": DSL935_F3_0_NIR,
    "CIL052_F3_4_M12BNIR": CIL052_F3_4_M12BNIR,
    "CIL085_F4_4_M12BNIR":CIL085_F4_4_M12BNIR,
}
class ObjectivesDB(metaclass=FrozenDB):
    __slots__ = ()
    DSL934_F3_0_NIR: Final[Objective] = DSL934_F3_0_NIR
    DSL934_F4_0_NIR: Final[Objective] = DSL934_F4_0_NIR
    DSL935_F4_8_NIR:    Final[Objective] = DSL935_F4_8_NIR
    DSL935_F3_0_NIR:    Final[Objective] = DSL935_F3_0_NIR
    CIL052_F3_4_M12BNIR:    Final[Objective] = CIL052_F3_4_M12BNIR
    CIL085_F4_4_M12BNIR: Final[Objective] = CIL085_F4_4_M12BNIR


    REGISTRY: Final[Mapping[str, Objective]] = MappingProxyType(_REGISTRY)

    @classmethod
    def get_objective(cls, name: str) -> Objective:
        try:
            return cls.REGISTRY[name]
        except KeyError as e:
            available = ", ".join(cls.REGISTRY.keys())
            raise KeyError(f"Unknown objective '{name}'. Available: {available}") from e

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(cls.REGISTRY.keys())

__all__ = ["DSL934_F3_0_NIR", "DSL935_F4_8_NIR", "DSL935_F3_0_NIR", "CIL052_F3_4_M12BNIR", "CIL085_F4_4_M12BNIR"]
