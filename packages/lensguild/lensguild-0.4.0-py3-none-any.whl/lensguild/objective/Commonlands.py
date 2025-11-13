from typing import Final
from pathlib import  Path
from allytools.units.length import LengthUnit, Length
from allytools.units.angle import Angle
from allytools.units.angle_unit import AngleUnit
from allytools.frozen import FrozenDB
from lensguild.sensor import SensorFormats
from .objective import Objective, ObjectiveID, ObjectiveBrand

CIL085_F4_4_M12BNIR: Final[Objective] = Objective(
    objectiveID=ObjectiveID(ObjectiveBrand.Commonlands, "CIL085-F4.4-M12BNIR"),
    EFL=Length(8.2, LengthUnit.MM),
    sensor_format=SensorFormats.S_1_1_8,
    f_number=4.4,
    max_fov=Angle.from_value(57.0, AngleUnit.DEG),
    max_image_circle=Length(8.8, LengthUnit.MM),
    max_CRA=Angle.from_value(10.0, AngleUnit.DEG),
    _zmx_file=Path(r"Catalog\Commanlands\CIL085_F4.4.zmx"),
    filter=None)

CIL052_F3_4_M12BNIR: Final[Objective] = Objective(
    objectiveID=ObjectiveID(ObjectiveBrand.Commonlands, "CIL052-F3.4-M12ANIR"),
    EFL=Length(5.2, LengthUnit.MM),
    sensor_format=SensorFormats.S_1_1_8,
    f_number=3.4,
    max_fov=Angle.from_value(82.0, AngleUnit.DEG),
    max_image_circle=Length(8.9, LengthUnit.MM),
    max_CRA=Angle.from_value(12.0, AngleUnit.DEG),
    _zmx_file=Path(r"Catalog\Commanlands\CIL052_F3.4.zmx"),
    filter=None)

__all__ =["CIL085_F4_4_M12BNIR", "CIL052_F3_4_M12BNIR"]