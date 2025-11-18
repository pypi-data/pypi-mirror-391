import os
import ctypes
import pytest
from libevdev._clib import Libevdev, UinputDevice
from pathlib import Path
from typing import BinaryIO, Iterable

# Note: these tests test for the correct functioning of the python bindings,
# not of libevdev underneath. Some ranges are hardcoded for simplicity, e.g.
# if properties 1-4 work the others will work too if libevdev works
# correctly


def is_root():
    return os.getuid() == 0


def has_event_devices():
    return list(Path("/dev/input/").glob("event*"))


@pytest.fixture
def local_device() -> Iterable[BinaryIO]:
    try:
        with open("/dev/input/event3", "rb") as fd:
            yield fd
    except FileNotFoundError:
        pytest.skip("/dev/input/event3 not available")


@pytest.fixture
def local_abs_device() -> Iterable[BinaryIO]:
    for device in Path("/dev/input/").glob("event*"):
        with open(device, "rb") as fd:
            dev = Libevdev(fd)
            if dev.has_event("EV_ABS", "ABS_Y"):
                yield fd
                break
    else:
        pytest.skip("No abs device available")


@pytest.fixture
def local_mt_device() -> Iterable[BinaryIO]:
    for device in Path("/dev/input/").glob("event*"):
        with open(device, "rb") as fd:
            dev = Libevdev(fd)
            if dev.num_slots is not None:
                yield fd
                break
    else:
        pytest.skip("No MT device available")


class TestNameConversion:
    def test_type_max(self):
        for t in ["REL", "ABS"]:
            c = Libevdev.event_to_value("EV_{}".format(t), "{}_MAX".format(t))
            max = Libevdev.type_max("EV_{}".format(t))
            assert c == max

    def test_prop_name(self):
        name = Libevdev.property_to_name(0)
        assert name == "INPUT_PROP_POINTER"

        prevname = None
        for i in range(5):
            name = Libevdev.property_to_name(i)
            assert name is not None
            assert name.startswith("INPUT_PROP_")
            assert prevname != name
            prevname = name

    def test_prop_to_name_invalid(self):
        name = Libevdev.property_to_name(-1)
        assert name is None
        name = Libevdev.property_to_name(100)
        assert name is None
        with pytest.raises(ctypes.ArgumentError):
            name = Libevdev.property_to_name("foo")

    def test_prop_to_value(self):
        value = Libevdev.property_to_value("INPUT_PROP_POINTER")
        assert value == 0

        value = Libevdev.property_to_value("INPUT_PROP_DIRECT")
        assert value == 1

    def test_prop_to_value_invalid(self):
        name = Libevdev.property_to_value("foo")
        assert name is None

    def test_type_to_name(self):
        name = Libevdev.event_to_name(1)
        assert name == "EV_KEY"

        prevname = None
        for i in range(5):
            name = Libevdev.event_to_name(i)
            assert name is not None
            assert name.startswith("EV_")
            assert prevname != name
            prevname = name

    def test_type_to_name_invalid(self):
        name = Libevdev.event_to_name(-1)
        assert name is None
        name = Libevdev.event_to_name(100)
        assert name is None
        with pytest.raises(ctypes.ArgumentError):
            name = Libevdev.event_to_name("foo")

    def test_code_to_name(self):
        name = Libevdev.event_to_name(0, 0)
        assert name == "SYN_REPORT"

        name = Libevdev.event_to_name(1, 1)
        assert name == "KEY_ESC"

    def test_code_to_name_invalid(self):
        name = Libevdev.event_to_name(0, 1000)
        assert name is None
        name = Libevdev.event_to_name(0, -1)
        assert name is None
        with pytest.raises(ctypes.ArgumentError):
            name = Libevdev.event_to_name(0, "foo")

    def test_value_to_name(self):
        name = Libevdev.event_to_name(3, 0x37, 0)
        assert name == "MT_TOOL_FINGER"

        name = Libevdev.event_to_name(3, 0x37, 1)
        assert name == "MT_TOOL_PEN"

    def test_value_to_name_invalid(self):
        name = Libevdev.event_to_name(3, 0x37, 1000)
        assert name is None
        name = Libevdev.event_to_name(3, 0x37, -1)
        assert name is None
        with pytest.raises(ctypes.ArgumentError):
            name = Libevdev.event_to_name(0, "foo")

    def test_event_type_to_value(self):
        v = Libevdev.event_to_value("EV_REL")
        assert v == 2

    def test_event_type_to_value_invalid(self):
        v = Libevdev.event_to_value("foo")
        assert v is None
        with pytest.raises(AttributeError):
            v = Libevdev.event_to_value(0)

    def test_event_code_to_value(self):
        v = Libevdev.event_to_value("EV_REL", "REL_Y")
        assert v == 1

        v = Libevdev.event_to_value(0, "SYN_DROPPED")
        assert v == 3

    def test_event_code_to_value_invalid(self):
        v = Libevdev.event_to_value("EV_REL", "KEY_ESC")
        assert v is None

    def test_event_value_to_value(self):
        v = Libevdev.event_to_value("EV_ABS", "ABS_MT_TOOL_TYPE", "MT_TOOL_FINGER")
        assert v == 0

        v = Libevdev.event_to_value("EV_ABS", "ABS_MT_TOOL_TYPE", "MT_TOOL_PEN")
        assert v == 1

    def test_event_value_to_value_invalid(self):
        v = Libevdev.event_to_value("EV_ABS", "ABS_X", "foo")
        assert v is None


