from __future__ import annotations
from typing import Optional
import numpy as np
import h5py

def create_or_overwrite(group: h5py.Group, name: str, *, overwrite: bool) -> None:
    """
    Ensure `group[name]` is free to create. Delete if exists and overwrite=True.
    """
    if name in group:
        if overwrite:
            del group[name]
        else:
            raise KeyError(f"Dataset '{name}' already exists in group '{group.name}'")

def save_array(
    group: h5py.Group,
    name: str,
    array: np.ndarray,
    *,
    compression: Optional[str] = "gzip",
    overwrite: bool = True,
) -> None:
    """
    Save a NumPy array to an HDF5 dataset (optionally compressed).
    """
    if not isinstance(array, np.ndarray):
        raise TypeError(f"Expected np.ndarray, got {type(array)}")
    create_or_overwrite(group, name, overwrite=overwrite)
    group.create_dataset(name, data=array, compression=compression)

def read_array(group: h5py.Group, name: str) -> np.ndarray:
    """
    Read an HDF5 dataset as a NumPy array.
    """
    if name not in group:
        raise KeyError(f"Dataset '{name}' not found in group '{group.name}'")
    return np.asarray(group[name][()])
