from dataclasses import dataclass
import numpy as np
import h5py
from allytools.formats import (
    save_array, read_array,
    save_dataclass, read_dataclass_from_h5,
    set_attrs_from_dataclass, get_attrs_as_dict,
)

@dataclass
class Foo:
    x: int
    y: np.ndarray
    name: str = "demo"

with h5py.File("demo.h5", "w") as f:
    g = f.create_group("grp")
    save_array(g, "data", np.arange(6).reshape(2, 3))
    save_dataclass(g, Foo(7, np.array([1.0, 2.0])))
    set_attrs_from_dataclass(g, {"version": "1.0", "ok": True})

with h5py.File("demo.h5", "r") as f:
    g = f["grp"]
    A = read_array(g, "data")
    foo = read_dataclass_from_h5(g, Foo)
    attrs = get_attrs_as_dict(g)