class TestLibevdevDevice:
    def test_ctx_init(self):
        dev = Libevdev()
        del dev

    def test_set_get_name(self):
        dev = Libevdev()
        name = dev.name
        assert name == ""

        dev.name = "foo"
        name = dev.name
        assert name == "foo"

        dev.name = None
        name = dev.name
        assert name == ""

    def test_set_get_uniq(self):
        dev = Libevdev()
        uniq = dev.uniq
        assert uniq is None

        dev.uniq = "foo"
        uniq = dev.uniq
        assert uniq == "foo"

        # libevdev issue: phys may be NULL (unlike the name) but we can't
        # set it to NULL. But the conversion code returns None for the empty
        # string, so let's test for that
        dev.uniq = None
        uniq = dev.uniq
        assert uniq is None

    def test_set_get_phys(self):
        dev = Libevdev()
        phys = dev.phys
        assert phys is None

        dev.phys = "foo"
        phys = dev.phys
        assert phys == "foo"

        # libevdev issue: phys may be NULL (unlike the name) but we can't
        # set it to NULL. But the conversion code returns None for the empty
        # string, so let's test for that
        dev.phys = None
        phys = dev.phys
        assert phys is None

    def test_get_driver_version(self):
        dev = Libevdev()
        v = dev.driver_version
        assert v == 0
        # we can't set this, nothing else we can test

    def test_set_get_id(self):
        dev = Libevdev()
        id = dev.id
        assert id["bustype"] == 0
        assert id["vendor"] == 0
        assert id["product"] == 0
        assert id["version"] == 0

        id["bustype"] = 1
        id["vendor"] = 2
        id["product"] = 3
        id["version"] = 4

        dev.id = id
        id = dev.id
        assert id["bustype"] == 1
        assert id["vendor"] == 2
        assert id["product"] == 3
        assert id["version"] == 4

        del id["bustype"]
        del id["vendor"]
        del id["product"]
        id["version"] = 5

        dev.id = id
        id = dev.id
        assert id["bustype"] == 1
        assert id["vendor"] == 2
        assert id["product"] == 3
        assert id["version"] == 5


@pytest.mark.skipif(not is_root(), reason="Test requires root")
class TestRealDevice:
    """
    Tests various things against /dev/input/event3 which is usually the
    keyboard. Requires root rights though.
    """

    def test_set_fd(self, local_device):
        dev = Libevdev()
        dev.fd = local_device
        fd = dev.fd
        assert local_device == fd

        fd2 = open("/dev/input/event3", "rb")
        dev.fd = fd2
        fd = dev.fd
        assert fd == fd2
        fd2.close()

    def test_init_fd(self, local_device):
        dev = Libevdev(local_device)
        fd = dev.fd
        assert local_device == fd

        fd2 = open("/dev/input/event3", "rb")
        dev.fd = fd2
        fd = dev.fd
        assert fd == fd2
        fd2.close()

    def test_ids(self, local_device):
        dev = Libevdev(local_device)
        id = dev.id
        assert id["bustype"] != 0
        assert id["vendor"] != 0
        assert id["product"] != 0
        assert id["version"] != 0

    def test_name(self, local_device):
        dev = Libevdev(local_device)
        name = dev.name
        assert name != ""

    def test_driver_version(self, local_device):
        dev = Libevdev(local_device)
        v = dev.driver_version
        assert v == 0x010001

    def test_set_clock_id(self, local_device):
        dev = Libevdev(local_device)
        try:
            import time

            clock = time.CLOCK_MONOTONIC
        except AttributeError:
            clock = 1
        rc = dev.set_clock_id(clock)
        assert rc == 0

    def test_grab(self, local_device):
        dev = Libevdev(local_device)
        # no exception == success
        dev.grab()
        dev.grab(False)
        dev.grab(True)

    def test_has_event(self, local_device):
        dev = Libevdev(local_device)
        assert dev.has_event("EV_SYN", "SYN_REPORT")

        type_supported = -1
        max_code = -1
        for t in range(1, 5):
            if dev.has_event(t):
                type_supported = t
                max_code = Libevdev.type_max(t)
                if max is None:
                    continue
                break

        assert type_supported > 0

        codes_supported = 0
        for c in range(max_code + 1):
            if dev.has_event(type_supported, c):
                codes_supported += 1

        assert codes_supported > 0

    @pytest.mark.skipif(not not os.getenv("CI"), reason="Skip in CI")
    def test_has_property(self):
        """
        Let's assume at least one event device with at least one property set.
        May cause false negatives.
        """

        props_supported = 0
        for device in Path("/dev/input/").glob("event*"):
            with open(device, "rb") as fd:
                dev = Libevdev(fd)
                for p in range(6):
                    if dev.has_property(p):
                        props_supported += 1
        assert props_supported > 0

    def test_num_slots(self, local_device):
        """
        Let's assume that our device doesn't have slots
        """
        dev = Libevdev(local_device)
        assert dev.num_slots is None


