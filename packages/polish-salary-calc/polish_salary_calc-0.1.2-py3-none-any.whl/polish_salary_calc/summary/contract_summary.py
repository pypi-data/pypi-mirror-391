from decimal import Decimal
from enum import Enum
from typing import TypedDict, override, Self

from polish_salary_calc.salary.salaryexporter import SalaryExporter
from polish_salary_calc.contracts.employment_contract import EmploymentContract
from polish_salary_calc.contracts.mandate_contract import MandateContract
from polish_salary_calc.contracts.self_employment import SelfEmployment
from polish_salary_calc.contracts.work_contract import WorkContract
from polish_salary_calc.contract_settings.self_employment_settings import SelfEmploymentSettings
from polish_salary_calc.contract_settings.work_contract_settings import WorkContractSettings
from polish_salary_calc.contract_settings.employment_contract_settings import EmploymentContractSettings
from polish_salary_calc.contract_settings.mandate_contract_settings import MandateContractSettings
from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.salary.salary import SalaryType, Salary



class Months(Enum):
    JAN = "JAN"
    FEB = "FEB"
    MAR = "MAR"
    APR = "APR"
    MAY = "MAY"
    JUN = "JUN"
    JUL = "JUL"
    AUG = "AUG"
    SEP = "SEP"
    OCT = "OCT"
    NOV = "NOV"
    DEC = "DEC"

class ContractSettings(TypedDict):
    """
    Configuration of contract calculation parameters for a given month.

    Keys:
        rates (Rates | None): Tax and social insurance rates used for the month.
        contract_settings (EmploymentContractSettings | MandateContractSettings |
                           SelfEmploymentSettings | WorkContractSettings | None):
            Configuration object describing specific contract rules (tax basis, insurance coverage, etc.).
        salary_base (Decimal | None): Base input salary for calculation (gross or net depending on salary_type).
        salary_type (SalaryType): Indicates whether salary_base is gross or net.
        enabled (bool): Whether this month's contract should be included in calculations.
    """
    rates: Rates  | None
    contract_settings: EmploymentContractSettings | MandateContractSettings | SelfEmploymentSettings | WorkContractSettings | None
    salary_base: Decimal | None
    salary_type: SalaryType
    enabled: bool


