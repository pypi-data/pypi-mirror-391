from __future__ import annotations

import builtins
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, overload, runtime_checkable

import pint
from attrs import field, frozen, validators
from typing_extensions import assert_never, override

from xq_pulse.util import Quantity, Unit, unit

Literal = Quantity
if TYPE_CHECKING:
    from xq_pulse.pulse.pulse import Pulse


@runtime_checkable
class Parameterized(Protocol):
    """
    Anything that can depend on Parameters. Generally pulses or expressions.
    """

    @abstractmethod
    def bind(self, binding: Binding) -> Parameterized | Literal: ...

    @property
    @abstractmethod
    def parameters(self) -> frozenset[Parameter]:
        """
        Return the set of Parameters that this Bindable depends on.
        """
        # TODO: Since all Bindables are frozen, this can be memoized / calculated in __init__.
        ...

    @property
    def is_bound(self) -> bool:
        """
        Check if this Bindable is bound to a specific set of parameters.
        This is a convenience method that checks if the parameters set is empty.
        """
        return len(self.parameters) == 0

    @abstractmethod
    def simplify(self) -> Parameterized | Literal:
        """
        Recursively transform this DSL tree into an equivalent simpler form.
        """
        ...


@overload
def simplify(expr: Literal) -> Literal: ...
@overload
def simplify(expr: Expression) -> Expression: ...
def simplify(expr: Parameterized | Literal) -> Parameterized | Literal:
    if isinstance(expr, Literal):
        return expr
    return expr.simplify()


class AnyExpression(ABC):
    """
    Abstract base class for Expressions (including Parameters but not Literals).
    Used to implement operator overloads.
    Only use this for inheritance.
    For type annotations, use Expression, which is a union type and supports compile time exhaustiveness checking.
    """

    @property
    @abstractmethod
    def units(self) -> Unit:
        """
        Return the unit of this expression.
        Property name is identical to pint.Quantity.units, so all Expressions share the units property.
        """
        ...

    def __add__(self, other: Expression) -> SumExpression:
        return SumExpression(self, other)

    def __radd__(self, other: Expression) -> SumExpression:
        return SumExpression(other, self)

    def __sub__(self, other: Expression) -> DifferenceExpression:
        return DifferenceExpression(self, other)

    def __mul__(self, other: Expression) -> ProductExpression:
        return ProductExpression(self, other)

    def __rmul__(self, other: Expression) -> ProductExpression:
        return ProductExpression(other, self)

    def __truediv__(self, other: Expression | float | int) -> QuotientExpression:
        if isinstance(other, (float, int)):
            other = other * unit.dimensionless
        return QuotientExpression(self, other)


@frozen
class Parameter(Parameterized, AnyExpression):
    name: str  # TODO: Is this necessary?
    unit: Unit = field(repr=str, validator=validators.instance_of(Unit))

    @property
    @override
    def units(self) -> Unit:
        return self.unit

    def bind(self, binding: Binding) -> Expression:
        if self in binding:
            return binding[self]
        else:
            return self

    @property
    @override
    def parameters(self) -> frozenset[Parameter]:
        return frozenset({self})

    @override
    def simplify(self) -> Expression | Literal:
        return self


Binding = dict[Parameter, Literal]


class ExpressionUnitValidator:
    """
    A validators for attrs to check a given AnyExpression has a compatible unit.
    """

    def __init__(self, unit: Unit):
        self.unit = unit

    def __call__(self, _, __, param):
        assert isinstance(param, AnyExpression), f"Value {param} of type {type(param).__name__} is not an AnyExpression"
        assert param.units.is_compatible_with(self.unit), (
            f"Parameter with unit {param.units} is not compatible with unit {self.unit}"
        )

    def __repr__(self):
        return f"<Validator for AnyExpression with unit {self.unit}>"


@frozen
class SumExpression(Parameterized, AnyExpression):
    lhs: Expression
    rhs: Expression

    @property
    @override
    def units(self) -> Unit:
        assert self.lhs.units.is_compatible_with(self.rhs.units), (
            f"SumExpression has incompatible types lhs: {self.lhs.units} and rhs: {self.rhs.units}."
        )
        return self.lhs.units

    def bind(self, binding: Binding) -> Expression:
        return SumExpression(
            lhs=bind(self.lhs, binding),
            rhs=bind(self.rhs, binding),
        )

    @property
    def parameters(self) -> frozenset[Parameter]:
        lhs_params = self.lhs.parameters if not is_literal(self.lhs) else frozenset()
        rhs_params = self.rhs.parameters if not is_literal(self.rhs) else frozenset()
        return frozenset.union(lhs_params, rhs_params)

    @override
    def simplify(self) -> Expression | Literal:
        if self.is_bound:
            return eval_expression(self)
        return self


def sum(*args: Expression) -> Expression:
    assert len(args) > 0, "At least one argument is required"
    if len(args) == 1:
        return args[0]
    elif all(is_bound(expr) for expr in args):
        return builtins.sum(eval_expression(arg) for arg in args)
    else:
        return SumExpression(lhs=args[0], rhs=sum(*args[1:]))


@frozen
class DifferenceExpression(Parameterized, AnyExpression):
    lhs: Expression
    rhs: Expression

    @property
    @override
    def units(self) -> Unit:
        assert self.lhs.units.is_compatible_with(self.rhs.units), (
            f"DifferenceExpression has incompatible types lhs: {self.lhs.units} and rhs: {self.rhs.units}."
        )
        return self.lhs.units

    def bind(self, binding: Binding) -> Expression:
        return DifferenceExpression(
            lhs=bind(self.lhs, binding),
            rhs=bind(self.rhs, binding),
        )

    @property
    def parameters(self) -> frozenset[Parameter]:
        lhs_params = self.lhs.parameters if not is_literal(self.lhs) else frozenset()
        rhs_params = self.rhs.parameters if not is_literal(self.rhs) else frozenset()
        return frozenset.union(lhs_params, rhs_params)

    @override
    def simplify(self) -> Expression | Literal:
        if self.is_bound:
            return eval_expression(self)
        return self


