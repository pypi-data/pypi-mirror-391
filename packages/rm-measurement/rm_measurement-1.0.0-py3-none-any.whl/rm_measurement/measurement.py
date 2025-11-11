from dataclasses import dataclass;
from typing import Sequence;
from uuid import UUID;

from .measurement_types import MeasurementType;
from .exceptions import UnequalSequenceLength;


@dataclass(frozen=True)
class Measurement:
    id: UUID
    measurement_type: MeasurementType
    x_property: str
    y_property: str
    x_unit: str
    y_unit: str
    x_values: Sequence[float]
    y_values: Sequence[float]

    def __post_init__(self):
        self._check_equal_sequence_length();

    def _check_equal_sequence_length(self):
        if len(self.x_values) != len(self.y_values):
            raise UnequalSequenceLength("The x and y values must share the same length");

