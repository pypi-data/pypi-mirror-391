from dataclasses import fields, is_dataclass
import numpy as np
import h5py

def read_dataclass_from_h5(group: h5py.Group, cls):
    if not is_dataclass(cls):
        raise TypeError(f"Expected dataclass type, got {cls}")
    kwargs = {}
    for f in fields(cls):
        if f.name in group:
            kwargs[f.name] = group[f.name][()]
    return cls(**kwargs)

def save_dataclass(group: h5py.Group, obj, *, skip_none: bool = True) -> None:
    if not is_dataclass(obj):
        raise TypeError(f"Expected dataclass instance, got {type(obj)}")
    for f in fields(obj):
        name = f.name
        value = getattr(obj, name)
        if skip_none and value is None:
            continue
        if isinstance(value, (list, tuple)):
            value = np.asarray(value)
        elif isinstance(value, str):
            dtype = h5py.string_dtype(encoding="utf-8") # type: ignore[attr-defined]
            group.create_dataset(name, data=np.array(value, dtype=dtype))
            continue
        group.create_dataset(name, data=value)

def save_array(group: h5py.Group, name: str, array: np.ndarray, *,
               compression: str | None = "gzip",
               overwrite: bool = True) -> None:
    if not isinstance(array, np.ndarray):
        raise TypeError(f"Expected np.ndarray, got {type(array)}")
    if name in group:
        if overwrite:
            del group[name]
        else:
            raise KeyError(f"Dataset '{name}' already exists in group '{group.name}'")
    group.create_dataset(name, data=array, compression=compression)


def read_array_from_h5(group: h5py.Group, name: str) -> np.ndarray:
    """
    Read a NumPy array from a dataset in an HDF5 group.
    Returns a numpy array (converted via np.asarray).
    """
    if name not in group:
        raise KeyError(f"Dataset '{name}' not found in group '{group.name}'")

    data = group[name][()]
    return np.asarray(data)




def set_attrs_from_dataclass(h5obj, obj, *, skip_none: bool = True) -> None:
    """
    Copy fields from a dataclass (or items from a dict) into HDF5 attributes.
    Normalizes numpy scalars and UTF-8 strings.
    """
    if is_dataclass(obj):
        items = ((f.name, getattr(obj, f.name)) for f in fields(obj))
    elif isinstance(obj, dict):
        items = obj.items()
    else:
        raise TypeError(f"Expected dataclass or dict, got {type(obj)}")

    for k, v in items:
        if skip_none and v is None:
            continue

        # Normalize common types for HDF5 attrs
        if isinstance(v, np.generic):
            v = v.item()
        elif isinstance(v, bytes):
            v = v.decode("utf-8", errors="replace")
        elif isinstance(v, (list, tuple)):
            v = np.asarray(v)

        if isinstance(v, str):
            dt = h5py.string_dtype(encoding="utf-8")  # type: ignore[attr-defined]
            h5obj.attrs.create(k, np.array(v, dtype=dt))
        else:

            h5obj.attrs[k] = v

def normalize_attr_value(v):
    # HDF5 attrs can be numpy scalars, 0-d arrays, or bytes
    if isinstance(v, np.ndarray) and v.shape == ():
        v = v[()]
    if isinstance(v, np.generic):
        v = v.item()
    if isinstance(v, bytes):
        v = v.decode("utf-8", errors="replace")
    return v