class YearContractSummary(SalaryExporter):
    """
    Aggregates salary calculations across an entire year on a monthly basis.

    The class manages:
    - Default contract rates and salary input applied to all months.
    - Month-level overrides (rates, contract settings, base salary, contract enable/disable).
    - Sequential accumulation of social/tax bases across months
      (important for thresholds such as ZUS cap, 50% cost limit, and PIT threshold).
    - Optional comparison with another contract (absolute-and-difference summary).

    Attributes:
        default_salary_base (Decimal): Default salary input used when no per-month override is provided.
        default_salary_type (SalaryType): Default interpretation of salary_base (gross or net).
        _monthly_contract_parameters (dict[Months, ContractSettings]): Per-month configuration states.
        _monthly_contract_calculated_data (dict[Months, Salary]): Calculated salary objects per month.
        summary (Salary): Aggregated total yearly salary calculation.
        is_calculated (bool): Indicates whether yearly calculation has already been executed.
        salary_compared_contract (Salary | None): Salary object used for comparative evaluation.
        salary_difference (Salary | None): Difference between `summary` and `salary_compared_contract`.
        is_compared (bool): Indicates if `compare_to()` was executed.
    """
    def __init__(self,
                 default_rates:Rates,
                 contract_settings: EmploymentContractSettings | MandateContractSettings | SelfEmploymentSettings | WorkContractSettings,
                 default_salary_base: Decimal,
                 default_salary_type: SalaryType= SalaryType.GROSS
                 ) -> None:
        """
        Initialize yearly contract summary with default configuration applied to all months.

        Args:
            default_rates (Rates): Default tax and insurance rates used for all months unless overridden.
            contract_settings (...): The default contract configuration object replicated per month.
            default_salary_base (Decimal): Default salary value (gross/net depending on salary_type).
            default_salary_type (SalaryType): Whether salary_base is gross or net.
        """
        self.default_salary_base: Decimal = default_salary_base
        self.default_salary_type: SalaryType = default_salary_type

        self._monthly_contract_parameters: dict[Months, ContractSettings] = {}
        self._monthly_contract_calculated_data: dict[Months,Salary] = {}

        self.summary: Salary = Salary(rates=default_rates,contract_settings=contract_settings)
        self.is_calculated=False

        self._set_empty_months_options_to_default()

        self.salary_compared_contract: Salary | None = None
        self.salary_difference: Salary | None = None
        self.is_compared: bool = False

    @classmethod
    def from_contract(cls,contract: Salary) -> Self:
        """
        Construct a yearly summary from an already-calculated Salary object.

        Args:
            contract (Salary): The base contract to replicate monthly.

        Returns:
            YearContractSummary: New summary instance with defaults extracted from the contract.
        """
        return cls(contract.rates,contract.contract_settings,contract.input_salary,contract.salary_type)

    def calculate(self) -> None:
        """
        Perform salary calculations for each month and accumulate yearly totals.

        Calculation details:
        - Iterates through all Months.
        - For each enabled month:
            * Propagates cumulative sums (ZUS base, 50% cost usage, PIT tax base).
            * Instantiates the correct contract type based on contract_settings.
            * Calculates salary for the month and stores results.
            * Updates cumulative totals for subsequent months.
        - Aggregates results into `summary`.

        Raises:
            NotImplementedError: If an unsupported contract type is encountered.
        """
        social_security_base_sum: Decimal = self.summary.contract_settings.social_security_base_sum
        cost_fifty_sum: Decimal = self.summary.contract_settings.cost_fifty_sum
        tax_base_sum: Decimal = self.summary.contract_settings.tax_base_sum

        for month in Months:
            mco = self._monthly_contract_parameters[month]
            if not mco["enabled"] or not mco["contract_settings"] or not mco["rates"] or not mco["salary_base"]:
                self._monthly_contract_calculated_data[month] = Salary(self.summary.rates, self.summary.contract_settings)
                continue

            mco["contract_settings"].social_security_base_sum = social_security_base_sum
            mco["contract_settings"].cost_fifty_sum = cost_fifty_sum
            mco["contract_settings"].tax_base_sum = tax_base_sum

            contract: EmploymentContract | MandateContract | SelfEmployment | WorkContract | None = None
            if isinstance(mco["contract_settings"], EmploymentContractSettings):
                contract = EmploymentContract(mco["rates"],mco["contract_settings"])
            elif isinstance(mco["contract_settings"], MandateContractSettings):
                contract = MandateContract(mco["rates"],mco["contract_settings"])
            elif isinstance(mco["contract_settings"], SelfEmploymentSettings):
                contract = SelfEmployment(mco["rates"],mco["contract_settings"])
            elif isinstance(mco["contract_settings"], WorkContractSettings):
                contract = WorkContract(mco["rates"],mco["contract_settings"])
            else: raise NotImplementedError("Contract contract_settings not implemented")

            contract.calculate(mco["salary_base"],mco["salary_type"])
            contract.name = month.name
            self._monthly_contract_calculated_data[month] = contract

            social_security_base_sum = contract.social_security_base_total
            cost_fifty_sum = contract.cost_fifty_total
            tax_base_sum = contract.tax_base_total

            self.summary +=contract

        self.is_calculated = True

    def modify_month_contracts(self,
                               months: list[Months],
                               enabled: bool = True,
                               rates:Rates | None = None,
                               salary_base: Decimal | None = None,
                               salary_type: SalaryType= SalaryType.GROSS
                               ) -> None:
        """
        Override monthly settings for one or more months.

        Args:
            months (list[Months]): Months to modify.
            enabled (bool): Whether the contract is active for these months.
            rates (Rates | None): Rates override, fallback to summary rates if None.
            salary_base (Decimal | None): Salary base override, fallback to default if None.
            salary_type (SalaryType): Base salary interpretation (gross/net).
        """
        for month in months:
            self._monthly_contract_parameters[month]={
                "rates": rates or self.summary.rates,
                "contract_settings":  self.summary.contract_settings,
                "salary_base": salary_base or self.default_salary_base,
                "salary_type": salary_type or self.default_salary_type,
                "enabled":enabled
            }

    def _set_empty_months_options_to_default(self) -> None:
        """
        Initialize all months with default configuration values.
        """
        self.modify_month_contracts(
                list(Months),
                True,
                self.summary.rates,
                self.default_salary_base,
                self.default_salary_type
            )

    def to_dict_salary(self) ->  dict[str, Salary]:
        """
        Convert monthly and summary salary results into a dictionary.

        Returns:
            dict[str, Salary]:
                Keys include month names, 'SUMMARY', and optionally 'COMPARED'/'DIFFERENCE'.
        """
        output = {k.value: v for k, v in self._monthly_contract_calculated_data.items()}
        output['SUMMARY'] =self.summary
        if self.is_compared and self.salary_compared_contract is not None and self.salary_difference is not None:
            output['COMPARED'] = self.salary_compared_contract
            output['DIFFERENCE'] = self.salary_difference
        return output

    @override
    def to_exporter_dict(self)-> dict[str,dict[str,str | Decimal | bool]]:
        """
        Convert monthly and summary calculations into flat export format compatible with SalaryExporter.

        Returns:
            dict[str, dict]: Flattened structure suitable for tabular export.
        """
        output = {k:vv for k, v in self.to_dict_salary().items() for vv in v.to_exporter_dict().values()}
        return output

    def compare_to(self, salary_compared_contract: Self | 'Salary') -> Self | 'Salary':
        """
        Compare this yearly summary to another contract or summary.

        Args:
            salary_compared_contract (Self | Salary): The comparison target.

        Returns:
            Self | Salary: Returns self to allow call chaining.

        Raises:
            RuntimeError: If calculation has not been performed.
        """
        if self.is_calculated:
            if isinstance(salary_compared_contract, Salary):
                self.salary_compared_contract = salary_compared_contract
            else: self.salary_compared_contract = salary_compared_contract.summary
            self.salary_difference = self.summary - self.salary_compared_contract
            self.is_compared = True
        else: raise RuntimeError("Contract not calculated! Calculate first, before comparison!")
        return self

    def __str__(self) -> str:
        """Return formatted string export using SalaryExporter.to_string()."""
        return self.to_string()

    def __getitem__(self, item: str) ->  Salary:
        """
         Access calculated monthly or summary salary by name.

         Example:
             summary["MARCH"]
             summary["SUMMARY"]

         Args:
             item (str): Month name or "SUMMARY"/"COMPARED"/"DIFFERENCE".

         Returns:
             Salary: Requested salary object.
         """
        return self.to_dict_salary()[item]