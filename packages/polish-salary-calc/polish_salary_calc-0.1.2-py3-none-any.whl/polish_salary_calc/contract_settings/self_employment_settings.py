
from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from typing import TypedDict, Self, Unpack
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, IntEnum


class SelfEmploymentType(Enum):
    """
    Enumeration describing self-employment insurance regime variants in Poland.

    Attributes:
        COMMON:
            Full ZUS contributions ("pełny ZUS").
        PREFERRED:
            Reduced ZUS contributions for new entrepreneurs ("mały ZUS preferencyjny").
        STARTUP_RELIEF:
            Start-up exemption: no social contributions for 6 months ("ulga na start").
        UNREGISTERED_BUSINESS:
            Unregistered business activity ("działalność nierejestrowana"):
            No contributions and no formal registration required under revenue threshold.
    """
    COMMON = 1
    PREFERRED = 2
    STARTUP_RELIEF = 3
    UNREGISTERED_BUSINESS = 4
    #SMALL_ZUS = 5

class TaxType(Enum):
    """
    Enumeration describing the form of income taxation for self-employment.

    Attributes:
        STANDARD:
            Progressive PIT rate (12% / 32%).
        LINE_TAX:
            Linear taxation 19%.
        A_LUMP_SUM:
            Lump-sum taxation ("ryczałt") based on sector-specific tax rate.
    """
    STANDARD = 1
    LINE_TAX = 2
    A_LUMP_SUM = 3

class HealthBase(IntEnum):
    """
    Enumeration representing health insurance base tiers for predictable lump-sum
    taxation or rate-based healthcare contributions.

    These represent government-defined thresholds.
    """
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

LUMP_RATES_ALLOWED ={
    Decimal('0.02'),Decimal('0.03'),Decimal('0.055'),Decimal('0.085'),Decimal('0.10'),Decimal('0.12'),Decimal('0.14'),Decimal('0.15'),Decimal('0.17')
}

class SelfEmploymentOptionsDict(TypedDict):
    """
    Typed dictionary describing configuration parameters for self-employment
    tax and social contribution calculation.

    Each key corresponds to a field in SelfEmploymentSettings.
    """
    self_employment_type: SelfEmploymentType
    tax_type: TaxType
    tax_lump_rate: Decimal
    health_base: HealthBase
    # employer_pension_contribution_rate: Decimal
    is_sick_pay: bool
    sick_pay_days: int
    month_days: int
    is_fp:bool
    other_minimum_contract:bool
    # average_social_income_previous_year:Decimal
    #is_a_lump_sum: bool
    costs: Decimal