@frozen
class ProductExpression(Parameterized, AnyExpression):
    lhs: Expression
    rhs: Expression

    @property
    @override
    def units(self) -> Unit:
        expr_unit = self.lhs.units * self.rhs.units
        assert isinstance(expr_unit, pint.Unit), (
            f"Multiplying {self.lhs.units} by {self.rhs.units} did not yield a pint.Unit but {type(expr_unit)}: {expr_unit}"
        )
        return expr_unit

    def bind(self, binding: Binding) -> Expression:
        return ProductExpression(
            lhs=bind(self.lhs, binding),
            rhs=bind(self.rhs, binding),
        )

    @property
    def parameters(self) -> frozenset[Parameter]:
        lhs_params = self.lhs.parameters if not is_literal(self.lhs) else frozenset()
        rhs_params = self.rhs.parameters if not is_literal(self.rhs) else frozenset()
        return frozenset.union(lhs_params, rhs_params)

    @override
    def simplify(self) -> Expression | Literal:
        if self.is_bound:
            return eval_expression(self)
        return self


@frozen
class QuotientExpression(Parameterized, AnyExpression):
    lhs: Expression
    rhs: Expression

    @property
    @override
    def units(self) -> Unit:
        expr_unit = self.lhs.units / self.rhs.units
        assert isinstance(expr_unit, pint.Unit), (
            f"Dividing {self.lhs.units} by {self.rhs.units} did not yield a pint.Unit but {type(expr_unit)}: {expr_unit}"
        )
        return expr_unit

    def bind(self, binding: Binding) -> Expression:
        return QuotientExpression(
            lhs=bind(self.lhs, binding),
            rhs=bind(self.rhs, binding),
        )

    @property
    def parameters(self) -> frozenset[Parameter]:
        lhs_params = self.lhs.parameters if not is_literal(self.lhs) else frozenset()
        rhs_params = self.rhs.parameters if not is_literal(self.rhs) else frozenset()
        return frozenset.union(lhs_params, rhs_params)

    @override
    def simplify(self) -> Expression | Literal:
        if self.is_bound:
            return eval_expression(self)
        return self


@frozen
class MaximumExpression(Parameterized, AnyExpression):
    lhs: Expression
    rhs: Expression

    @property
    @override
    def units(self) -> Unit:
        assert self.lhs.units.is_compatible_with(self.rhs.units), (
            f"MaxExpression has incompatible types lhs: {self.lhs.units} and rhs: {self.rhs.units}."
        )
        return self.lhs.units

    def bind(self, binding: Binding) -> Expression:
        return MaximumExpression(
            lhs=bind(self.lhs, binding),
            rhs=bind(self.rhs, binding),
        )

    @property
    def parameters(self) -> frozenset[Parameter]:
        lhs_params = self.lhs.parameters if not is_literal(self.lhs) else frozenset()
        rhs_params = self.rhs.parameters if not is_literal(self.rhs) else frozenset()
        return frozenset.union(lhs_params, rhs_params)

    @override
    def simplify(self) -> Expression | Literal:
        if self.is_bound:
            return eval_expression(self)
        return self


def max(*args: Expression) -> Expression:
    assert len(args) > 0, "At least one argument is required"
    if len(args) == 1:
        return args[0]
    else:
        return MaximumExpression(lhs=args[0], rhs=max(*args[1:]))


def is_literal(expression: Expression) -> bool:
    """Return True if the expression is a literal quantity."""
    return isinstance(expression, Quantity)


def is_bound(expression: Expression) -> bool:
    return isinstance(expression, Quantity) or expression.is_bound


Expression = (
    Literal
    | Parameter
    | SumExpression
    | DifferenceExpression
    | ProductExpression
    | MaximumExpression
    | QuotientExpression
)


@overload
def bind(bindable: Literal, binding: Binding) -> Literal: ...
@overload
def bind(bindable: Expression, binding: Binding) -> Expression: ...
@overload
def bind(bindable: Pulse, binding: Binding) -> Pulse: ...
def bind(bindable: Parameterized | Literal, binding: Binding) -> Parameterized | Literal:
    """
    Wrapper around the bind method which also works for literal quantities.
    """
    match bindable:
        case Quantity():
            return bindable
        case Parameterized():
            return bindable.bind(binding)
        case _:
            assert_never(bindable)


def eval_expression(expression: Expression) -> Literal:
    """
    Evaluate the expression to a literal value.
    """
    assert is_bound(expression), (
        f"Expression cannot be evaluated because it has free parameters: {expression.parameters}"
    )
    match expression:
        case Quantity():
            return expression
        case Parameter():
            assert False, "Cannot evaluate Parameter. This should be unreachable due to the is_bound assertion"
        case SumExpression(lhs, rhs):
            return eval_expression(lhs) + eval_expression(rhs)
        case DifferenceExpression(lhs, rhs):
            return eval_expression(lhs) - eval_expression(rhs)
        case ProductExpression(lhs, rhs):
            return eval_expression(lhs) * eval_expression(rhs)
        case QuotientExpression(lhs, rhs):
            return eval_expression(lhs) / eval_expression(rhs)
        case MaximumExpression(lhs, rhs):
            return builtins.max(eval_expression(lhs), eval_expression(rhs))
        case _:
            assert_never(expression)
