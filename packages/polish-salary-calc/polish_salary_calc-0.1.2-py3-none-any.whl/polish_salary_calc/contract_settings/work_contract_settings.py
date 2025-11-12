
from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from typing import TypedDict, Self, Unpack
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class WorkContractType(Enum):
    """Type of employment contract for determining social insurance handling
    and cost deduction rules."""
    COMMON = 0
    THE_SAME_COMPANY = 1

class WorkContractOptionsDict(TypedDict):
    """Dictionary representation of `WorkContractSettings`.

    Keys:
        work_contract_type: WorkContractType
            Type of the employment contract.
        is_fifty: bool
            Whether 50% author rights cost deduction is applied.
        is_a_lump_sum: bool
            Whether lump-sum taxation applies (ryczałt).
    """
    work_contract_type: WorkContractType
    is_fifty: bool
    is_a_lump_sum:bool #ryczałt


@dataclass
class WorkContractSettings(ContractSettngs):
    """Configuration object for calculating salary under a work (employment) contract.

    Extends:
        ContractSettngs: Base class that stores shared salary computation parameters.

    Attributes:
        work_contract_type (WorkContractType):
            Whether the employee works for the same company or a common case.
            Affects social insurance base computation rules.
        is_fifty (bool):
            Indicates whether 50% author's cost deduction should be applied.
        is_a_lump_sum (bool):
            Indicates whether lump-sum (ryczałt) taxation applies.
    """
    work_contract_type: WorkContractType = WorkContractType.COMMON
    is_fifty: bool = False
    is_a_lump_sum: bool = False

    def to_dict(self) ->Unpack[WorkContractOptionsDict]:
        """Return the settings as a dictionary.

        Returns:
            dict: Dictionary representation that matches `WorkContractOptionsDict`.
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, data: WorkContractOptionsDict) -> Self:
        """Create a `WorkContractSettings` object from a dictionary.

         Args:
             data (WorkContractOptionsDict): A settings dictionary, typically read from a saved config.

         Returns:
             WorkContractSettings: New settings instance populated with provided data.
         """
        return cls(**data)

    @classmethod
    def builder(cls) -> 'SettingsBuilder':
        """Return a builder object for fluent-style configuration.

        Returns:
            SettingsBuilder: Builder instance for constructing `WorkContractSettings`.
        """
        return cls.SettingsBuilder()

    class SettingsBuilder:
        """Fluent builder for `WorkContractSettings`.

        Usage:
            settings = (WorkContractSettings.builder()
                .set_work_contract_type(WorkContractType.THE_SAME_COMPANY)
                .is_fifty(True)
                .set_tax_base_sum(Decimal('15000'))
                .build()
            )
        """
        def __init__(self):
            self._options = WorkContractSettings()

        def set_work_contract_type(self, work_contract_type: WorkContractType) -> Self:
            """Set the contract type."""
            self._options.work_contract_type = work_contract_type
            return self

        def is_fifty(self, is_fifty: bool) -> Self:
            """Enable or disable 50% author's cost deduction."""
            self._options.is_fifty = is_fifty
            return self

        def  is_a_lump_sum(self,  is_a_lump_sum: bool) -> Self:
            """Enable or disable lump-sum taxation (ryczałt)."""
            self._options. is_a_lump_sum =  is_a_lump_sum
            return self

        def set_social_security_base_sum(self, social_security_base_sum: Decimal) -> Self:
            """Set cumulative social security contribution base (used for annual caps)."""
            self._options.social_security_base_sum = social_security_base_sum
            return self

        def set_cost_fifty_sum(self, cost_fifty_sum: Decimal) -> Self:
            """Set cumulative value of already applied 50% author's cost deductions."""
            self._options.cost_fifty_sum = cost_fifty_sum
            return self

        def set_tax_base_sum(self, tax_base_sum: Decimal) -> Self:
            """Set cumulative taxable income (used for progressive thresholds)."""
            self._options.tax_base_sum = tax_base_sum
            return self

        def set_employee_ppk(self, employee_ppk: Decimal) -> Self:
            """Set employee's PPK fund contribution percentage."""
            self._options.employee_ppk = employee_ppk
            return self

        def set_employer_ppk(self, employer_ppk: Decimal) -> Self:
            """Set employer's PPK fund contribution percentage."""
            self._options.employer_ppk = employer_ppk
            return self

        def set_salary_deductions(self, salary_deductions: Decimal) -> Self:
            """Set fixed salary deductions (applied before taxation)."""
            self._options.salary_deductions = salary_deductions
            return self

        def set_name(self,name: str) -> Self:
            """Set optional contract label (for UI or logs)."""
            self._options.name = name
            return self

        def build(self) -> 'WorkContractSettings':
            """Finalize and return the settings instance."""
            return self._options