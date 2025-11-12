from dataclasses import fields, is_dataclass
from typing import Union, get_args, get_origin


class DictLike:
    """
    A class that allows attribute access via dictionary-like key lookup.

    Provides dictionary-style access (`obj[key]`) to attributes.
    Also supports `get(key, default)` method and `find_key` to search nested structures.
    """

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def find_key(self, key):
        if hasattr(self, key):
            return getattr(self, key)

        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue
            attr_value = getattr(self, attr_name, None)
            if isinstance(attr_value, DictLike):
                try:
                    return attr_value.find_key(key)
                except KeyError:
                    pass

        raise KeyError(key)

    def __post_init__(self):
        if not is_dataclass(self):
            return

        for field in fields(self):
            value = getattr(self, field.name)
            if value is None:
                continue

            target_type = field.type

            if get_origin(target_type) is Union:
                args = get_args(target_type)
                target_type = next((arg for arg in args if arg is not type(None)), None)

            if (
                isinstance(value, dict)
                and isinstance(target_type, type)
                and issubclass(target_type, DictLike)
            ):
                setattr(self, field.name, target_type(**value))

            elif isinstance(value, list) and get_origin(target_type) is list:
                inner_type = get_args(target_type)[0]
                if isinstance(inner_type, type) and issubclass(inner_type, DictLike):
                    setattr(
                        self,
                        field.name,
                        [inner_type(**v) if isinstance(v, dict) else v for v in value],
                    )


__all__ = ["DictLike"]
