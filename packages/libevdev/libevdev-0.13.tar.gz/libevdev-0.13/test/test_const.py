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

import pytest

import libevdev
from libevdev import evbit, propbit
from libevdev.const import EventType, EventCode, InputProperty


class TestEventBits:
    def test_ev_types(self):
        assert libevdev.EV_SYN in libevdev.types
        assert libevdev.EV_REL in libevdev.types
        assert libevdev.EV_ABS in libevdev.types
        assert len(libevdev.types) == 13

    def test_EV_REL(self):
        assert libevdev.EV_REL.REL_X in libevdev.EV_REL.codes
        assert libevdev.EV_REL.REL_Y in libevdev.EV_REL.codes
        assert libevdev.EV_ABS.ABS_X not in libevdev.EV_REL.codes

    def test_type_max(self):
        assert libevdev.EV_REL.max == libevdev.EV_REL.REL_MAX.value
        assert libevdev.EV_ABS.max == libevdev.EV_ABS.ABS_MAX.value
        assert libevdev.EV_KEY.max == libevdev.EV_KEY.KEY_MAX.value

        assert libevdev.EV_REL.max == 0x0F
        assert libevdev.EV_ABS.max == 0x3F
        assert libevdev.EV_KEY.max == 0x2FF

    def test_evcode_compare(self):
        assert libevdev.EV_REL.REL_X != libevdev.EV_REL.REL_Y
        assert libevdev.EV_REL.REL_X != libevdev.EV_ABS.ABS_X
        assert libevdev.EV_REL != libevdev.EV_ABS

        assert libevdev.EV_REL.REL_X != libevdev.EV_REL
        assert libevdev.EV_ABS.ABS_X != libevdev.EV_ABS

    def test_int_conversion(self):
        assert int(libevdev.EV_REL.REL_X) == 0
        assert int(libevdev.EV_KEY.KEY_ESC) == 1
        assert int(libevdev.EV_KEY) == 0x1
        assert int(libevdev.INPUT_PROP_SEMI_MT) == 3

    def test_evbit(self):
        assert evbit(0, 0) == libevdev.EV_SYN.SYN_REPORT
        assert evbit(1, 30) == libevdev.EV_KEY.KEY_A
        assert evbit(2, 1) == libevdev.EV_REL.REL_Y

        assert evbit(0) == libevdev.EV_SYN
        assert evbit(1) == libevdev.EV_KEY
        assert evbit(2) == libevdev.EV_REL

        for t in libevdev.types:
            assert evbit(t.value) == t

    def test_direct_name(self):
        """
        libevdev.EV_FOO.FOO_BAR == libevdev.FOO_BAR
        """
        for ty in libevdev.types:
            for code in filter(lambda c: c.is_defined, ty.codes):
                assert getattr(libevdev, code.name) == code

    def test_propbit(self):
        assert propbit(0) == libevdev.INPUT_PROP_POINTER
        assert propbit(1) == libevdev.INPUT_PROP_DIRECT

        for p in libevdev.props:
            assert propbit(p.value) == p

    def test_evbit_string(self):
        assert evbit("EV_SYN") == libevdev.EV_SYN
        assert evbit("EV_KEY") == libevdev.EV_KEY
        assert evbit("EV_REL") == libevdev.EV_REL
        assert evbit("EV_REP") == libevdev.EV_REP

        for t in libevdev.types:
            assert evbit(t.name) == t

    def test_evcode_string(self):
        assert evbit("ABS_X") == libevdev.ABS_X
        assert evbit("REL_X") == libevdev.REL_X
        assert evbit("SYN_REPORT") == libevdev.SYN_REPORT
        assert evbit("REP_PERIOD") == libevdev.REP_PERIOD

    def test_evcode_is_defined(self):
        for t in libevdev.types:
            for c in t.codes:
                fake_name = "{}_{:02X}".format(t.name[3:], c.value)
                if c.is_defined:
                    assert c.name != fake_name
                else:
                    assert c.name == fake_name

    def test_evcode_undefined(self):
        assert evbit("SYN_04") == libevdev.EV_SYN._SYN_04
        assert libevdev.EV_SYN._SYN_04.name == "SYN_04"

    def test_propbit_string(self):
        assert propbit("INPUT_PROP_POINTER") == libevdev.INPUT_PROP_POINTER
        assert propbit("INPUT_PROP_DIRECT") == libevdev.INPUT_PROP_DIRECT

        for p in libevdev.props:
            assert propbit(p.value) == p

    def test_repr(self):
        assert str(libevdev.EV_REL) == "EV_REL:2"

    def test_less_than(self):
        assert libevdev.EV_REL < libevdev.EV_ABS

    def test_hashables(self):
        d = {}
        d[libevdev.ABS_Z] = True  # same numeric value as EV_REL
        d[libevdev.EV_ABS] = True
        d[libevdev.EV_REL] = True
        d[libevdev.INPUT_PROP_SEMI_MT] = True  # same numeric value as EV_ABS
        assert len(d) == 4