@dataclass
class SelfEmploymentSettings(ContractSettngs):
    """
    Configuration container for calculating tax and social contributions
    for self-employed individuals.

    Extends ContractSettngs with additional fields relevant for:
    - ZUS scheme selection,
    - form of income taxation,
    - lump-sum tax rate selection,
    - optional sickness insurance,
    - supplemental social contribution rules.

    Attributes:
        self_employment_type:
            Determines which ZUS contribution scheme applies.
        tax_type:
            Determines the taxing regime (PIT, linear, lump sum).
        tax_lump_rate:
            Lump-sum tax rate (only if tax_type = A_LUMP_SUM).
        health_base:
            Health insurance contribution base range.
        is_sick_pay:
            Whether voluntary sickness insurance is enabled.
        sick_pay_days:
            Number of sick-leave days in the current month.
        month_days:
            Number of days in the settlement month.
        is_fp:
            Whether Labor Fund contributions apply.
        other_minimum_contract:
            Indicates whether taxpayer is simultaneously covered by another contract at minimum wage.
        costs:
            Tax-deductible business expenses amount.
    """
    self_employment_type: SelfEmploymentType = SelfEmploymentType.COMMON
    tax_type: TaxType = TaxType.STANDARD
    tax_lump_rate: Decimal = Decimal('0.17')
    health_base: HealthBase = HealthBase.NONE
    is_sick_pay: bool = False
    sick_pay_days: int = 0
    month_days: int = 0
    is_fp:bool = True
    other_minimum_contract:bool = False
    # average_social_income_previous_year:Decimal= Decimal('0.0')
    #is_a_lump_sum: bool = False
    costs: Decimal = Decimal('0.0')

    def to_dict(self) ->Unpack[SelfEmploymentOptionsDict]:
        """
        Return configuration as a TypedDict representation.

        Returns:
            dict: A dictionary mapping field names to their values.
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, data: SelfEmploymentOptionsDict) -> Self:
        """
        Construct configuration from dictionary data.

        Args:
            data: TypedDict containing configuration values.

        Returns:
            SelfEmploymentSettings: Populated instance.
        """
        return cls(**data)

    @classmethod
    def builder(cls) -> 'SettingsBuilder':
        """
        Create a fluent builder for this configuration.

        Returns:
            SettingsBuilder
        """
        return cls.SettingsBuilder()

    class SettingsBuilder:
        """
        Fluent builder for SelfEmploymentSettings.

        Provides a chained configuration interface, enabling readable construction:

            settings = (SelfEmploymentSettings.SettingsBuilder()
                            .set_self_employment_type(SelfEmploymentType.PREFERRED)
                            .set_tax_type(TaxType.A_LUMP_SUM)
                            .set_tax_lump_rate(Decimal('0.085'))
                            .set_health_base(HealthBase.MEDIUM)
                            .set_costs(Decimal('450.00'))
                            .set_name("Freelance designer")
                            .build())
        """
        def __init__(self):
            """Initialize builder with default configuration."""
            self._options = SelfEmploymentSettings()

        def set_self_employment_type(self, self_employment_type: SelfEmploymentType) -> Self:
            """Set ZUS contribution scheme."""
            self._options.self_employment_type = self_employment_type
            return self
        def set_tax_type(self, tax_type: TaxType) -> Self:
            """Set tax calculation regime."""
            self._options.tax_type = tax_type
            return self
        def set_tax_lump_rate(self, tax_lump_rate: Decimal) -> Self:
            """
            Set lump-sum tax rate.

            Raises:
                ValueError: If rate is not in allowed `LUMP_RATES_ALLOWED`.
            """
            self._options.tax_lump_rate = tax_lump_rate
            return self
        def set_health_base(self, health_base: HealthBase) -> Self:
            """Set health contribution scale."""
            self._options.health_base = health_base
            return self
        def set_sick_pay(self,  is_sick_pay: bool, sick_pay_days: int = 0, month_days: int = 0) -> Self:
            """Configure voluntary sickness insurance."""
            self._options.is_sick_pay =  is_sick_pay
            self._options.sick_pay_days = sick_pay_days
            self._options.month_days = month_days
            return self
        def is_fp(self, is_fp: bool) -> Self:
            """Enable or disable Labor Fund contribution."""
            self._options.is_fp = is_fp
            return self
        def is_other_minimum_contract(self, other_minimum_contract: bool) -> Self:
            """Specify if taxpayer holds another minimum-wage contract."""
            self._options.other_minimum_contract = other_minimum_contract
            return self

        # def set_average_social_income_previous_year(self, average_social_income_previous_year: Decimal) -> Self:
        #     self._options.average_social_income_previous_year = average_social_income_previous_year
        #     return self

        def set_costs(self, costs: Decimal) -> Self:
            """Set tax-deductible business expenses."""
            self._options.costs = costs
            return self
        def set_current_month_gross_sum(self, current_month_gross_sum: Decimal) -> Self:
             self._options.current_month_gross_sum = current_month_gross_sum
             return self
        def set_social_security_base_sum(self, social_security_base_sum: Decimal) -> Self:
            """Set the basis for ZUS calculation if overridden."""
            self._options.social_security_base_sum = social_security_base_sum
            return self
        def set_tax_base_sum(self, tax_base_sum: Decimal) -> Self:
            """Set taxable income base."""
            self._options.tax_base_sum = tax_base_sum
            return self
        def set_accident_insurance_rate(self, accident_insurance_rate: Decimal | None) -> Self:
             self._options.accident_insurance_rate = accident_insurance_rate
             return self
        def set_salary_deductions(self, salary_deductions: Decimal) -> Self:
            """Set non-taxable deductions (e.g., allowances)."""
            self._options.salary_deductions = salary_deductions
            return self
        def set_name(self,name: str) -> Self:
            """Assign display name for the configuration."""
            self._options.name = name
            return self
        def build(self) -> 'SelfEmploymentSettings':
            """Finalize and return the configured settings instance."""
            return self._options