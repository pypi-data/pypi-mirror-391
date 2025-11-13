"""
Tiny, typed helpers for HDF5 + dataclasses.
"""
from .datasets import save_array, read_array, create_or_overwrite
from .dataclass_io import save_dataclass, read_dataclass_from_h5
from .attrs import (
    set_attrs_from_dataclass,
    get_attrs_as_dict,
    read_attrs_into_dataclass,
    normalize_attr_value,
)

__all__ = [
    # datasets
    "save_array", "read_array", "create_or_overwrite",
    # dataclasses
    "save_dataclass", "read_dataclass_from_h5",
    # attributes
    "set_attrs_from_dataclass", "get_attrs_as_dict",
    "read_attrs_into_dataclass", "normalize_attr_value",
]
