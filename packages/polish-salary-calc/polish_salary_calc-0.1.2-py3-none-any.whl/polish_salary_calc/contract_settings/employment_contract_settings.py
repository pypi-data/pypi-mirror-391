from typing import TypedDict, Self, Unpack
from dataclasses import dataclass
from decimal import Decimal

from polish_salary_calc.contract_settings.contract_settings import ContractSettngs


class EmploymentContractDict(TypedDict):
    """
    Serializable representation of EmploymentContractSettings used for exporting
    and reconstructing settings (e.g., saving to JSON, passing between calculation
    components, or storing configuration snapshots).

    Fields:
        increased_costs: Whether the taxpayer applies standard increased employee cost deduction.
        cost_fifty_ratio: Ratio defining how much of the income is treated as 50% tax-deductible costs.
        fp_fgsp: Determines whether contributions to FP and FGŚP are calculated.
        active_business: Whether the employee is simultaneously running a business affecting ZUS basis rules.
        under_26: If True, eligible for income tax exemption under PIT-0 for under-26 employees.
        sick_pay: Employer-funded sickness benefit base (for absence calculations).
        current_month_gross_sum: Year-to-date gross income accumulator.
        social_security_base_sum: Running ZUS contribution calculation base for ZUS limit tracking.
        cost_fifty_sum: Accumulator controlling use of the 50% cost limit.
        tax_base_sum: Progressive tax accumulation (used to determine PIT threshold transitions).
        employee_ppk: Accumulated PPK employee contributions.
        employer_ppk: Accumulated PPK employer contributions.
        accident_insurance_rate: Optional accident insurance contribution rate.
        salary_deductions: Any post-tax deductions from net salary.
        name: Optional identifier used in reporting/export.
    """
    increased_costs: bool
    cost_fifty_ratio: Decimal
    fp_fgsp: bool
    active_business: bool
    under_26: bool
    sick_pay: Decimal
    current_month_gross_sum: Decimal
    social_security_base_sum: Decimal
    cost_fifty_sum: Decimal
    tax_base_sum: Decimal
    employee_ppk: Decimal
    employer_ppk: Decimal
    accident_insurance_rate: Decimal | None
    salary_deductions: Decimal
    name: str

@dataclass
class EmploymentContractSettings(ContractSettngs):
    """
    Configuration state for Employment Contract (Umowa o pracę) calculations.
    This class stores taxpayer attributes that modify payroll rules as well as
    cumulative year-to-date values required to correctly apply Polish tax and
    social security thresholds.

    Extends:
        ContractSettngs — provides shared accumulators and export utilities.

    Key parameters:
        increased_costs: Whether to apply standard employee cost deduction.
        cost_fifty_ratio: Percentage (0.0–1.0) of income eligible for 50% tax-deductible costs.
        fp_fgsp: Include FP / FGŚP employer contributions.
        active_business: Determines contribution coordination rules for individuals also running a business.
        under_26: Whether PIT-0 exemption applies.
        sick_pay: Monthly sickness benefit entitlement.
    """
    increased_costs: bool = False
    cost_fifty_ratio: Decimal = Decimal('0.0')
    fp_fgsp: bool = False
    active_business: bool = False
    under_26: bool = False
    sick_pay: Decimal = Decimal('0.0')
    # current_month_gross_sum: Decimal = Decimal('0.0')
    # social_security_base_sum: Decimal = Decimal('0.0')
    # cost_fifty_sum: Decimal = Decimal('0.0')
    # tax_base_sum: Decimal = Decimal('0.0')
    # employee_ppk: Decimal = Decimal('0.0')
    # employer_ppk: Decimal = Decimal('0.0')
    # accident_insurance_rate: Decimal | None = None

    def to_dict(self) ->Unpack[EmploymentContractDict]:
        """
        Convert settings to a serializable dictionary representation.

        Returns:
            EmploymentContractDict: A copy of the instance state suitable for
            storage, logging, or transmitting between salary calculation modules.
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, data: EmploymentContractDict) -> Self:
        """
        Reconstruct a settings object from a previously exported dictionary.

        Args:
            data: Dictionary produced by `to_dict()` or `to_exporter_dict()`.

        Returns:
            EmploymentContractSettings: Restored settings instance.
        """
        return cls(**data)

    @classmethod
    def builder(cls) -> 'SettingsBuilder':
        """
        Create a builder instance to allow fluent configuration.

        Returns:
            SettingsBuilder: Builder object for controlled attribute assignment.
        """
        return cls.SettingsBuilder()

    class SettingsBuilder:
        """
        Fluent builder for EmploymentContractSettings. Enables constructing
        settings objects step-by-step without requiring large constructors.

        Example:
            settings = (
                EmploymentContractSettings.SettingsBuilder()
                    .is_increased_costs(True)
                    .set_cost_fifty_ratio(Decimal('0.5'))
                    .is_under_26(True)
                    .set_name("Employee A")
                    .build()
            )
        """
        def __init__(self):
            self._options = EmploymentContractSettings()

        def is_increased_costs(self, increased_costs: bool) -> Self:
            self._options.increased_costs = increased_costs
            return self

        def set_cost_fifty_ratio(self, cost_fifty_ratio: Decimal) -> Self:
            self._options.cost_fifty_ratio = cost_fifty_ratio
            return self

        def is_fp_fgsp(self, is_fp_fgsp: bool) -> Self:
            self._options.fp_fgsp = is_fp_fgsp
            return self

        def is_active_business(self, active_business: bool) -> Self:
            self._options.active_business = active_business
            return self

        def is_under_26(self, under_26: bool) -> Self:
            self._options.under_26 = under_26
            return self

        def set_sick_pay(self, sick_pay: Decimal) -> Self:
            self._options.sick_pay = sick_pay
            return self

        def set_current_month_gross_sum(self, current_month_gross_sum: Decimal) -> Self:
            self._options.current_month_gross_sum = current_month_gross_sum
            return self

        def set_social_security_base_sum(self, social_security_base_sum: Decimal) -> Self:
            self._options.social_security_base_sum = social_security_base_sum
            return self

        def set_cost_fifty_sum(self, cost_fifty_sum: Decimal) -> Self:
            self._options.cost_fifty_sum = cost_fifty_sum
            return self

        def set_tax_base_sum(self, tax_base_sum: Decimal) -> Self:
            self._options.tax_base_sum = tax_base_sum
            return self

        def set_employee_ppk(self, employee_ppk: Decimal) -> Self:
            self._options.employee_ppk = employee_ppk
            return self

        def set_employer_ppk(self, employer_ppk: Decimal) -> Self:
            self._options.employer_ppk = employer_ppk
            return self

        def set_accident_insurance_rate(self, accident_insurance_rate: Decimal | None) -> Self:
            self._options.accident_insurance_rate = accident_insurance_rate
            return self

        def set_salary_deductions(self, salary_deductions: Decimal) -> Self:
            self._options.salary_deductions = salary_deductions
            return self

        def set_name(self,name: str) -> Self:
            self._options.name = name
            return self

        def build(self) -> 'EmploymentContractSettings':
            """
            Finalize and return the constructed settings object.

            Returns:
                EmploymentContractSettings: The configured instance.
            """
            return self._options