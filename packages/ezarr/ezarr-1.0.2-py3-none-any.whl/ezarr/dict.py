from __future__ import annotations

import itertools as it
from collections.abc import ItemsView, Iterator, Mapping, MutableMapping
from typing import Any, Self, cast, override
import warnings

import numpy as np
import numpy.typing as npt
import zarr
from numpy._typing import _SupportsArray as SupportsArray  # pyright: ignore[reportPrivateUsage]
from zarr.errors import UnstableSpecificationWarning
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

import ezarr
from ezarr import io
from ezarr._repr import repr_element
from ezarr.names import AccessModeLiteral
from ezarr.object import EZObject

type DictData[T] = Mapping[str, int | float | np.integer | np.floating | list[Any] | npt.ArrayLike | DictData[T]]
type GroupItems = ItemsView[str, zarr.Group | zarr.Array]


class EZDict[T](EZObject[T, dict[str, T]], MutableMapping[str, T]):
    """
    Dict-like object wrapping a zarr.Group for storing arbitrary Python objects

    Args:
        group: a zarr.Group

    Example:
        >>> EZDict(zarr.open_group({}))
        EZDict{}
    """

    __match_args__: tuple[str] = ("_group",)

    def __init__(self, group: zarr.Group) -> None:
        self._group: zarr.Group = group

    @classmethod
    def from_dict(
        cls,
        dct: Mapping[str, Any],
        *,
        name: str = "",
        store: StoreLike | None = None,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> Self:
        r"""
        Create an EZDict from a regular in-memory Python dictionary.

        Args:
            dct: dictionary with arbitrary data to store.
            name: name for the EZDict, to use inside the store.
            store: Store or path to directory in file system or nam of zip file.
            mode: Persistence mode, in ['r', 'r+', 'a', 'w', 'w-'].
            path: Group path within store.
            overwrite: overwrite object if a group with name `name` already exists ? (default: False)

        Example:
            >>> data = {"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}}
            >>> ez_dict = EZDict.from_dict(data)
            >>> repr(ez_dict)
            'EZDict{\n\ta: 1,\n\tb: [1 2 3],\n\tc: {...}\n}'
        """
        if store is None:
            store = {}

        grp = zarr.open_group(store, mode=mode, path=path)

        if name:
            grp = grp.create_group(name, overwrite=overwrite)

        to_visit: list[tuple[Any, str, str]] = [(dct[k], k, "") for k in dct.keys()]

        while len(to_visit):
            value, name_, path_ = to_visit.pop()

            if isinstance(value, Mapping):
                to_visit.extend([(value[k], k, f"{path_}/{name_}" if path_ else name_) for k in value.keys()])  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

            elif isinstance(value, list | SupportsArray):
                grp.require_group(path_).create_array(name_, data=np.asarray(value), overwrite=overwrite)  # pyright: ignore[reportUnknownArgumentType]

            else:
                io.write_object(grp, obj=value, name=name_, path=path_, overwrite=overwrite)

        return cls(grp)

    @staticmethod
    def _repr(grp: zarr.Group) -> str:
        if not len(grp):
            return "{}"

        if len(grp) > 100:
            return (
                "{\n\t"
                + ",\n\t".join(
                    [
                        f"{name}: {repr_element(io.read_object(grp, name=name), prefix=f'\t{" " * len(name)}  ')}"
                        for name in it.islice(sorted(grp.keys()), 0, 10)
                    ]
                )
                + ",\n\t...,\n\t"
                + ",\n\t".join(
                    [
                        f"{name}: {repr_element(io.read_object(grp, name=name), prefix=f'\t{" " * len(name)}  ')}"
                        for name in it.islice(sorted(grp.keys()), len(grp) - 10, None)
                    ]
                )
                + "}"
            )

        return (
            "{\n\t"
            + ",\n\t".join(
                [
                    f"{name}: {repr_element(io.read_object(grp, name=name), prefix=f'\t{" " * len(name)}  ')}"
                    for name in sorted(grp.keys())
                ]
            )
            + "\n}"
        )

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}{self._repr(self._group)}"

    @override
    def __len__(self) -> int:
        return len(self._group)

    @override
    def __getitem__(self, key: str, /) -> T:
        return io.read_object(self._group, name=key)

    @override
    def __setitem__(self, key: str, value: T, /) -> None:
        if key in self:
            try:
                # try to compare values, might fail when comparing arrays with different shapes
                if self[key] == value:
                    return

            except ValueError:
                pass

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            io.write_object(self._group, obj=value, name=key, overwrite=True)

    @override
    def __delitem__(self, key: str, /) -> None:
        del self._group[key]

    @override
    def __iter__(self) -> Iterator[str]:
        yield from sorted(self._group.keys())

    def __deepcopy__(self, _memo: dict[Any, Any]) -> dict[str, Any]:
        return self.copy()

    def __ior__(self, other: object) -> EZDict[T]:
        if not isinstance(other, Mapping):
            raise NotImplementedError

        other = cast(Mapping[str, T], other)
        for name, value in other.items():
            if isinstance(value, Mapping):
                grp = self._group.require_group(name)
                EZDict(grp).__ior__(value)  # pyright: ignore[reportUnknownArgumentType]

            else:
                with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                    self[name] = value

        return self

    @classmethod
    @override
    def open(
        cls, store: StoreLike | None = None, *, name: str = "", mode: AccessModeLiteral = "a", path: str | None = None
    ) -> Self:
        r"""
        Open this EZDict from a store.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZDict, to use inside the store.
            mode: Persistence mode.
            path: path within the store to open.

        Example:
            >>> ez_dict = EZDict.from_dict({"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}})
            >>> ez_dict.save("/tmp/dict", overwrite=True)
            >>> repr(ez_dict.open("/tmp/dict"))
            'EZDict{\n\ta: 1,\n\tb: [1 2 3]\n}'
        """
        path = f"{path.rstrip('/')}/{name}" if path else name
        return cls(zarr.open_group(store, mode=mode, path=path))

    @override
    def save(
        self,
        store: StoreLike,
        *,
        name: str = "",
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save this EZDict to a local file system.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZDict, to use inside the store.
            mode: Persistence mode.
            path: path within the store where the EZDict will be saved.
            overwrite: overwrite EZDict if a group with name `name` already exists ? (default: False)

        Example:
            >>> from pathlib import Path
            >>> ez_dict = EZDict.from_dict({"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}})
            >>> ez_dict.save("/tmp/dict", overwrite=True)
            >>> Path("/tmp/dict").exists()
            True
        """
        path = f"{path.rstrip('/')}/{name}/" if path else f"{name}/"

        for _, array in self._group.arrays():
            assert isinstance(array, zarr.Array)
            zarr.create_array(store, name=path + array.path, data=array, overwrite=overwrite)  # pyright: ignore[reportArgumentType]

    @staticmethod
    def _copy_nested(dct: dict[str, Any], value: EZDict[Any]) -> dict[str, Any]:
        for k, v in value.items():
            if isinstance(v, EZDict):
                sub = dct.setdefault(k, {})
                EZDict._copy_nested(sub, v)  # pyright: ignore[reportUnknownArgumentType]

            elif isinstance(v, ezarr.EZList):
                dct[k] = v.copy()

            elif isinstance(v, zarr.Array):
                dct[k] = np.array(v)

            else:
                dct[k] = v

        return dct

    @override
    def copy(self) -> dict[str, T]:
        """
        Convert this EZDict into a Python dict, loading all the data into memory.

        Example:
            >>> ez_dict = EZDict.from_dict({"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}})
            >>> ez_dict.copy()
            {'a': np.int64(1), 'b': array([1, 2, 3]), 'c': {'d': np.str_('some text')}}
        """
        return EZDict._copy_nested({}, self)