class TestEventType:
    def test_from_value_valid_types(self):
        """Test from_value() with all valid event type values"""
        assert EventType.from_value(0) == libevdev.EV_SYN
        assert EventType.from_value(1) == libevdev.EV_KEY
        assert EventType.from_value(2) == libevdev.EV_REL
        assert EventType.from_value(3) == libevdev.EV_ABS

    @pytest.mark.parametrize("evtype", [t for t in libevdev.types])
    def test_from_value_all_types(self, evtype):
        """Test from_value() returns correct type for all known types"""
        result = EventType.from_value(evtype.value)
        assert result is not None
        assert result == evtype
        assert result.value == evtype.value
        assert result.name == evtype.name

    @pytest.mark.parametrize("value", [8, 13, 14, 50, 255, 1000, -5, -100])
    def test_from_value_invalid(self, value):
        """Test from_value() with various invalid values"""
        assert EventType.from_value(value) is None

    def test_from_name_valid_names(self):
        """Test from_name() with valid event type names"""
        assert EventType.from_name("EV_SYN") == libevdev.EV_SYN
        assert EventType.from_name("EV_KEY") == libevdev.EV_KEY
        assert EventType.from_name("EV_REL") == libevdev.EV_REL
        assert EventType.from_name("EV_ABS") == libevdev.EV_ABS
        assert EventType.from_name("EV_MSC") == libevdev.EV_MSC

    @pytest.mark.parametrize("evtype", [t for t in libevdev.types])
    def test_from_name_all_types(self, evtype):
        """Test from_name() returns correct type for all known types"""
        result = EventType.from_name(evtype.name)
        assert result is not None
        assert result == evtype
        assert result.value == evtype.value
        assert result.name == evtype.name

    @pytest.mark.parametrize(
        "name",
        [
            "INVALID",
            "EV_INVALID",
            "",
            "ev_syn",  # lowercase
            "EV_SYN ",  # trailing space
            " EV_SYN",  # leading space
            "REL_X",  # event code name, not type name
            "INPUT_PROP_POINTER",  # property name
            "ABS",  # missing prefix
            "REL",  # missing prefix
        ],
    )
    def test_from_name_invalid_parametrized(self, name):
        """Test from_name() with various invalid names"""
        assert EventType.from_name(name) is None

    def test_from_value_and_from_name_consistency(self):
        """Test that from_value() and from_name() return the same objects"""
        for evtype in libevdev.types:
            from_value = EventType.from_value(evtype.value)
            from_name = EventType.from_name(evtype.name)
            assert from_value == from_name
            assert from_value is from_name  # should be same object reference


class TestEventCode:
    def test_from_name_valid_codes(self):
        """Test from_name() with valid event code names"""
        assert EventCode.from_name("ABS_X") == libevdev.ABS_X
        assert EventCode.from_name("REL_X") == libevdev.REL_X
        assert EventCode.from_name("REL_Y") == libevdev.REL_Y
        assert EventCode.from_name("KEY_A") == libevdev.KEY_A
        assert EventCode.from_name("KEY_ESC") == libevdev.KEY_ESC
        assert EventCode.from_name("SYN_REPORT") == libevdev.SYN_REPORT

    def test_from_name_all_defined_codes(self):
        """Test from_name() for all defined event codes"""
        for evtype in libevdev.types:
            for code in filter(lambda c: c.is_defined, evtype.codes):
                result = EventCode.from_name(code.name)
                assert result is not None
                assert result == code
                assert result.name == code.name
                assert result.value == code.value

    @pytest.mark.parametrize(
        "name",
        [
            "INVALID",
            "",
            "abs_x",  # lowercase
            "ABS_X ",  # trailing space
            " ABS_X",  # leading space
            "ABS_999",  # doesn't exist
            "X",  # missing prefix
            "Y",  # missing prefix
            "EV_ABS",  # event type
            "INPUT_PROP_POINTER",  # input property
        ],
    )
    def test_from_name_invalid_parametrized(self, name):
        """Test from_name() with various invalid names"""
        assert EventCode.from_name(name) is None

    def test_from_name_undefined_codes(self):
        """Test from_name() with undefined code names returns None"""
        # Undefined codes like SYN_04 are not accessible via from_name
        # because they are not set on the libevdev module
        assert EventCode.from_name("SYN_04") is None

    @pytest.mark.parametrize(
        "evtype,code,expected",
        [
            (libevdev.EV_ABS, 0, libevdev.ABS_X),
            (3, 0, libevdev.ABS_X),
            (libevdev.EV_ABS, 1, libevdev.ABS_Y),
            (3, 1, libevdev.ABS_Y),
            (libevdev.EV_REL, 0, libevdev.REL_X),
            (2, 0, libevdev.REL_X),
            (libevdev.EV_REL, 1, libevdev.REL_Y),
            (libevdev.EV_KEY, 1, libevdev.KEY_ESC),
            (1, 1, libevdev.KEY_ESC),
            (libevdev.EV_KEY, 30, libevdev.KEY_A),
            (libevdev.EV_SYN, 0, libevdev.SYN_REPORT),
            (0, 0, libevdev.SYN_REPORT),
        ],
    )
    def test_from_type_and_code_value(self, evtype, code, expected):
        """Test from_type_and_code_value() with various EventType and code combinations"""
        result = EventCode.from_type_and_code_value(evtype, code)
        assert result == expected

    def test_from_type_and_code_value_all_codes(self):
        """Test from_type_and_code_value() for all codes in all types"""
        for evtype in libevdev.types:
            for code in evtype.codes:
                # Test with EventType object
                result = EventCode.from_type_and_code_value(evtype, code.value)
                assert result == code

                # Test with int type value
                result = EventCode.from_type_and_code_value(evtype.value, code.value)
                assert result == code

    @pytest.mark.parametrize(
        "evtype,code",
        [
            (999, 9999),
            (libevdev.EV_ABS, 9999),
            (3, 9999),
            (libevdev.EV_ABS, -1),
            (libevdev.EV_REL, 1000),
            (libevdev.EV_KEY, 10000),
        ],
    )
    def test_from_type_and_code_value_invalid(self, evtype, code):
        """Test from_type_and_code_value() with various invalid codes"""
        result = EventCode.from_type_and_code_value(evtype, code)
        assert result is None

    def test_from_type_and_code_value_undefined_codes(self):
        """Test from_type_and_code_value() with undefined but valid code values"""
        # These are codes that exist in the range but don't have names
        # They should still be returned
        result = EventCode.from_type_and_code_value(libevdev.EV_SYN, 4)
        assert result is not None
        # The code should be the undefined one with generated name
        assert result.name == "SYN_04"
        assert result.value == 4
        assert not result.is_defined


