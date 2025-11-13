from dataclasses import dataclass
from typing import Sequence, Tuple
import numpy as np
from allytools.units import Length
from lensguild.sensor.sensor import Sensor


@dataclass(frozen=True, slots=True)
class QuadrantGrid:
    x: np.ndarray  # shape (R, C), float64
    y: np.ndarray  # shape (R, C), float64

    @property
    def shape(self) -> Tuple[int, int]:
        return self.x.shape

    def x_seq(self) -> Sequence[Sequence[float]]:
        """Return x grid as nested Python lists (Sequence[Sequence[float]])."""
        return self.x.tolist()

    def y_seq(self) -> Sequence[Sequence[float]]:
        """Return y grid as nested Python lists (Sequence[Sequence[float]])."""
        return self.y.tolist()


    def to_tuple_grid(self) -> Sequence[Sequence[Tuple[float, float]]]:
        """
        Return an (R, C) object array of (x, y) tuples,
        exposed as a Sequence-of-Sequences of tuples.
        """
        R, C = self.x.shape
        out = np.frompyfunc(lambda a, b: (a, b), 2, 1)(self.x, self.y)
        # Return as Sequence[Sequence[(float, float)]]
        return out.tolist()  # <-- convert ndarray to nested Python lists

    def to_points_rc(self) -> Sequence[Sequence[float]]:
        """
        Return an (R*C, 2) sequence of [x_mm, y_mm] in row-major order.
        Usable as Sequence[Sequence[float]].
        """
        pts = np.column_stack((self.x.ravel(), self.y.ravel()))
        return pts.tolist()  # <-- convert ndarray to list-of-lists


def quadrant_grid(sensor: Sensor, size: int) -> QuadrantGrid:
    """
    Return a QuadrantGrid covering the top-right quadrant measured from the sensor center
    to the top-right corner, using pixel-center spacing.
    y decreases top-to-bottom (as in the original code).
    """
    if size <= 0:
        raise ValueError("size must be a positive integer.")

    # Determine pixel pitch (mm)
    px_mm = None
    if hasattr(sensor.pixel, "length") and isinstance(sensor.pixel.length, Length):
        px_mm = sensor.pixel.length.value_mm
    else:
        px_w = sensor.pixel.width.value_mm if hasattr(sensor.pixel, "width") and isinstance(sensor.pixel.width, Length) else None
        px_h = sensor.pixel.height.value_mm if hasattr(sensor.pixel, "height") and isinstance(sensor.pixel.height, Length) else None
        if px_w is None and px_h is None:
            raise AttributeError("Pixel must have .length or (.width and/or .height) as Length.")
        px_mm = px_w if px_h is None else (px_h if px_w is None else 0.5 * (px_w + px_h))

    mid_x_pix = sensor.width_pix / 2.0
    mid_y_pix = sensor.height_pix / 2.0

    # Distance from sensor center to last pixel center in +X/+Y
    start_x_mm = (mid_x_pix - 0.5) * px_mm
    start_y_mm = (mid_y_pix - 0.5) * px_mm
    end_x_mm   = (sensor.width_pix  - 0.5) * px_mm
    end_y_mm   = (sensor.height_pix - 0.5) * px_mm

    x_centers = np.linspace(start_x_mm, end_x_mm, size, dtype=np.float64)
    y_centers = np.linspace(start_y_mm, end_y_mm, size, dtype=np.float64)[::-1]  # top-to-bottom

    # Shift so origin is at the sensor center (0,0) at the first cell of the quadrant
    x_grid, y_grid = np.meshgrid(x_centers - start_x_mm, y_centers - start_y_mm)

    return QuadrantGrid(x_grid, y_grid)

def tuple_grid_from_sequences(
    x_seq: Sequence[Sequence[float]],
    y_seq: Sequence[Sequence[float]]
) -> np.ndarray:
    """
    Reconstruct an (R, C, 2) NumPy array of float64
    from x_seq() and y_seq() nested lists.
    """
    if len(x_seq) != len(y_seq):
        raise ValueError("Row count mismatch between x_seq and y_seq")

    R = len(x_seq)
    if R == 0:
        return np.empty((0, 0, 2), dtype=np.float64)

    C = len(x_seq[0])

    # Allocate result
    out = np.empty((R, C, 2), dtype=np.float64)

    for r, (row_x, row_y) in enumerate(zip(x_seq, y_seq)):
        if len(row_x) != len(row_y):
            raise ValueError("Column count mismatch between x_seq and y_seq")
        if len(row_x) != C:
            raise ValueError("All rows must have the same length.")
        for c, (a, b) in enumerate(zip(row_x, row_y)):
            out[r, c, 0] = float(a)
            out[r, c, 1] = float(b)

    return out
