"""Tests unitaires de tempmon (stdlib unittest, aucune dépendance)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tempmon.model import Reading, SensorGroup, Snapshot, Status  # noqa: E402
from tempmon.sensors.hwmon import _classify, _parse_chip  # noqa: E402
from tempmon.sensors.registry import build_provider  # noqa: E402
from tempmon.sensors.simulated import SimulatedProvider  # noqa: E402


class TestStatus(unittest.TestCase):
    def test_normal(self):
        r = Reading("c", 50, warning=80, critical=95)
        self.assertEqual(r.status, Status.NORMAL)

    def test_warning(self):
        r = Reading("c", 82, warning=80, critical=95)
        self.assertEqual(r.status, Status.WARNING)

    def test_critical(self):
        r = Reading("c", 96, warning=80, critical=95)
        self.assertEqual(r.status, Status.CRITICAL)

    def test_unknown_when_none(self):
        r = Reading("c", None, warning=80, critical=95)
        self.assertEqual(r.status, Status.UNKNOWN)


class TestGroupAggregation(unittest.TestCase):
    def test_hottest_and_status(self):
        g = SensorGroup("cpu", "cpu", [
            Reading("a", 40, 80, 95),
            Reading("b", 88, 80, 95),
            Reading("c", 60, 80, 95),
        ])
        self.assertEqual(g.hottest.label, "b")
        self.assertEqual(g.status, Status.WARNING)

    def test_overall_status_priority(self):
        snap = Snapshot(groups=[
            SensorGroup("a", "cpu", [Reading("x", 50, 80, 95)]),
            SensorGroup("b", "gpu", [Reading("y", 99, 80, 95)]),
        ])
        self.assertEqual(snap.overall_status, Status.CRITICAL)


class TestHwmonParsing(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(_classify("coretemp"), "cpu")
        self.assertEqual(_classify("nvme"), "disk")
        self.assertEqual(_classify("amdgpu"), "gpu")
        self.assertEqual(_classify("wtf"), "other")

    def test_parse_chip_from_fake_sysfs(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "name"), "w") as f:
                f.write("coretemp\n")
            with open(os.path.join(d, "temp1_label"), "w") as f:
                f.write("Package\n")
            with open(os.path.join(d, "temp1_input"), "w") as f:
                f.write("54000\n")  # 54.0 °C
            with open(os.path.join(d, "temp1_crit"), "w") as f:
                f.write("100000\n")
            group = _parse_chip(d)
            self.assertIsNotNone(group)
            self.assertEqual(group.kind, "cpu")
            self.assertEqual(group.readings[0].label, "Package")
            self.assertAlmostEqual(group.readings[0].celsius, 54.0)
            self.assertAlmostEqual(group.readings[0].critical, 100.0)


class TestSimulatedProvider(unittest.TestCase):
    def test_produces_groups(self):
        snap = SimulatedProvider(seed=1).read()
        self.assertTrue(snap.groups)
        self.assertEqual(snap.source, "simulated")
        for g in snap.groups:
            for r in g.readings:
                self.assertIsNotNone(r.celsius)


class TestRegistry(unittest.TestCase):
    def test_force_simulated(self):
        p = build_provider("simulated")
        self.assertEqual(p.name, "simulated")

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            build_provider("bogus")

    def test_autodetect_returns_available(self):
        p = build_provider()
        self.assertTrue(p.available())


if __name__ == "__main__":
    unittest.main()
