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


import libevdev
from libevdev import InputEvent


class TestEvents:
    def test_event_matches_type(self):
        ev = InputEvent(libevdev.EV_REL)
        assert ev.matches(libevdev.EV_REL)
        assert not ev.matches(libevdev.EV_REL.REL_X)
        assert not ev.matches(libevdev.EV_ABS)
        assert not ev.matches(libevdev.EV_ABS.ABS_X)

    def test_event_matches_code(self):
        ev = InputEvent(libevdev.EV_REL.REL_X)
        assert ev.matches(libevdev.EV_REL.REL_X)
        assert ev.matches(libevdev.EV_REL)
        assert not ev.matches(libevdev.EV_ABS)
        assert not ev.matches(libevdev.EV_ABS.ABS_X)

    def test_event_matches_self(self):
        e1 = InputEvent(libevdev.EV_REL.REL_X)
        e2 = InputEvent(libevdev.EV_REL)
        assert e1 == e1
        assert e2 == e2

        assert e2 == e1
        assert e1 == e2

        e2 = InputEvent(libevdev.EV_REL.REL_Y)
        assert e2 != e1
        assert e1 != e2

    def test_event_matches_invalid(self):
        e1 = InputEvent(libevdev.EV_REL.REL_X)
        assert e1 != 0
        assert e1 is not None
        assert e1 != "foo"
