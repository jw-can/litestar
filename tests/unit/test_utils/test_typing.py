from __future__ import annotations

from sys import version_info
from typing import Any, Deque, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import pytest
from typing_extensions import Annotated

from litestar.utils.typing import annotation_is_iterable_of_type, get_origin_or_inner_type, make_non_optional_union
from tests.models import DataclassPerson, DataclassPet

if version_info >= (3, 10):
    from collections import deque  # noqa: F401

    py_310_plus_annotation = [
        (eval(tp), exp)
        for tp, exp in [
            ("tuple[DataclassPerson, ...]", True),
            ("list[DataclassPerson]", True),
            ("deque[DataclassPerson]", True),
            ("tuple[DataclassPet, ...]", False),
            ("list[DataclassPet]", False),
            ("deque[DataclassPet]", False),
        ]
    ]
else:
    py_310_plus_annotation = []


@pytest.mark.parametrize(
    "annotation, expected",
    (
        (List[DataclassPerson], True),
        (Sequence[DataclassPerson], True),
        (Iterable[DataclassPerson], True),
        (Tuple[DataclassPerson, ...], True),
        (Deque[DataclassPerson], True),
        (List[DataclassPet], False),
        (Sequence[DataclassPet], False),
        (Iterable[DataclassPet], False),
        (Tuple[DataclassPet, ...], False),
        (Deque[DataclassPet], False),
        *py_310_plus_annotation,
        (int, False),
        (str, False),
        (bool, False),
    ),
)
def test_annotation_is_iterable_of_type(annotation: Any, expected: bool) -> None:
    assert annotation_is_iterable_of_type(annotation=annotation, type_value=DataclassPerson) is expected


@pytest.mark.parametrize(
    ("annotation", "expected"), [(Union[None, str, int], Union[str, int]), (Optional[Union[str, int]], Union[str, int])]
)
def test_make_non_optional_union(annotation: Any, expected: Any) -> None:
    assert make_non_optional_union(annotation) == expected


def test_get_origin_or_inner_type() -> None:
    assert get_origin_or_inner_type(List[DataclassPerson]) == list
    assert get_origin_or_inner_type(Annotated[List[DataclassPerson], "foo"]) == list
    assert get_origin_or_inner_type(Annotated[Dict[str, List[DataclassPerson]], "foo"]) == dict
