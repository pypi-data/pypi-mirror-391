from __future__ import annotations
from dataclasses import fields, is_dataclass
from typing import Any, Optional, Union, get_args, get_origin
import numpy as np
import h5py

from .datasets import save_array, read_array, create_or_overwrite

def _unwrap_optional(tp: Any) -> tuple[Any, bool]:
    """
    Return (inner_type, is_optional) for `Optional[T]` / `T | None` / `Union[T, None]`.
    """
    origin = get_origin(tp)
    if origin is Union:
        args = get_args(tp)
        if type(None) in args:
            non_none = [a for a in args if a is not type(None)]
            return (non_none[0] if non_none else Any), True
    return tp, False

def _as_python_scalar(x: Any) -> Any:
    """
    Convert 0-d arrays / numpy scalars / bytes to clean Python types.
    """
    if isinstance(x, np.ndarray) and x.shape == ():
        x = x[()]
    if isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, bytes):
        x = x.decode("utf-8", errors="replace")
    return x

def save_dataclass(
    group: h5py.Group,
    obj: Any,
    *,
    skip_none: bool = True,
    compression: Optional[str] = None,
    overwrite: bool = True,
) -> None:
    """
    Write each dataclass field to an HDF5 dataset.
    - lists/tuples → ndarray
    - strings → UTF-8 scalar dataset
    - ndarrays → via save_array (compression/overwrite honored)
    - numpy scalars → Python scalars
    """
    if not is_dataclass(obj):
        raise TypeError(f"Expected dataclass instance, got {type(obj)}")

    for f in fields(obj):
        name = f.name
        value = getattr(obj, name)

        if skip_none and value is None:
            continue

        # lists/tuples → ndarray
        if isinstance(value, (list, tuple)):
            value = np.asarray(value)

        # strings → UTF-8 scalar dataset
        if isinstance(value, str):
            dt = h5py.string_dtype(encoding="utf-8")  # type: ignore[attr-defined]
            create_or_overwrite(group, name, overwrite=overwrite)
            group.create_dataset(name, data=np.array(value, dtype=dt))
            continue

        # ndarray → use save_array
        if isinstance(value, np.ndarray):
            save_array(group, name, value, compression=compression, overwrite=overwrite)
            continue

        # numpy scalar → Python
        if isinstance(value, np.generic):
            value = value.item()

        # everything else (ints/floats/bools)
        create_or_overwrite(group, name, overwrite=overwrite)
        group.create_dataset(name, data=value)

def read_dataclass_from_h5(group: h5py.Group, cls: Any):
    """
    Construct dataclass `cls` from datasets/subgroups within `group`.
    - Missing fields fall back to dataclass defaults.
    - Strings/bytes normalized to str.
    - 0-d arrays / numpy scalars normalized to Python scalars.
    - ndarrays returned as numpy arrays.
    - Nested dataclasses supported if a subgroup exists under field name.
    """
    if not is_dataclass(cls):
        raise TypeError(f"Expected dataclass type, got {cls}")

    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        name = f.name
        inner_t, _ = _unwrap_optional(f.type)

        if name not in group:
            continue

        node = group[name]

        # subgroup → nested dataclass
        if isinstance(node, h5py.Group) and is_dataclass(inner_t):
            kwargs[name] = read_dataclass_from_h5(node, inner_t)
            continue

        if not isinstance(node, h5py.Dataset):
            raise TypeError(f"Field '{name}' is not a dataset/group in '{group.name}'")

        raw = node[()]

        # arrays (ndim >= 1) → ndarray
        if isinstance(raw, np.ndarray) and raw.ndim >= 1:
            kwargs[name] = np.asarray(raw)
            continue

        # scalars → normalize
        kwargs[name] = _as_python_scalar(raw)

    return cls(**kwargs)
