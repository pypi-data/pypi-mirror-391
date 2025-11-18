"""Test prerequisites file."""

from typing import Dict

import pytest

from prerequisites import (
    require,
    require_all_in_all,
    require_all_of_type,
    require_all_same_type,
    require_one_in_all,
    require_one_of_types,
    require_type,
    require_type_or_none,
)


def test_require_conditions() -> None:
    """Test require conditions."""
    require(1 > 0)
    require_one_in_all([1 > 0, False])
    require_all_in_all([1 > 0, True, "a" + "b" == "ab"])

    with pytest.raises(ValueError):
        require("a" == "b")

    with pytest.raises(ValueError):
        require_one_in_all([1 < 0, False])

    with pytest.raises(ValueError):
        require_all_in_all([1 > 0, False, "a" + "b" == "ab"])


def test_variable_types() -> None:
    """Test require types."""
    require_type(1, int)
    require_one_of_types(1, (int, float))
    require_all_of_type([1, 2, 3, 0, 1 + 2], int)
    require_all_same_type([1, 2, 3])
    require_all_same_type([1, 2, 3], [int])
    require_type_or_none(None, str)
    require_type_or_none(21, int)

    with pytest.raises(TypeError):
        require_type("test", int)

    with pytest.raises(TypeError):
        require_all_same_type(["test", 1])

    with pytest.raises(TypeError):
        require_one_of_types(1, (Dict, str))

    with pytest.raises(TypeError):
        require_all_of_type([1, 2, 3, "a", 1 + 2], int)

    with pytest.raises(TypeError):
        require_type_or_none(1, str)
