# Copyright © 2017 Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import pytest

import libevdev
from libevdev import InvalidFileError, InvalidArgumentException


def is_root() -> bool:
    return os.getuid() == 0


class TestDevice:
    def test_device_empty(self):
        d = libevdev.Device()
        id = {"bustype": 0, "vendor": 0, "product": 0, "version": 0}
        syns = {libevdev.EV_SYN: libevdev.EV_SYN.codes}

        assert d.name == ""
        assert d.id == id
        assert d.fd is None
        assert d.phys is None
        assert d.uniq is None
        assert d.driver_version == 0
        assert d.syspath is None
        assert d.devnode is None
        assert d.evbits == syns
        assert d.properties == []

        for t in libevdev.types:
            if t == libevdev.EV_SYN:
                continue

            assert not d.has(t)

            for c in t.codes:
                assert not d.has(c)
                assert d.value[c] is None
                d.disable(c)  # noop
            d.disable(t)  # noop

        for p in libevdev.props:
            assert not d.has_property(p)

        assert d.num_slots is None
        assert d.current_slot is None

        for c in libevdev.EV_ABS.codes:
            assert d.absinfo[c] is None

        assert [e for e in d.events()] == []
        assert [e for e in d.sync()] == []

        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_ABS.ABS_MT_POSITION_X]

    def test_device_name(self):
        d = libevdev.Device()
        d.name = "test device"
        assert d.name == "test device"

    def test_device_id(self):
        d = libevdev.Device()
        id = {"bustype": 1, "vendor": 2, "product": 3, "version": 4}
        d.id = id
        assert d.id == id

        d.id = {"vendor": 3, "product": 4, "version": 5}
        id = {"bustype": 1, "vendor": 3, "product": 4, "version": 5}
        assert d.id == id

        d.id = {"bustype": 8, "product": 5, "version": 6}
        id = {"bustype": 8, "vendor": 3, "product": 5, "version": 6}
        assert d.id == id

        d.id = {"bustype": 8, "vendor": 9, "version": 10}
        id = {"bustype": 8, "vendor": 9, "product": 5, "version": 10}
        assert d.id == id

        d.id = {"bustype": 8, "vendor": 9, "product": 12}
        id = {"bustype": 8, "vendor": 9, "product": 12, "version": 10}
        assert d.id == id

    def test_device_phys(self):
        d = libevdev.Device()
        d.phys = "foo"
        assert d.phys == "foo"

        d.phys = None
        assert d.phys is None

    def test_device_uniq(self):
        d = libevdev.Device()
        d.uniq = "bar"
        assert d.uniq == "bar"

        d.uniq = None
        assert d.uniq is None

    def test_driver_version(self):
        d = libevdev.Device()
        # read-only
        with pytest.raises(AttributeError):
            d.driver_version = 1

    def test_garbage_fd(self):
        with pytest.raises(InvalidFileError):
            libevdev.Device(fd=1)

        with pytest.raises(InvalidFileError):
            d = libevdev.Device()
            d.fd = 2

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_fd_on_init(self):
        fd = open("/dev/input/event0", "rb")
        d = libevdev.Device(fd)
        assert d.fd == fd

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_fd_too_late(self):
        fd = open("/dev/input/event0", "rb")
        d = libevdev.Device()
        with pytest.raises(InvalidFileError):
            d.fd = fd

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_fd_change(self):
        fd1 = open("/dev/input/event0", "rb")
        fd2 = open("/dev/input/event1", "rb")
        d = libevdev.Device(fd1)
        assert d.fd == fd1
        d.fd = fd2
        assert d.fd == fd2

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_has_bits(self):
        fd = open("/dev/input/event0", "rb")
        d = libevdev.Device(fd)
        bits = d.evbits

        # assume at least 2 event types
        assert len(bits.keys()) > 1

        for t, cs in bits.items():
            if t == libevdev.EV_SYN:
                continue

            # assume at least one code
            assert len(cs) > 0

    def test_set_bits(self):
        d = libevdev.Device()
        # read-only
        with pytest.raises(AttributeError):
            d.evbits = {}

    def test_bits_change_after_enable(self):
        d = libevdev.Device()
        bits = d.evbits
        assert libevdev.EV_SYN in bits
        assert libevdev.EV_REL not in bits

        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)

        bits = d.evbits
        assert libevdev.EV_SYN in bits
        assert libevdev.EV_REL in bits
        assert libevdev.EV_ABS not in bits
        assert libevdev.EV_KEY not in bits

        assert libevdev.EV_REL.REL_X in bits[libevdev.EV_REL]
        assert libevdev.EV_REL.REL_Y in bits[libevdev.EV_REL]

    def test_bits_change_after_disable(self):
        d = libevdev.Device()
        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)
        d.enable(libevdev.EV_KEY.KEY_A)
        d.enable(libevdev.EV_KEY.KEY_B)

        bits = d.evbits
        assert libevdev.EV_SYN in bits
        assert libevdev.EV_REL in bits
        assert libevdev.EV_KEY in bits
        assert libevdev.EV_ABS not in bits
        assert libevdev.EV_REL.REL_X in bits[libevdev.EV_REL]
        assert libevdev.EV_REL.REL_Y in bits[libevdev.EV_REL]
        assert libevdev.EV_KEY.KEY_A in bits[libevdev.EV_KEY]
        assert libevdev.EV_KEY.KEY_B in bits[libevdev.EV_KEY]

        d.disable(libevdev.EV_REL.REL_Y)
        d.disable(libevdev.EV_KEY)
        bits = d.evbits
        assert libevdev.EV_KEY not in bits
        assert libevdev.EV_REL in bits
        assert libevdev.EV_REL.REL_X in bits[libevdev.EV_REL]
        assert libevdev.EV_REL.REL_Y not in bits[libevdev.EV_REL]

    def test_properties(self):
        d = libevdev.Device()
        assert d.properties == []
        for p in libevdev.props:
            assert not d.has_property(p)

        props = sorted([libevdev.INPUT_PROP_BUTTONPAD, libevdev.INPUT_PROP_DIRECT])

        for p in props:
            d.enable(p)

        assert d.properties == props
        for p in libevdev.props:
            if p not in props:
                assert not d.has_property(p)
            else:
                assert d.has_property(p)

        with pytest.raises(NotImplementedError):
            d.disable(libevdev.INPUT_PROP_BUTTONPAD)

    def test_has(self):
        d = libevdev.Device()

        d.enable(libevdev.EV_REL.REL_X)
        d.enable(libevdev.EV_REL.REL_Y)
        d.enable(libevdev.EV_KEY.KEY_A)
        d.enable(libevdev.EV_KEY.KEY_B)

        assert d.has(libevdev.EV_REL)
        assert d.has(libevdev.EV_REL.REL_X)
        assert d.has(libevdev.EV_REL.REL_Y)
        assert not d.has(libevdev.EV_REL.REL_Z)

        assert d.has(libevdev.EV_KEY)
        assert d.has(libevdev.EV_KEY.KEY_A)
        assert d.has(libevdev.EV_KEY.KEY_B)
        assert not d.has(libevdev.EV_KEY.KEY_C)

        assert not d.has(libevdev.EV_ABS)

    def test_enable_abs(self):
        d = libevdev.Device()
        with pytest.raises(InvalidArgumentException):
            d.enable(libevdev.EV_ABS.ABS_X)

    def test_value(self):
        d = libevdev.Device()
        d.enable(libevdev.EV_REL.REL_X)
        assert d.value[libevdev.EV_REL.REL_X] == 0
        assert d.value[libevdev.EV_REL.REL_Y] is None

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_mt_value(self):
        # Unable to set ABS_MT_SLOT on a libevdev device, see
        # https://bugs.freedesktop.org/show_bug.cgi?id=104270
        d = libevdev.Device()
        a = libevdev.InputAbsInfo(minimum=0, maximum=100)
        d.name = "test device"
        d.enable(libevdev.EV_ABS.ABS_X, a)
        d.enable(libevdev.EV_ABS.ABS_Y, a)
        d.enable(
            libevdev.EV_ABS.ABS_MT_SLOT, libevdev.InputAbsInfo(minimum=0, maximum=30)
        )
        d.enable(libevdev.EV_ABS.ABS_MT_POSITION_X, a)
        d.enable(libevdev.EV_ABS.ABS_MT_POSITION_Y, a)
        d.enable(libevdev.EV_ABS.ABS_MT_TRACKING_ID, a)

        uinput = d.create_uinput_device()

        fd = open(uinput.devnode, "rb")
        d = libevdev.Device(fd)

        assert d.num_slots == 31
        assert d.value[libevdev.EV_ABS.ABS_X] == 0
        assert d.value[libevdev.EV_ABS.ABS_Y] == 0

        with pytest.raises(libevdev.InvalidArgumentException):
            d.value[libevdev.EV_ABS.ABS_MT_POSITION_X]
        with pytest.raises(libevdev.InvalidArgumentException):
            d.value[libevdev.EV_ABS.ABS_MT_POSITION_Y]
        with pytest.raises(libevdev.InvalidArgumentException):
            d.value[libevdev.EV_ABS.ABS_MT_SLOT]
        with pytest.raises(libevdev.InvalidArgumentException):
            d.value[libevdev.EV_ABS.ABS_MT_TRACKING_ID]
        # also raises for non-existing axes
        with pytest.raises(libevdev.InvalidArgumentException):
            d.value[libevdev.EV_ABS.ABS_MT_ORIENTATION]

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_slot_value(self):
        # Unable to set ABS_MT_SLOT on a libevdev device, see
        # https://bugs.freedesktop.org/show_bug.cgi?id=104270
        d = libevdev.Device()
        a = libevdev.InputAbsInfo(minimum=0, maximum=100)
        d.name = "test device"
        d.enable(libevdev.EV_ABS.ABS_X, a)
        d.enable(libevdev.EV_ABS.ABS_Y, a)
        d.enable(
            libevdev.EV_ABS.ABS_MT_SLOT, libevdev.InputAbsInfo(minimum=0, maximum=30)
        )
        d.enable(libevdev.EV_ABS.ABS_MT_POSITION_X, a)
        d.enable(libevdev.EV_ABS.ABS_MT_POSITION_Y, a)
        d.enable(libevdev.EV_ABS.ABS_MT_TRACKING_ID, a)

        uinput = d.create_uinput_device()
        events = [
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_SLOT, 0),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_TRACKING_ID, 1),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_POSITION_X, 100),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_POSITION_Y, 110),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_SLOT, 1),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_TRACKING_ID, 2),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_POSITION_X, 200),
            libevdev.InputEvent(libevdev.EV_ABS.ABS_MT_POSITION_Y, 210),
            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0),
        ]
        uinput.send_events(events)

        fd = open(uinput.devnode, "rb")
        d = libevdev.Device(fd)

        assert d.slots[0][libevdev.EV_ABS.ABS_MT_POSITION_X] == 100
        assert d.slots[1][libevdev.EV_ABS.ABS_MT_POSITION_X] == 200
        assert d.slots[0][libevdev.EV_ABS.ABS_MT_POSITION_Y] == 110
        assert d.slots[1][libevdev.EV_ABS.ABS_MT_POSITION_Y] == 210

        assert d.slots[0][libevdev.EV_ABS.ABS_MT_ORIENTATION] is None

        for idx, s in enumerate(d.slots[:2]):
            idx += 1
            assert s[libevdev.EV_ABS.ABS_MT_POSITION_X] == idx * 100
            assert s[libevdev.EV_ABS.ABS_MT_POSITION_Y] == idx * 100 + 10

        for s in d.slots[2:]:
            assert s[libevdev.EV_ABS.ABS_MT_POSITION_X] == 0
            assert s[libevdev.EV_ABS.ABS_MT_POSITION_Y] == 0

        with pytest.raises(IndexError):
            d.slots[200]

        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_ABS.ABS_X]
        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_ABS.ABS_MT_SLOT]
        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_REL.REL_X]
        with pytest.raises(AttributeError):
            d.slots[0][libevdev.EV_ABS]

        d.slots[0][libevdev.EV_ABS.ABS_MT_POSITION_X] = 10
        assert d.slots[0][libevdev.EV_ABS.ABS_MT_POSITION_X] == 10
        d.slots[1][libevdev.EV_ABS.ABS_MT_POSITION_Y] = 50
        assert d.slots[1][libevdev.EV_ABS.ABS_MT_POSITION_Y] == 50

        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_ABS.ABS_MT_ORIENTATION] = 50
        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_ABS.ABS_X] = 10
        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_ABS.ABS_MT_SLOT] = 10
        with pytest.raises(libevdev.InvalidArgumentException):
            d.slots[0][libevdev.EV_REL.REL_X] = 10
        with pytest.raises(AttributeError):
            d.slots[0][libevdev.EV_ABS] = 10

    def test_absinfo(self):
        d = libevdev.Device()
        a = libevdev.InputAbsInfo(minimum=100, maximum=1000, resolution=50)
        d.enable(libevdev.EV_ABS.ABS_X, a)
        # we expect these to be filled in
        a.fuzz = 0
        a.flat = 0
        a.value = 0

        a2 = d.absinfo[libevdev.EV_ABS.ABS_X]
        assert a == a2

        assert d.absinfo[libevdev.EV_ABS.ABS_Y] is None
        a.fuzz = 10
        d.absinfo[libevdev.EV_ABS.ABS_X] = a
        a2 = d.absinfo[libevdev.EV_ABS.ABS_X]
        assert a == a2

        a = libevdev.InputAbsInfo(minimum=500)
        d.absinfo[libevdev.EV_ABS.ABS_X] = a
        a2 = d.absinfo[libevdev.EV_ABS.ABS_X]
        assert a.minimum == a2.minimum
        assert a2.minimum is not None
        assert a2.maximum is not None
        assert a2.fuzz is not None
        assert a2.flat is not None
        assert a2.resolution is not None
        assert a2.value is not None

    def test_absinfo_set_invalid(self):
        a = libevdev.InputAbsInfo(minimum=500)
        d = libevdev.Device()
        with pytest.raises(InvalidArgumentException):
            d.absinfo[libevdev.EV_ABS.ABS_Y] = a
        with pytest.raises(AssertionError):
            d.absinfo[libevdev.EV_REL.REL_X]
        with pytest.raises(AssertionError):
            d.absinfo[libevdev.EV_REL.REL_X] = a

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_absinfo_sync_kernel(self):
        d = libevdev.Device()
        d.name = "sync test device"
        a = libevdev.InputAbsInfo(
            minimum=0, maximum=1000, resolution=50, fuzz=0, flat=0, value=0
        )
        d.enable(libevdev.EV_ABS.ABS_X, a)
        d.enable(libevdev.EV_ABS.ABS_Y, a)
        uinput = d.create_uinput_device()

        fd = open(uinput.devnode, "rb")
        d = libevdev.Device(fd)
        a2 = d.absinfo[libevdev.EV_ABS.ABS_X]
        assert a == a2
        a2.resolution = 100
        d.absinfo[libevdev.EV_ABS.ABS_X] = a2
        d.sync_absinfo_to_kernel(libevdev.EV_ABS.ABS_X)
        fd.close()

        fd = open(uinput.devnode, "rb")
        d = libevdev.Device(fd)
        a3 = d.absinfo[libevdev.EV_ABS.ABS_X]
        print(a3)
        assert a2 == a3
        a3 = d.absinfo[libevdev.EV_ABS.ABS_Y]
        assert a == a3

    @pytest.mark.skipif(not is_root(), reason="Test requires root")
    def test_uinput_empty(self):
        d = libevdev.Device()
        with pytest.raises(OSError):
            d.create_uinput_device()
