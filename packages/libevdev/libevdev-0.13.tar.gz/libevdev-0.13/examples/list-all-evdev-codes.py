#!/usr/bin/env python3

import sys
import libevdev


def main(_):
    for t in libevdev.types:
        print(f"#define {t.name} {t.value}")

    for t in libevdev.types:
        for c in filter(lambda c: c.is_defined, t.codes):
            print(f"#define {c.name} {c.value}")
        print()

    for p in libevdev.props:
        print(f"#define {p.name} {p.value}")

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(f"Usage: {sys.argv[0]}")
        sys.exit(1)
    main(sys.argv)
