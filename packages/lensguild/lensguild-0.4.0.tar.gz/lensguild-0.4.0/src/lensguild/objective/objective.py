from enum import Enum
from dataclasses import dataclass,field
from allytools.units import Length, Angle
from lensguild.sensor import SensorFormats
from lensguild.filter import OpticalFilter
from lensguild.objective.model_id import ModelID
from typing import Optional
from pathlib import Path

class ObjectiveBrand(Enum):
    Sunex = 'Sunex'
    Commonlands = 'Commonlands'

@dataclass(frozen=True)
class ObjectiveID(ModelID[ObjectiveBrand]):
    pass


@dataclass(frozen=True)
class Objective:
    objectiveID: ObjectiveID
    EFL: Length
    sensor_format:SensorFormats
    f_number:float
    max_fov:Angle
    max_image_circle:Length
    max_CRA: Angle
    _zmx_file: Optional[Path] = field(default=None, repr=False)
    filter: OpticalFilter | None = None

    def __post_init__(self):
        if not isinstance(self.EFL, Length):
            raise TypeError("EFL must be a Length instance.")
        if not isinstance(self.max_fov, Angle):
            raise TypeError("max_fov must be an Angle instance.")
        if not isinstance(self.max_image_circle, Length):
            raise TypeError("max_image_circle must be a Length instance.")
        if not isinstance(self.max_CRA, Angle):
            raise TypeError("max_CRA must be an Angle instance.")
        if not isinstance(self.sensor_format, SensorFormats):
            raise TypeError("image_format must be a SensorType enum member.")
        if not isinstance(self.f_number, (int, float)) or self.f_number <= 0:
            raise ValueError("f_number must be a positive number.")
        if self.filter is not None and not isinstance(self.filter, OpticalFilter):
            raise TypeError("filter must be an OpticalFilter instance or None.")
        if self._zmx_file is not None and not isinstance(self._zmx_file, Path):
            object.__setattr__(self, "_zmx_file", Path(self._zmx_file))

    @property
    def zmx_file(self) -> Path:
        if self._zmx_file is None:
            raise AttributeError(f"{self!r} zmx_file is  None.")
        return self._zmx_file

    def __str__(self) -> str:
        return (
            f"{self.objectiveID}\n"
            f"  EFL          : {self.EFL}   f/{self.f_number}\n"
            f"  format       : {self.sensor_format}\n"
            f"  max FOV      : {self.max_fov}\n"
            f"  image circle : {self.max_image_circle}\n"
            f"  max CRA      : {self.max_CRA}\n"
            f"  filter       : {self.filter}\n"
            f"  zmx file     : {self._zmx_file}"
        )

    def __repr__(self) -> str:
        return (
            f"Objective(objectiveID={self.objectiveID!r}, EFL={self.EFL!s}, "
            f"image_format={self.sensor_format!s}, f_number={self.f_number!r}, "
            f"max_fov={self.max_fov!s}, max_image_circle={self.max_image_circle!s}, "
            f"max_CRA={self.max_CRA!s}, filter={self.filter!s}, zmx_file={self._zmx_file!s})"
        )
