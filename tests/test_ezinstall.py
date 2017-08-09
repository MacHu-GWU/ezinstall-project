#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from ezinstall.ezinstall import Path


def test():
    p = Path(__file__)

    assert p.basename == "test_ezinstall.py"
    assert p.fname == "test_ezinstall"
    assert p.ext == ".py"
    assert p.dirname == "tests"

    assert p.parent.basename == "tests"

    assert p.parts[-1] == "test_ezinstall.py"
    assert p.parts[-2] == "tests"

    assert p.path_chain()[0].basename == "test_ezinstall.py"
    assert p.path_chain()[1].basename == "tests"


if __name__ == "__main__":
    import os
    pytest.main([os.path.basename(__file__), "--tb=native", "-s", ])