class TestInputProperty:
    def test_from_value_valid_properties(self):
        """Test from_value() with valid property values"""
        assert InputProperty.from_value(0) == libevdev.INPUT_PROP_POINTER
        assert InputProperty.from_value(1) == libevdev.INPUT_PROP_DIRECT
        assert InputProperty.from_value(2) == libevdev.INPUT_PROP_BUTTONPAD

    @pytest.mark.parametrize("prop", [p for p in libevdev.props])
    def test_from_value_all_properties(self, prop):
        """Test from_value() returns correct property for all known properties"""
        result = InputProperty.from_value(prop.value)
        assert result is not None
        assert result == prop
        assert result.value == prop.value
        assert result.name == prop.name

    @pytest.mark.parametrize("value", [10, 20, 50, 255, 1000, -5, -100])
    def test_from_value_invalid(self, value):
        """Test from_value() with various invalid values"""
        assert InputProperty.from_value(value) is None

    @pytest.mark.parametrize(
        "name,expected",
        (
            ("INPUT_PROP_POINTER", libevdev.INPUT_PROP_POINTER),
            ("INPUT_PROP_DIRECT", libevdev.INPUT_PROP_DIRECT),
            ("INPUT_PROP_BUTTONPAD", libevdev.INPUT_PROP_BUTTONPAD),
            ("INPUT_PROP_SEMI_MT", libevdev.INPUT_PROP_SEMI_MT),
        ),
    )
    def test_from_name_valid_names(self, name, expected):
        """Test from_name() with valid property names"""
        assert InputProperty.from_name(name) == expected

    @pytest.mark.parametrize("prop", [p for p in libevdev.props])
    def test_from_name_all_properties(self, prop):
        """Test from_name() returns correct property for all known properties"""
        result = InputProperty.from_name(prop.name)
        assert result is not None
        assert result == prop
        assert result.value == prop.value
        assert result.name == prop.name

    @pytest.mark.parametrize(
        "name",
        [
            "INVALID",
            "INPUT_PROP_INVALID",
            "",
            "input_prop_pointer",  # lowercase
            "INPUT_PROP_POINTER ",  # trailing space
            " INPUT_PROP_POINTER",  # leading space
            "POINTER",  # missing prefix
            "EV_ABS",  # event type name
            "ABS_X",  # event code name
            "POINTER",  # missing prefix
            "DIRECT",  # missing prefix
        ],
    )
    def test_from_name_invalid_parametrized(self, name):
        """Test from_name() with various invalid names"""
        assert InputProperty.from_name(name) is None

    def test_from_value_and_from_name_consistency(self):
        """Test that from_value() and from_name() return the same objects"""
        for prop in libevdev.props:
            from_value = InputProperty.from_value(prop.value)
            from_name = InputProperty.from_name(prop.name)
            assert from_value == from_name
            assert from_value is from_name  # should be same object reference
