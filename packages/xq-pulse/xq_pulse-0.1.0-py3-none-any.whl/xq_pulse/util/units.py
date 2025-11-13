import functools
import inspect

import pint

from xq_pulse.util import unit


class UnitValidator:
    """
    A validators for attrs to check if a value is compatible with a given unit.
    """

    def __init__(self, unit: pint.Unit):
        self.unit = unit

    def __call__(self, _, __, value):
        assert isinstance(value, pint.Quantity), f"Value {value} of type {type(value).__name__} is not a pint.Quantity"
        assert value.is_compatible_with(self.unit), f"Value {value} is not compatible with unit {self.unit}"

    def __repr__(self):
        return f"<Validator for pint.Quantity with unit {self.unit}>"


def args(**decorator_kwargs):
    def decorator_units(func):
        @functools.wraps(func)
        def wrapper_units(*args, **kwargs):
            # Get the function signature to map positional args to parameter names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for key, declared_unit in decorator_kwargs.items():
                assert isinstance(declared_unit, pint.Unit), f"Unit {declared_unit} is not a valid unit"
                assert key in bound_args.arguments, (
                    f"Argument {key} has a unit constraint but is not present in the function signature"
                )
                arg_value = bound_args.arguments[key]
                assert declared_unit.is_compatible_with(arg_value), (
                    f"Argument {arg_value} of type {type(arg_value).__name__} is not compatible with declared unit {declared_unit}"
                )

            # Call to the actual function
            value = func(*args, **kwargs)
            return value

        return wrapper_units

    return decorator_units


def returns(declared_unit: pint.Unit):
    def decorator_returns(func):
        @functools.wraps(func)
        def wrapper_returns(*args, **kwargs):
            assert isinstance(declared_unit, pint.Unit), f"Unit {declared_unit} is not a valid unit"

            # Call to the actual function
            value = func(*args, **kwargs)
            assert declared_unit.is_compatible_with(value), (
                f"Return value {value} of type {type(value).__name__} is not compatible with declared unit {declared_unit}"
            )
            return value

        return wrapper_returns

    return decorator_returns


def round_time(time: pint.Quantity) -> pint.Quantity:
    """
    Round a time quantity to the nearest nanosecond. Returns a quantity in nanoseconds.
    This function is mainly needed to work around floating point inaccuracies.
    By rounding the times equality checks and hashing (so units as dict or set keys) work as expected.
    """
    return round(time.m_as(unit.ns)) * unit.ns
