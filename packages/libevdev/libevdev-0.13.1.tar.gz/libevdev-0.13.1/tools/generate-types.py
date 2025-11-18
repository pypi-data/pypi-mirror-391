#!/usr/bin/env python3
# Copyright © 2025 Red Hat, Inc.
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
#
# This script generates the __init__.pyi type definitions.
# Usage:
#   $ python3 ./tools/generate-types.py > libevdev/__init__.pyi
#
# This only needs updates when new codes are being added to the kernel and even
# then it only needs updates for those codes to resolve for typing checkers. The
# actual lookup of the value is at runtime.

from libevdev._clib import Libevdev


prefix = """# This file is generated, do not edit
from typing import Type

from libevdev import device
from libevdev import event
from libevdev import const

Device: Type[device.Device]
InputAbsInfo: Type[device.InputAbsInfo]
InvalidFileError: Type[device.InvalidFileError]
EventsDroppedException: Type[device.EventsDroppedException]
InvalidArgumentException: Type[device.InvalidArgumentException]
InputEvent: Type[event.InputEvent]
EventType: Type[const.EventType]
EventCode: Type[const.EventCode]
InputProperty: Type[const.InputProperty]

def evbit(
    evtype: int | str, evcode: int | str | None = None
) -> const.EventCode | const.EventType | None: ...
def propbit(prop: int | str) -> const.InputProperty | None: ...
"""

print(prefix)

Libevdev()  # libevdev's methods are set as classmethods once we instantiate it

tmax: int | None = Libevdev.event_to_value("EV_MAX")
assert tmax is not None

type_names: list[str] = []
code_names: list[str] = []

for t in range(tmax + 1):
    tname = Libevdev.event_to_name(t)
    if tname is None:
        continue

    cmax = Libevdev.type_max(t)
    if cmax is None:
        continue

    print(f"class _{tname}(const.EventType):")
    type_names.append(tname)

    for c in range(cmax + 1):
        cname = Libevdev.event_to_name(t, c)
        if cname is None:
            continue

        print("    @property")
        print(f"    def {cname}(self) -> const.EventCode: ...")
        code_names.append(f"{cname}")

    print()

pmax: int | None = Libevdev.property_to_value("INPUT_PROP_MAX")
assert pmax is not None
prop_names: list[str] = []
for p in range(pmax + 1):
    pname = Libevdev.property_to_name(p)
    if pname is None:
        continue
    prop_names.append(pname)

for name in type_names:
    print(f"{name}: _{name}")
for name in code_names:
    print(f"{name}: const.EventCode")
for name in prop_names:
    print(f"{name}: const.InputProperty")

print("types: list[const.EventType]")
print("props: list[const.InputProperty]")
