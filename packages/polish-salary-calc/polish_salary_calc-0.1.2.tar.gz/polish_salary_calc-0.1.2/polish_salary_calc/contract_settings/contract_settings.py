from dataclasses import dataclass
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import override

from polish_salary_calc.salary.salaryexporter import SalaryExporter,SalaryExporterDict


@dataclass
class ContractSettngs(SalaryExporter,ABC):
    """
    Abstract base class defining cumulative state and configuration shared between
    all contract types (Employment, Mandate, SelfEmployment, WorkContract).

    This class stores values that must be *propagated month-to-month* across yearly
    calculations, such as:
        - social insurance base accumulation (used to stop contributions above ZUS cap)
        - 50% cost limit usage (used until cost_threshold is reached)
        - taxable base progressive accumulation (for PIT tax threshold handling)
        - cumulative gross salary (optional reporting value)
        - PPK employee/employer contributions tracking
        - optional accident insurance rate (varies by employer industry risk class)

    It also acts as the configuration object passed into monthly contract calculation,
    where concrete subclasses define contract-specific calculation rules.
    """
    name: str | None = None
    current_month_gross_sum: Decimal = Decimal('0.0')
    social_security_base_sum: Decimal = Decimal('0.0')
    cost_fifty_sum: Decimal = Decimal('0.0')
    tax_base_sum: Decimal = Decimal('0.0')
    employee_ppk: Decimal = Decimal('0.0')
    employer_ppk: Decimal = Decimal('0.0')
    accident_insurance_rate: Decimal | None = None
    salary_deductions: Decimal = Decimal('0.0')

    def __str__(self) -> str:
        """
        Return formatted string export of the configuration using SalaryExporter.
        """
        return self.to_string()

    @override
    def to_exporter_dict(self) -> SalaryExporterDict:
        """
        Convert internal configuration state to a dictionary structure suitable
        for export (JSON, Excel, CSV, Pandas DataFrame).

        Returns:
            SalaryExporterDict: A mapping where the key is the class name and the
            value is the internal attribute dictionary.
        """
        return {self.__class__.__name__:self.__dict__}

    @abstractmethod
    def to_dict(self) -> dict[str, str | Decimal | bool]:
        """
        Convert configuration to a simple dictionary representation that can be
        serialized or embedded inside salary summary objects.

        This method must be implemented by contract-specific subclasses to ensure
        that only relevant fields are exposed and formatted correctly.

        Returns:
            dict[str, str | Decimal | bool]: Serialisable contract settings data.
        """
        pass

    def options_type(self):
        """
        Get the user-friendly type name of the contract settings object.

        Returns:
            str: Name of the concrete class (e.g., 'EmploymentContractSettings').
        """
        return self.__class__.__name__