class TestAbsDevice:
    """
    Tests various things against the first device with EV_ABS.
    We're relying on that this device has ABS_Y, this tests against a code
    that's nonzero and is the most common ABS anyway.
    Requires root rights.
    """

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_absinfo(self, local_abs_device):
        dev = Libevdev(local_abs_device)
        a = dev.absinfo("ABS_Y")
        assert a is not None
        assert "minimum" in a
        assert "maximum" in a
        assert "resolution" in a
        assert "fuzz" in a
        assert "flat" in a
        assert "value" in a

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_set_absinfo(self, local_abs_device):
        dev = Libevdev(local_abs_device)
        real_a = dev.absinfo("ABS_Y")
        assert real_a is not None
        a = dev.absinfo("ABS_Y")
        assert a is not None
        a["minimum"] = 100
        a["maximum"] = 200
        a["fuzz"] = 300
        a["flat"] = 400
        a["resolution"] = 500
        a["value"] = 600

        a = dev.absinfo("ABS_Y", new_values=a)
        assert a is not None
        assert a["minimum"] == 100
        assert a["maximum"] == 200
        assert a["fuzz"] == 300
        assert a["flat"] == 400
        assert a["resolution"] == 500
        assert a["value"] == 600

        l2 = Libevdev(local_abs_device)
        a2 = l2.absinfo("ABS_Y")
        assert a2 is not None
        assert a["minimum"] != real_a["minimum"]
        assert a["maximum"] != real_a["maximum"]
        assert a["fuzz"] != real_a["fuzz"]
        assert a["flat"] != real_a["flat"]
        assert a["resolution"] != real_a["resolution"]
        assert a2["value"] == real_a["value"]
        assert a2["minimum"] == real_a["minimum"]
        assert a2["maximum"] == real_a["maximum"]
        assert a2["fuzz"] == real_a["fuzz"]
        assert a2["flat"] == real_a["flat"]
        assert a2["resolution"] == real_a["resolution"]
        assert a2["value"] == real_a["value"]

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_set_absinfo_invalid(self, local_abs_device):
        dev = Libevdev(local_abs_device)
        with pytest.raises(ValueError):
            dev.absinfo("REL_X")

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_set_absinfo_kernel(self, local_abs_device):
        # FIXME: yeah, nah, not testing that on a random device...
        pass

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_get_set_event_value(self, local_abs_device):
        dev = Libevdev(local_abs_device)
        v = dev.event_value("EV_ABS", "ABS_Y")
        assert v is not None
        v = dev.event_value(0x03, 0x01, new_value=300)
        assert v == 300
        v = dev.event_value(0x03, 0x01)
        assert v == 300

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_get_set_event_value_invalid(self, local_abs_device):
        dev = Libevdev(local_abs_device)
        v = dev.event_value("EV_ABS", 0x600)
        assert v is None
        v = dev.event_value(0x03, 0x600, new_value=300)
        assert v is None

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_enable_event_code(self, local_abs_device):
        dev = Libevdev(local_abs_device)

        assert not dev.has_event("EV_REL", "REL_RY")
        dev.enable("EV_REL", "REL_RY")
        assert dev.has_event("EV_REL", "REL_RY")
        dev.disable("EV_REL", "REL_RY")
        assert not dev.has_event("EV_REL", "REL_RY")

        data = {
            "minimum": 100,
            "maximum": 200,
            "value": 300,
            "fuzz": 400,
            "flat": 500,
            "resolution": 600,
        }
        assert not dev.has_event("EV_ABS", "ABS_RY")
        dev.enable("EV_ABS", "ABS_RY", data)
        assert dev.has_event("EV_ABS", "ABS_RY")
        dev.disable("EV_ABS", "ABS_RY")
        assert not dev.has_event("EV_ABS", "ABS_RY")

        data = 1
        assert not dev.has_event("EV_REP", "REP_DELAY")
        dev.enable("EV_REP", "REP_DELAY", data)
        assert dev.has_event("EV_REP", "REP_DELAY")
        dev.disable("EV_REP", "REP_DELAY")
        assert not dev.has_event("EV_REP", "REP_DELAY")

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_enable_property(self, local_abs_device):
        dev = Libevdev(local_abs_device)
        assert not dev.has_property("INPUT_PROP_ACCELEROMETER")
        dev.enable_property("INPUT_PROP_ACCELEROMETER")
        assert dev.has_property("INPUT_PROP_ACCELEROMETER")


