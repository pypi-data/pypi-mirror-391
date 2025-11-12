from __future__ import annotations

__all__ = ["FieldDoesNotExistTestError", "validate_fields_exists_or_raise"]


class FieldDoesNotExistTestError(Exception):
    pass


def validate_fields_exists_or_raise(cleaned_data: dict, model_cls) -> None:
    if not_found := [
        key
        for key in cleaned_data
        if key not in [fld.name for fld in model_cls._meta.get_fields()]
    ]:
        raise FieldDoesNotExistTestError(f"Invalid field in cleaned data. Got {not_found}")
