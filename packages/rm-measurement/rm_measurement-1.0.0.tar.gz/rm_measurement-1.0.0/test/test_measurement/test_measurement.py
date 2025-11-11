from unittest import TestCase;

from uuid import uuid4;

from src.rm_measurement.measurement import Measurement;
from src.rm_measurement.measurement_types import MeasurementType;
from src.rm_measurement.exceptions import UnequalSequenceLength;

class TestMeasurement(TestCase):

    def setUp(self) -> None:
        pass;

    def tearDown(self) -> None:
        pass;

    def testEnforcesEqualSequenceLength(self):
        with self.assertRaises(UnequalSequenceLength):
            Measurement(uuid4(), MeasurementType.XRD, "angle", "counts", "°", "1", [1,2,3], [4,5]);