@pytest.mark.skipif(not has_event_devices(), reason="Local event devices required")
class TestMTDevice:
    """
    Tests various things against the first MT device found.
    Requires root rights.
    """

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_current_slot(self, local_mt_device):
        dev = Libevdev(local_mt_device)
        assert dev.current_slot is not None and dev.current_slot >= 0

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_slot_value(self, local_mt_device):
        dev = Libevdev(local_mt_device)
        assert dev.current_slot is not None
        a = dev.absinfo("ABS_MT_POSITION_X")
        v = dev.slot_value(dev.current_slot, "ABS_MT_POSITION_X")
        assert a is not None
        assert v is not None
        assert a["minimum"] <= v
        assert a["maximum"] >= v

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_set_slot_value(self, local_mt_device):
        dev = Libevdev(local_mt_device)
        assert dev.current_slot is not None
        v = dev.slot_value(dev.current_slot, "ABS_MT_POSITION_X")
        assert v is not None
        v += 10
        v2 = dev.slot_value(dev.current_slot, "ABS_MT_POSITION_X", v)
        assert v == v2
        v2 = dev.slot_value(dev.current_slot, "ABS_MT_POSITION_X")
        assert v == v2


class TestUinput:
    """
    Tests uinput device creation.
    Requires root rights.
    """

    def is_identical(self, d1: Libevdev, d2: Libevdev):
        ev_max = Libevdev.event_to_value("EV_MAX")
        assert ev_max is not None
        for t in range(ev_max):
            type_max = Libevdev.type_max(t)
            if type_max is None:
                continue
            for c in range(type_max):
                if d1.has_event(t, c) != d2.has_event(t, c):
                    return False
        return True

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_relative(self):
        dev = Libevdev()
        dev.name = "test device"
        dev.enable("EV_REL", "REL_X")
        dev.enable("EV_REL", "REL_Y")
        with UinputDevice(dev) as uinput:
            assert uinput.devnode is not None

            with open(uinput.devnode, "rb") as f:
                newdev = Libevdev(f)
                assert self.is_identical(dev, newdev)

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_button(self):
        dev = Libevdev()
        dev.name = "test device"
        dev.enable("EV_KEY", "BTN_LEFT")
        dev.enable("EV_KEY", "KEY_A")
        with UinputDevice(dev) as uinput:
            assert uinput.devnode is not None

            with open(uinput.devnode, "rb") as f:
                newdev = Libevdev(f)
                assert self.is_identical(dev, newdev)

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_absolute(self):
        absinfo = {"minimum": 0, "maximum": 1}

        dev = Libevdev()
        dev.name = "test device"
        dev.enable("EV_ABS", "ABS_X", absinfo)
        dev.enable("EV_ABS", "ABS_Y", absinfo)
        with UinputDevice(dev) as uinput:
            assert uinput.devnode is not None

            with open(uinput.devnode, "rb") as f:
                newdev = Libevdev(f)
                assert self.is_identical(dev, newdev)

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_device_node(self):
        dev = Libevdev()
        dev.name = "test device"
        dev.enable("EV_REL", "REL_X")
        dev.enable("EV_REL", "REL_Y")
        with UinputDevice(dev) as uinput:
            assert uinput.devnode.startswith("/dev/input/event")

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_syspath(self):
        dev = Libevdev()
        dev.name = "test device"
        dev.enable("EV_REL", "REL_X")
        dev.enable("EV_REL", "REL_Y")
        uinput = UinputDevice(dev)
        assert uinput.syspath.startswith("/sys/devices/virtual/input/input")
