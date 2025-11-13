from typing import Any

import pint
from pint import Quantity as PintQuantity
from pint import Unit as PintUnit
from pint.facets.plain import PlainUnit

unit = pint.UnitRegistry()
pint.set_application_registry(unit)

Unit = PintUnit | PlainUnit
Quantity = PintQuantity
