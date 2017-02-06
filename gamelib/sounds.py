#!/usr/bin/env python3
"""Load paths to sound files."""

import os
import sys


def load_sound_paths():
    """meh."""
    sound_dir = os.path.join(os.path.dirname(__file__), 'sound_files')

    for f in os.listdir(sound_dir):
        name = os.path.splitext(os.path.basename(f))[0]
        path = os.path.join(sound_dir, f)
        setattr(sys.modules[__name__], name, path)


load_sound_paths()
