from __future__ import annotations

from numbers import Number
import pickle
from collections.abc import Collection, Mapping
from typing import Any, cast
import warnings

import numpy as np
import zarr
from zarr.errors import UnstableSpecificationWarning

import ezarr
from ezarr.names import UNKNOWN, Attribute, EZType
from ezarr.types import DeferredCreationFunc, PyObject, PyObjectCodec, SupportsEZRead, SupportsEZWrite


def read_object(grp: zarr.Group, *, name: str, path: str = "") -> Any:
    path = f"{path.lstrip('/')}/{name}" if path else name
    data = grp[path]
    ez_type = cast(str, data.attrs.get(Attribute.EZType, UNKNOWN))

    if isinstance(data, zarr.Group):
        if ez_type != EZType.Object:
            return ezarr.EZDict[Any](data)

        ez_class = cast(zarr.Array | None, data.get(Attribute.EZClass))
        if ez_class is None:
            raise ValueError("Cannot read object with unknown class.")

        assert isinstance(ez_class, zarr.Array)
        data_class = pickle.loads(ez_class[()])

        if not issubclass(data_class, SupportsEZRead):
            raise ValueError(
                f"Don't know how to read {data_class} since it does not implement the '__ez_read__' method."
            )

        return data_class.__ez_read__(data)

    if data.ndim == 0:
        return data[()]

    if ez_type == EZType.List:
        return ezarr.EZList[Any](data)

    return data


def write_object[T](grp: zarr.Group, *, obj: Any, name: str, path: str = "", overwrite: bool = False) -> None:
    """
    Save any object in a zarr.Group

    Args:
        grp: a zarr.Group.
        obj: a Python object to be saved.
        name: name for the object, to use inside the Group.
        path: [optional] path within the Group where the object will be saved.
        overwrite: overwrite if a group with name `name` already exists ? (default: False)
    """
    if path:
        grp = grp.require_group(path, overwrite=overwrite)

    match obj:
        case SupportsEZWrite():
            subgroup = grp.create_group(name, overwrite=overwrite)
            subgroup.attrs[Attribute.EZType] = EZType.Object
            obj.__ez_write__(subgroup)

            klass = pickle.dumps(type(obj), protocol=pickle.HIGHEST_PROTOCOL)

            subgroup.create_array(Attribute.EZClass, data=np.void(klass), overwrite=True)  # pyright: ignore[reportArgumentType]

        case DeferredCreationFunc():
            obj(grp, name, overwrite)

        case Mapping():
            subgroup = grp.create_group(name, overwrite=overwrite)
            write_objects(subgroup, "", **obj)

        case Collection() | Number():
            with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                grp.create_array(name, data=np.array(obj), overwrite=overwrite)

        case _:
            with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                arr = grp.create_array(
                    name, shape=(), dtype=PyObject(), serializer=PyObjectCodec(), overwrite=overwrite
                )
            arr[()] = obj


def write_objects[T](grp: zarr.Group, path: str = "", **kwargs: Any) -> None:
    for name, value in kwargs.items():
        write_object(grp, obj=value, name=name, path=path)
