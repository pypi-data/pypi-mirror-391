"""Serialization support for pulse programs using cattrs."""

from __future__ import annotations

import attrs
import numpy as np
import pint
from cattrs import Converter

from xq_pulse.pulse.envelope import (
    Envelope,
    PiecewiseEnvelope,
    SquareEnvelope,
)
from xq_pulse.pulse.expression import (
    DifferenceExpression,
    Expression,
    Literal,
    MaximumExpression,
    Parameter,
    ProductExpression,
    QuotientExpression,
    SumExpression,
)
from xq_pulse.pulse.pulse import (
    AcquisitionPulse,
    ChannelMappedPulse,
    ContainerPulse,
    DelayPulse,
    DrivePulse,
    ForLoopPulse,
    LaserPulse,
    LeafPulse,
    ParallelPulse,
    Pulse,
    SequencePulse,
)
from xq_pulse.util import Unit, unit


def configure_converter(converter: Converter) -> None:
    """Configure a cattrs Converter for PulseProgram serialization.

    Sets up tagged union handling for Expression types and other necessary hooks.
    """

    # Handle numpy arrays - convert to/from lists for serialization
    def unstructure_numpy_array(arr: np.ndarray) -> dict:
        """Unstructure a numpy array to a dict with data, shape, and dtype."""
        return {
            "_type": "numpy.ndarray",
            "data": arr.tolist(),
            "shape": arr.shape,
            "dtype": str(arr.dtype),
        }

    def structure_numpy_array(obj: dict, _: type) -> np.ndarray:
        """Structure a dict back to a numpy array."""
        if not isinstance(obj, dict):
            raise ValueError(f"Expected dict for numpy array, got {type(obj)}")
        if obj.get("_type") != "numpy.ndarray":
            raise ValueError(f"Expected numpy array type tag, got {obj.get('_type')}")
        return np.array(obj["data"], dtype=obj.get("dtype", None)).reshape(obj["shape"])

    converter.register_unstructure_hook(np.ndarray, unstructure_numpy_array)
    converter.register_structure_hook(np.ndarray, structure_numpy_array)

    # Handle pint.Quantity (Literal) - structure/unstructure hooks
    # Using pint's recommended serialization approach: serialize magnitude and units string,
    # then reconstruct using the application registry (unit from xq_pulse.util)
    def unstructure_quantity(q: pint.Quantity) -> dict:
        """Unstructure a pint.Quantity using pint's serialization format.

        See https://pint.readthedocs.io/en/stable/advanced/serialization.html
        """
        return {
            "_type": "Literal",
            "magnitude": q.magnitude,
            "units": str(q.units),
        }

    def structure_quantity(obj: dict, _: type) -> pint.Quantity:
        """Structure a dict back to a pint.Quantity using pint's serialization format.

        Uses the application registry (unit from xq_pulse.util) to ensure custom units are preserved.
        See https://pint.readthedocs.io/en/stable/advanced/serialization.html
        """
        # Allow both with and without type tag (for compatibility)
        if isinstance(obj, dict):
            # If it has a type tag, verify it's Literal
            if "_type" in obj:
                if obj["_type"] != "Literal":
                    raise ValueError(f"Expected Literal type tag, got {obj.get('_type')}")
                # Use the application registry to reconstruct the Quantity
                return unit.Quantity(obj["magnitude"], obj["units"])
            # If no type tag, assume it's a direct Quantity dict (from unstructure_quantity)
            if "magnitude" in obj and "units" in obj:
                # Use the application registry to reconstruct the Quantity
                return unit.Quantity(obj["magnitude"], obj["units"])
        raise ValueError(f"Cannot structure Quantity from {type(obj)}: {obj}")

    converter.register_unstructure_hook(pint.Quantity, unstructure_quantity)
    converter.register_structure_hook(pint.Quantity, structure_quantity)

    # Handle pint.Unit - structure/unstructure hooks
    def unstructure_unit(u: pint.Unit) -> str:
        """Unstructure a pint.Unit to its string representation."""
        return str(u)

    def structure_unit(obj: str, _: type) -> pint.Unit:
        """Structure a string back to a pint.Unit."""
        return pint.Unit(obj)

    # Register for the base Unit type
    converter.register_unstructure_hook(pint.Unit, unstructure_unit)
    converter.register_structure_hook(pint.Unit, structure_unit)

    # Also handle PlainUnit if available (pint 0.23+)
    try:
        from pint.facets.plain.unit import PlainUnit

        converter.register_structure_hook(PlainUnit, structure_unit)
    except (ImportError, AttributeError):
        pass  # PlainUnit might not be available in all pint versions

    # Handle the Unit union type (PintUnit | PlainUnit) from xq_pulse.util
    # Both types serialize the same way (as strings), so we can use the same handler
    def structure_unit_union(obj: str, _: type) -> Unit:
        """Structure a string back to a Unit, handling the union type."""
        # Create a Unit from string - this works for both PintUnit and PlainUnit
        return pint.Unit(obj)

    # Register handlers for the union type from xq_pulse.util
    converter.register_unstructure_hook(Unit, unstructure_unit)
    converter.register_structure_hook(Unit, structure_unit_union)

    # Handle Expression union type using tagged unions
    # Each expression type needs a type tag during unstructuring
    # We'll use "_type" as the discriminator field

    # Unstructure hooks for each expression type - add type tag
    def unstructure_expression_with_tag(expr: Expression) -> dict:
        """Unstructure an Expression, adding a type tag."""
        if isinstance(expr, pint.Quantity):
            # Quantity already has _type from unstructure_quantity
            return unstructure_quantity(expr)
        # For attrs classes, use the standard unstructuring but add a type tag
        # Note: nested Expressions will be handled recursively
        result = converter.unstructure(expr, unstructure_as=type(expr))
        result["_type"] = type(expr).__name__
        return result

    # Structure hook for Expression union - use type tag to disambiguate
    def structure_expression(obj: dict, _: type) -> Expression:
        """Structure an Expression from a dict using the type tag."""
        if not isinstance(obj, dict):
            raise ValueError(f"Expected dict for Expression, got {type(obj)}")

        type_name = obj.get("_type")
        if type_name is None:
            # If no type tag but looks like a Quantity, try structuring as Quantity
            if "magnitude" in obj and "units" in obj:
                return structure_quantity(obj, pint.Quantity)
            raise ValueError("Expression dict missing '_type' field")

        # Map type names to classes
        type_map = {
            "Literal": pint.Quantity,
            "Parameter": Parameter,
            "SumExpression": SumExpression,
            "DifferenceExpression": DifferenceExpression,
            "ProductExpression": ProductExpression,
            "MaximumExpression": MaximumExpression,
            "QuotientExpression": QuotientExpression,
        }

        expr_class = type_map.get(type_name)
        if expr_class is None:
            raise ValueError(f"Unknown Expression type: {type_name}")

        # For Literal (Quantity), we can structure directly
        if expr_class is pint.Quantity:
            return structure_quantity(obj, pint.Quantity)

        # For other types, create a dict without the type tag for structuring
        obj_without_tag = {k: v for k, v in obj.items() if k != "_type"}

        return converter.structure(obj_without_tag, expr_class)

    # Register hooks for the Expression union
    converter.register_unstructure_hook(Expression, unstructure_expression_with_tag)
    converter.register_structure_hook(Expression, structure_expression)

    # Also register for Literal alias (which is just Quantity)
    converter.register_unstructure_hook(Literal, unstructure_quantity)
    converter.register_structure_hook(Literal, structure_quantity)

    # Handle Envelope union type using tagged unions
    def unstructure_envelope_with_tag(env: Envelope) -> dict:
        """Unstructure an Envelope, adding a type tag."""
        # Use attrs.asdict() to get the dict representation, avoiding recursion
        # by not going through the converter's unstructure hook
        result = attrs.asdict(env)

        # Process nested values recursively, handling Envelopes specially
        def process_value(v):
            if isinstance(v, Envelope):
                # Recursively call the hook for nested Envelopes
                return unstructure_envelope_with_tag(v)
            elif isinstance(v, (list, tuple)):
                return type(v)(process_value(item) for item in v)
            elif isinstance(v, dict):
                return {k: process_value(val) for k, val in v.items()}
            else:
                # For other types, use converter.unstructure
                # This should work since v is not an Envelope
                return converter.unstructure(v)

        # Process all values to handle nested Envelopes and other complex types
        result = {k: process_value(v) for k, v in result.items()}
        # Add type tag at the end
        result["_type"] = type(env).__name__
        return result

    def structure_envelope(obj: dict, _: type) -> Envelope:
        """Structure an Envelope from a dict using the type tag."""
        if not isinstance(obj, dict):
            raise ValueError(f"Expected dict for Envelope, got {type(obj)}")

        type_name = obj.get("_type")
        if type_name is None:
            raise ValueError("Envelope dict missing '_type' field")

        # Map type names to classes
        # TODO: Allow serialization of CallableEnvelope (e.g., by serializing function source)
        type_map = {
            "SquareEnvelope": SquareEnvelope,
            "PiecewiseEnvelope": PiecewiseEnvelope,
        }

        env_class = type_map.get(type_name)
        if env_class is None:
            if type_name == "CallableEnvelope":
                raise ValueError(
                    "CallableEnvelope cannot be serialized as it contains a callable. "
                    "TODO: Implement serialization of CallableEnvelope."
                )
            raise ValueError(f"Unknown Envelope type: {type_name}")

        # Create a dict without the type tag for structuring
        obj_without_tag = {k: v for k, v in obj.items() if k != "_type"}

        # Structure the envelope by structuring as the concrete type
        # We need to bypass the Envelope hook to avoid recursion when structuring subclasses
        # Since env_class (e.g., SquareEnvelope) is a subclass of Envelope,
        # converter.structure() will match the Envelope hook again, causing recursion.
        # Solution: Manually structure the fields and construct the instance
        if attrs.has(env_class):
            # For attrs classes, manually structure each field and construct the instance
            structured_fields = {}
            for attr_field in attrs.fields(env_class):
                field_value = obj_without_tag.get(attr_field.name)
                if field_value is not None:
                    # Structure the field value using the converter
                    # Handle type aliases and union types by trying each member
                    from typing import Union, get_args, get_origin

                    field_type = attr_field.type

                    # Check if it's a union type or type alias that resolves to a union
                    resolved = False
                    if hasattr(field_type, '__origin__') or hasattr(field_type, '__args__'):
                        origin = get_origin(field_type) if hasattr(field_type, '__origin__') else None
                        args = get_args(field_type) if hasattr(field_type, '__args__') else ()
                        # If it's a union type, try each member
                        if origin is Union or (hasattr(field_type, '__origin__') and get_origin(field_type) is Union):
                            # Try each union member
                            for union_member in args:
                                try:
                                    structured_fields[attr_field.name] = converter.structure(field_value, union_member)
                                    resolved = True
                                    break
                                except Exception:
                                    continue

                    if not resolved:
                        # Try structuring with the field type as-is
                        try:
                            structured_fields[attr_field.name] = converter.structure(field_value, field_type)
                        except Exception:
                            # If that fails and it's a dict with _type, it's likely a tagged union
                            # Let the converter figure it out by checking _type
                            if isinstance(field_value, dict) and "_type" in field_value:
                                # For tagged unions, we need to structure based on _type
                                # For example, if _type is "Literal", structure as Quantity
                                type_name = field_value.get("_type")
                                if type_name == "Literal":
                                    structured_fields[attr_field.name] = converter.structure(field_value, pint.Quantity)
                                else:
                                    # Unknown tagged type, try the original field type
                                    structured_fields[attr_field.name] = field_value
                            else:
                                # Value might already be structured, use as-is
                                structured_fields[attr_field.name] = field_value
                elif attr_field.default is not attrs.NOTHING:
                    # Use the default value
                    structured_fields[attr_field.name] = attr_field.default
                elif attr_field.default_factory is not None:
                    # Use the default factory
                    structured_fields[attr_field.name] = attr_field.default_factory()
            return env_class(**structured_fields)
        else:
            # For non-attrs classes, use converter.structure (shouldn't happen for our Envelopes)
            return converter.structure(obj_without_tag, env_class)

    # Register hooks for the Envelope union
    converter.register_unstructure_hook(Envelope, unstructure_envelope_with_tag)
    converter.register_structure_hook(Envelope, structure_envelope)

    def unstructure_pulse_with_tag(pulse: Pulse) -> dict:
        """Unstructure a Pulse, adding a type tag."""
        # ChannelMappedPulse shouldn't be serialized
        if isinstance(pulse, ChannelMappedPulse):
            raise ValueError("ChannelMappedPulse cannot be serialized. Only unmapped PulsePrograms can be serialized.")
        result = converter.unstructure(pulse, unstructure_as=type(pulse))
        result["_type"] = type(pulse).__name__
        return result

    def structure_pulse(obj: dict, _: type) -> Pulse:
        """Structure a Pulse from a dict using the type tag."""
        if not isinstance(obj, dict):
            raise ValueError(f"Expected dict for Pulse, got {type(obj)}")

        type_name = obj.get("_type")
        if type_name is None:
            raise ValueError("Pulse dict missing '_type' field")

        # Map type names to classes (excluding ChannelMappedPulse)
        type_map = {
            # Leaf pulses
            "DelayPulse": DelayPulse,
            "LaserPulse": LaserPulse,
            "DrivePulse": DrivePulse,
            "AcquisitionPulse": AcquisitionPulse,
            # Container pulses
            "SequencePulse": SequencePulse,
            "ParallelPulse": ParallelPulse,
            "ForLoopPulse": ForLoopPulse,
        }

        pulse_class = type_map.get(type_name)
        if pulse_class is None:
            if type_name == "ChannelMappedPulse":
                raise ValueError(
                    "ChannelMappedPulse cannot be deserialized. Only unmapped PulsePrograms can be serialized."
                )
            raise ValueError(f"Unknown Pulse type: {type_name}")

        # Create a dict without the type tag for structuring
        obj_without_tag = {k: v for k, v in obj.items() if k != "_type"}

        return converter.structure(obj_without_tag, pulse_class)

    # Register hooks for the Pulse union (excluding ChannelMappedPulse)
    converter.register_unstructure_hook(Pulse, unstructure_pulse_with_tag)
    converter.register_structure_hook(Pulse, structure_pulse)

    # Also register for LeafPulse and ContainerPulse unions
    converter.register_unstructure_hook(LeafPulse, unstructure_pulse_with_tag)
    converter.register_structure_hook(LeafPulse, structure_pulse)
    converter.register_unstructure_hook(ContainerPulse, unstructure_pulse_with_tag)
    converter.register_structure_hook(ContainerPulse, structure_pulse)


def create_converter() -> Converter:
    """Create and configure a Converter for PulseProgram serialization."""
    converter = Converter()
    configure_converter(converter)
    return converter
