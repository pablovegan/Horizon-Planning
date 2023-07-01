"""
Dataclasses to save the economy and the planned economy returned by the optimizer.
The Economy class is implemented using Pydantic to perform certain checks in
the data, which will normally come from a database, making it prone to mistakes
when loading the data.

Classes:
    ShapesNotEqualError
    ShapeError
    Economy
    PlannedEconomy
"""

from __future__ import annotations

import logging
from typing import Any
from dataclasses import dataclass, field

from numpy.typing import NDArray
from scipy.sparse import spmatrix
from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class ShapesNotEqualError(ValueError):
    """The shapes of the matrices difer."""

    def __init__(self) -> None:
        super().__init__("The shapes of the matrices in the same list differ.\n\n")


class ShapeError(ValueError):
    """The shapes of different matrices of the economy don't match."""

    def __init__(self, shape: tuple[int, int], desired_shape: tuple[int, int]) -> None:
        message = f"Shape is {shape}, instead of {desired_shape}.\n\n"
        logging.error(message)
        super().__init__(message)


ECONOMY_FIELDS = {
    "supply",
    "use_domestic",
    "use_import",
    "depreciation",
    "final_domestic",
    "final_export",
    "final_import",
    "prices_import",
    "prices_export",
    "worked_hours",
}


MatrixList = list[NDArray] | list[spmatrix]


class Economy(BaseModel):
    """Dataclass with validations that stores the whole economy's information."""

    model_config = dict(arbitrary_types_allowed=True)

    supply: list[NDArray] | list[spmatrix]
    use_domestic: list[NDArray] | list[spmatrix]
    use_import: list[NDArray] | list[spmatrix]
    depreciation: list[NDArray] | list[spmatrix]
    final_domestic: list[NDArray] | list[spmatrix]
    final_export: list[NDArray] | list[spmatrix]
    final_import: list[NDArray] | list[spmatrix]
    prices_import: list[NDArray] | list[spmatrix]
    prices_export: list[NDArray] | list[spmatrix]
    worked_hours: list[NDArray] | list[spmatrix]
    product_names: list[str] = ...
    sector_names: list[str] = ...

    @field_validator(*ECONOMY_FIELDS)
    def equal_shapes(cls, matrices: MatrixList, info: FieldValidationInfo) -> MatrixList:
        """Assert that all the inputed matrices have the same shape."""
        shapes = [matrix.shape for matrix in matrices]
        if not all([shape == shapes[0] for shape in shapes]):
            raise ShapesNotEqualError
        logging.info(f"{info.field_name} has shape {shapes[0]}")
        return matrices

    @field_validator(*ECONOMY_FIELDS)
    def equal_periods(cls, matrices: MatrixList, info: FieldValidationInfo) -> MatrixList:
        if "supply" in info.data and len(matrices) != len(info.data["supply"]):
            raise ValueError(
                f"\n{info.field_name} and supply don't have the same number of time periods.\n\n"
            )
        return matrices

    def model_post_init(self, __context: Any) -> None:
        """Run after initial validation. Validates that the shapes of the
        matrices are compatible with each other (same number of products
        and sectors).
        """

        self.validate_matrix_shape(
            self.use_domestic[0], self.use_import[0], shape=(self.products, self.sectors)
        )
        self.validate_matrix_shape(self.depreciation[0], shape=(self.products, self.products))
        self.validate_matrix_shape(
            self.final_domestic[0],
            self.final_export[0],
            self.prices_import[0],
            self.prices_export[0],
            shape=(self.products,),
        )
        self.validate_matrix_shape(self.worked_hours[0], shape=(self.sectors,))

        if self.product_names is not ... and len(self.product_names) != self.products:
            raise ValueError(f"\nList of PRODUCT names must be of length {self.products}.\n\n")

        if self.sector_names is not ... and len(self.product_names) != self.products:
            raise ValueError(f"\nList of SECTOR names must be of length {self.sectors}.\n\n")

    @staticmethod
    def validate_matrix_shape(*matrices: MatrixList, shape: tuple[int, int]) -> None:
        """Assert that all the inputed matrices have the same shape."""
        for matrix in matrices:
            if matrix.shape != shape:
                raise ShapeError(shape, matrix.shape)

    @property
    def products(self) -> int:
        """Number of products in the economy."""
        return self.supply[0].shape[0]

    @property
    def sectors(self) -> int:
        """Number of products in the economy."""
        return self.supply[0].shape[1]


@dataclass
class PlannedEconomy:
    """Dataclass that stores the whole planned economy.

    Args:
        activity (list[NDArray]): list with the planned activity for all sectors
            in each period.
        production (list[NDArray]): list with the planned production for all product
            in each period.
        surplus (list[NDArray]): The surplus production at the end of each period.
        total_import (list[NDArray]): list of total imports in each period.
        export_deficit (list[float]): list export deficit at the end of each period.
        worked_hours (list[float]): list of total worked hours in each period.
    """

    activity: list[NDArray] = field(default_factory=list)
    production: list[NDArray] = field(default_factory=list)
    surplus: list[NDArray] = field(default_factory=list)
    total_import: list[NDArray] = field(default_factory=list)
    export_deficit: list[float] = field(default_factory=list)
    worked_hours: list[float] = field(default_factory=list)
