from datetime import datetime
from pathlib import Path
from typing import Self, TypedDict, override, Unpack
from decimal import Decimal
from enum import Enum
import pandas as pd

from polish_salary_calc.salary.salaryexporter import SalaryExporter
from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from polish_salary_calc.rates.rates import Rates


class SalaryType(Enum):
    """
    Enumeration representing the basis on which a salary calculation is performed.

    Attributes:
        GROSS: Salary calculation is performed starting from a gross salary amount.
        NET: Salary calculation is performed starting from a target net salary amount.
    """
    GROSS = 1
    NET = 2

class SalaryDict(TypedDict):
    """
    Structured dictionary describing the result of a salary calculation.

    Each field represents a specific monetary value calculated during payroll processing.
    This structure is used for exporting or transferring salary computation results.

    Attributes:
        name (str): Human-readable identifier for the salary calculation.
        created_datetime (datetime): Timestamp indicating when the salary was calculated.

        salary_base (Decimal): Base salary before additions or sickness adjustments.
        salary_sick_pay (Decimal): Amount of sickness pay included in the salary.
        salary_gross (Decimal): Gross salary after combining base and sickness pay.

        social_security_base (Decimal): Base used for calculating social insurance contributions.
        social_security_base_total (Decimal): Total social insurance contribution base.

        pension_insurance (Decimal): Employee pension insurance contribution.
        disability_insurance (Decimal): Employee disability insurance contribution.
        sickness_insurance (Decimal): Employee sickness insurance contribution.
        social_insurance_sum (Decimal): Sum of employee social insurance contributions.

        cost (Decimal): Standard tax deductible cost.
        cost_fifty_total (Decimal): Total deductible cost under 50% author’s rights cost.
        regular_cost (Decimal): Standard deductible cost amount.
        author_rights_cost (Decimal): Deductible cost applied to copyrighted work compensation.

        health_insurance_base (Decimal): Base used to compute health insurance contribution.

        tax_base (Decimal): Income tax base after allowable deductions.
        tax_base_total (Decimal): Total taxable base including adjustments.
        tax (Decimal): Calculated income tax amount.
        health_insurance (Decimal): Health insurance contribution.
        ppk_tax (Decimal): Additional tax from PPK contributions when applicable.

        tax_advance_payment (Decimal): Tax prepayment to be transferred to tax authority.

        salary_deductions (Decimal): Sum of all deductions subtracted from gross salary.

        employee_ppk_contribution (Decimal): Employee share of PPK contribution.
        net_salary (Decimal): Final take-home salary.

        employer_pension_contribution (Decimal): Employer pension insurance cost.
        employer_disability_contribution (Decimal): Employer disability insurance cost.
        accident_insurance (Decimal): Employer accident insurance contribution.
        fp (Decimal): Employer Labor Fund (FP) contribution.
        fgsp (Decimal): Employer Guaranteed Employee Benefits Fund (FGŚP) contribution.
        employer_ppk_contribution (Decimal): Employer share of PPK contribution.

        total_employer_cost (Decimal): Total employer cost including gross salary and contributions.
        total_markups (Decimal): Total employer overhead relative to the net salary.

        brutto_ratio (Decimal): Percentage share of gross salary in employer's total cost.
        net_ratio (Decimal): Percentage share of net salary in employer's total cost.
        total_markups_ratio (Decimal): Percentage share of employer overhead in total cost.
    """
    name: str
    created_datetime:datetime
    salary_base: Decimal
    salary_sick_pay: Decimal
    salary_gross: Decimal
    social_security_base: Decimal
    social_security_base_total: Decimal
    pension_insurance: Decimal
    disability_insurance: Decimal
    sickness_insurance: Decimal
    social_insurance_sum: Decimal
    cost: Decimal
    cost_fifty_total: Decimal
    regular_cost: Decimal
    author_rights_cost: Decimal
    health_insurance_base: Decimal
    tax_base: Decimal
    tax_base_total: Decimal
    tax: Decimal
    health_insurance: Decimal
    ppk_tax: Decimal
    tax_advance_payment: Decimal
    salary_deductions: Decimal
    employee_ppk_contribution: Decimal
    net_salary: Decimal
    employer_pension_contribution: Decimal
    employer_disability_contribution: Decimal
    accident_insurance: Decimal
    fp: Decimal
    fgsp: Decimal
    employer_ppk_contribution: Decimal
    total_employer_cost: Decimal
    total_markups: Decimal
    brutto_ratio: Decimal
    net_ratio: Decimal
    total_markups_ratio: Decimal

class Salary[T: ContractSettngs](SalaryExporter):
    """
       Represents a detailed salary calculation result for a given contract configuration and tax rates.

       This class encapsulates the full structure of payroll calculation, including:
       - Base salary and sickness pay
       - Social insurance contributions (employee and employer)
       - Tax calculation and tax advance payments
       - Health insurance contributions
       - PPK (Employee Capital Plans) contributions
       - Net salary and total employer cost
       - Ability to compare salary results between different contract configurations

       The class supports arithmetic operators (`+`, `-`, `+=`, `-=`) allowing aggregation or
       difference analysis between salary objects. It also supports exporting results to multiple
       formats (CSV, JSON, Excel, DataFrame).

       Attributes:
           rates (Rates): Set of tax and contribution rates used in calculations.
           contract_settings (ContractSettngs): Contract configuration influencing cost structure.
           name (str): Human-readable identifier for calculation result.
           is_calculated (bool): Indicates whether salary calculation has been completed.
           is_compared (bool): Indicates whether this salary has been compared to another one.
           salary_compared_contract (Salary | None): Reference to compared salary object.
           salary_difference (Salary | None): Difference between compared salary results.
       """
    def __init__(self, rates: Rates , contract_settings: T ) -> None:

        self.input_salary = Decimal('0')
        self.salary_type = SalaryType.GROSS

        self._created_datetime = datetime.now()

        self.rates: Rates = rates
        self.contract_settings: T = contract_settings

        if self.contract_settings.name is None:
            self.name = self._generate_name_from_date()
        else:
            self.name = self.contract_settings.name

        if 0 < self.contract_settings.employer_ppk < Decimal('0.015') or 0 < self.contract_settings.employee_ppk < Decimal('0.02'):
            raise ValueError('Employer or employee PPK rate is too small')


        self.salary_base: Decimal = Decimal('0.0') #płaca podstawowa
        self.salary_sick_pay: Decimal = Decimal('0.0') #chorobowe
        self.salary_gross: Decimal= Decimal('0.0')  #brutto
        self.social_security_base: Decimal= Decimal('0.0') #podst ub społ
        self.social_security_base_total: Decimal= Decimal('0.0')
        self.pension_insurance: Decimal= Decimal('0.0') #ub emeryt
        self.disability_insurance: Decimal= Decimal('0.0') #ub rent
        self.sickness_insurance: Decimal= Decimal('0.0') #chorobowe
        self.social_insurance_sum: Decimal= Decimal('0.0') #uma ub społ
        self.cost: Decimal= Decimal('0.0')
        self.cost_fifty_total: Decimal= Decimal('0.0')
        self.regular_cost: Decimal= Decimal('0.0')
        self.author_rights_cost: Decimal= Decimal('0.0') #koszt praw autorskich (50%)
        self.health_insurance_base: Decimal= Decimal('0.0') #podst zdrowotne
        self.tax_base: Decimal= Decimal('0.0') #podstawa podatku
        self.tax_base_total = Decimal('0.0')
        self.tax: Decimal= Decimal('0.0') # podatek
        self.health_insurance: Decimal= Decimal('0.0')
        #self.ub_zdr_odl: Decimal= Decimal('0.0')
        self.ppk_tax: Decimal= Decimal('0.0')
        self.tax_advance_payment: Decimal= Decimal('0.0') #zaliczka podatku
        self.salary_deductions: Decimal= Decimal('0.0') #potrącenia wypłaty
        self.employee_ppk_contribution: Decimal= Decimal('0.0')
        self.net_salary: Decimal= Decimal('0.0')
        self.employer_pension_contribution: Decimal= Decimal('0.0') #ub emeryt prac
        self.employer_disability_contribution: Decimal= Decimal('0.0') #ub rent prac
        self.accident_insurance: Decimal= Decimal('0.0') #ub wyp prac
        self.fp: Decimal= Decimal('0.0')
        self.fgsp: Decimal= Decimal('0.0')
        self.employer_ppk_contribution: Decimal= Decimal('0.0') #ppk pracodawca
        self.total_employer_cost: Decimal= Decimal('0.0') #brutto brutto

        self.is_calculated: bool = False

        self.salary_compared_contract: Salary | None = None
        self.salary_difference: Salary | None = None
        self.is_compared: bool = False

    def _generate_name_from_date(self) -> str:
        """
        Generates a unique name based on timestamp.

        Returns:
            str: Timestamp-based salary calculation identifier.
        """
        return f'{self.__class__.__name__}{self._created_datetime:%Y_%m_%d_%H%M%S}'

    @property
    def created_datetime(self) -> str:
        """
        Returns formatted creation timestamp of the salary calculation.

        Returns:
            str: Timestamp formatted as 'YYYY-MM-DD HH:MM:SS'.
        """
        return self._created_datetime.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def total_markups(self) -> Decimal:
        """
        Calculates the difference between employer total cost and employee net salary.

        Returns:
            Decimal: Total employer overhead (employer cost minus net salary).
        """
        return (self.total_employer_cost - self.net_salary).quantize(Decimal('0.01'))

    @property
    def gross_ratio(self) -> Decimal:
        """
        Share of gross salary in total employer cost, expressed as a percentage.

        Returns:
            Decimal: Gross salary ratio as percent (0-100).
        """
        if self.total_employer_cost == 0: return Decimal('0.0')
        return ((self.salary_gross / self.total_employer_cost) * 100).quantize(Decimal('0.01'))

    @property
    def net_ratio(self) -> Decimal:
        """
        Share of net salary in total employer cost, expressed as a percentage.

        Returns:
            Decimal: Net salary ratio as percent (0-100).
        """
        if self.total_employer_cost == 0: return Decimal('0.0')
        return ((self.net_salary / self.total_employer_cost) * 100).quantize(Decimal('0.01'))

    @property
    def total_markups_ratio(self) -> Decimal:
        """
        Share of employer overhead in total employer cost.

        Returns:
            Decimal: Employer overhead ratio as percent (0-100).
        """
        if self.total_employer_cost == 0: return Decimal('0.0')
        return ((self.total_markups / self.total_employer_cost) * 100).quantize(Decimal('0.01'))

    def to_dict(self) -> Unpack[SalaryDict]:
        """
        Converts salary result into a flat dictionary structure.

        Returns:
            dict: Dictionary matching SalaryDict typing definition.
        """
        return {                                  "name": self.name,
                                                  "contract_type": self.get_contract_type(),
                                                  "created_datetime": self.created_datetime,
                                                  "salary_base": self.salary_base,
                                                  "salary_sick_pay": self.salary_sick_pay,
                                                  "salary_gross": self.salary_gross,
                                                  "social_security_base": self.social_security_base,
                                                  # "social_security_base_total": self.social_security_base_total,
                                                  "pension_insurance": self.pension_insurance,
                                                  "disability_insurance": self.disability_insurance,
                                                  "sickness_insurance": self.sickness_insurance,
                                                  "social_insurance_sum": self.social_insurance_sum, "cost": self.cost,
                                                  # "cost_fifty_total": self.cost_fifty_total,
                                                  "regular_cost": self.regular_cost,
                                                  "author_rights_cost": self.author_rights_cost,
                                                  "health_insurance_base": self.health_insurance_base,
                                                  "tax_base": self.tax_base,
                                                  # "tax_base_total": self.tax_base_total,
                                                  "tax": self.tax, "health_insurance": self.health_insurance,
                                                  "ppk_tax": self.ppk_tax,
                                                  "tax_advance_payment": self.tax_advance_payment,
                                                  "salary_deductions": self.salary_deductions,
                                                  "employee_ppk_contribution": self.employee_ppk_contribution,
                                                  "net_salary": self.net_salary,
                                                  "employer_pension_contribution": self.employer_pension_contribution,
                                                  "employer_disability_contribution": self.employer_disability_contribution,
                                                  "accident_insurance": self.accident_insurance, "fp": self.fp,
                                                  "fgsp": self.fgsp,
                                                  "employer_ppk_contribution": self.employer_ppk_contribution,
                                                  "total_employer_cost": self.total_employer_cost,
                                                  "total_markups": self.total_markups,
                                                  # "gross_ratio": self.gross_ratio,
                                                  "net_ratio": self.net_ratio,
                                                  "total_markups_ratio": self.total_markups_ratio}

    @override
    def to_exporter_dict(self, row_name: str | None = None)-> dict[str,dict[str, str | Decimal | bool]]:
        """
        Converts salary data into a nested dictionary suitable for export routines.

        Args:
            row_name (str | None): Optional root key name. Defaults to salary name.

        Returns:
            dict[str, dict[str, str | Decimal | bool]]: Export-ready structured dictionary.
        """
        if row_name is None:
            row_name = self.name
        output:  dict[str, dict[str, str | Decimal | bool]] = {row_name:self.to_dict()}
        # if self.is_compared and self.salary_compared_contract is not None and self.salary_difference is not None:
        #     output["COMPARED"] = self.salary_compared_contract.to_dict()
        #     output["DIFFERANCE"] = self.salary_difference.to_dict()
        return output

    def to_compared_dict(self, row_name: str | None = None) ->  dict[str,dict[str, str | Decimal | bool]]:
        """
        Returns a structured dictionary containing salary calculation data, including comparison results
        if this salary instance was compared to another one.

        If the salary was compared (`self.is_compared == True`), the returned dictionary will include:
        - The original salary calculation result.
        - The salary used for comparison under the key "COMPARED".
        - The numerical difference between them under the key "DIFFERANCE".

        Args:
            row_name (str | None): Optional root name key for the exported data.
                If None, the salary's internal `name` attribute is used.

        Returns:
            dict[str, dict[str, str | Decimal | bool]]:
                A nested dictionary suitable for exporting to CSV, JSON, Excel, or DataFrame.
        """
        if row_name is None:
            row_name = self.name
        output: dict[str, dict[str, str | Decimal | bool]] = {row_name: self.to_dict()}
        if self.is_compared and self.salary_compared_contract is not None and self.salary_difference is not None:
            output["COMPARED"] = self.salary_compared_contract.to_dict()
            output["DIFFERANCE"] = self.salary_difference.to_dict()
        return output

    def to_compared_string(self) -> str:
        """
        Returns a formatted string representation of the salary calculation along with comparison data,
        if available.

        This is primarily used for console or log-friendly output.

        Returns:
            str: Human-readable formatted salary comparison result.
        """
        return self.to_string(self.to_compared_dict())

    def get_compared_data_frame(self) -> pd.DataFrame:
        """
        Converts the salary comparison result into a pandas DataFrame.

        This is commonly used for analysis, reporting, or exporting to analytical tools
        such as Excel or BI software.

        Returns:
            pandas.DataFrame: Salary and comparison data in tabular form.
        """
        return self.get_data_frame(self.to_compared_dict())

    def to_compared_excel(self,path: Path) -> None:
        """
        Exports the salary comparison data to an Excel file.

        Args:
            path (Path): File path where the Excel file will be written.

        Returns:
            None
        """
        self.to_excel(path,self.to_compared_dict())

    def to_compared_csv(self,path: Path) -> None:
        """
        Exports the salary comparison data to a CSV file.

        Args:
            path (Path): File path where the CSV file will be written.

        Returns:
            None
        """
        self.to_csv(path,self.to_compared_dict())

    def to_compared_json(self,path: Path) -> None:
        """
        Exports the salary comparison data to a JSON file.

        Args:
            path (Path): File path where the JSON file will be written.

        Returns:
            None
        """
        self.to_json(path,self.to_compared_dict())

    def get_contract_type(self) -> str:
        """
        Returns the contract type of the salary object, represented by the class name.

        This is useful for export formatting, reporting, and distinguishing multiple
        salary calculations in aggregated outputs.

        Returns:
            str: Class name of the salary object, representing the contract type.
        """
        return self.__class__.__name__

    def compare_to(self, salary_compared_contract: "Salary") -> "Salary":
        """
        Compares this salary to another one and produces a difference salary object.

        Args:
            salary_compared_contract (Salary): Salary object to compare against.

        Returns:
            Salary: Difference, stored as `self.salary_difference`.
        """
        self.salary_compared_contract = salary_compared_contract
        # self.salary_difference = Salary(self.rates,self.contract_settings)
        self.salary_difference = self - self.salary_compared_contract
        self.salary_difference.name = "DIFFERENCE"
        self.is_compared = True
        return self.salary_difference

    def __str__(self) -> str:
        return self.to_string()

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, Salary):
            return NotImplemented
        return self.net_salary == other.net_salary
    def __le__(self, other:object) -> bool:
        if not isinstance(other, Salary):
            return NotImplemented
        return self.net_salary <= other.net_salary
    def __ge__(self, other:object) -> bool:
        if not isinstance(other, Salary):
            return NotImplemented
        return self.net_salary >= other.net_salary

    def __add__(self, other:"Salary") -> "Salary":
        """
        Adds two Salary objects by summing their financial components.

        Args:
            other (Salary): Salary to add.

        Returns:
            Salary: New Salary object representing combined totals.
        """
        output:Salary = Salary(self.rates,self.contract_settings)
        output.salary_base = self.salary_base + other.salary_base
        output.salary_sick_pay = self.salary_sick_pay + other.salary_sick_pay
        output.salary_gross = self.salary_gross +other.salary_gross
        output.social_security_base = self.social_security_base + other.social_security_base
        output.social_security_base_total = other.contract_settings.social_security_base_sum + self.social_security_base
        output.pension_insurance = self.pension_insurance + other.pension_insurance
        output.disability_insurance = self.disability_insurance + other.disability_insurance
        output.sickness_insurance = self.sickness_insurance + other.sickness_insurance
        output.social_insurance_sum = self.social_insurance_sum + other.social_insurance_sum
        output.author_rights_cost = self.author_rights_cost + other.author_rights_cost
        output.cost = self.cost + other.cost
        output.cost_fifty_total = other.contract_settings.cost_fifty_sum + self.author_rights_cost
        output.regular_cost = self.regular_cost + other.regular_cost
        output.author_rights_cost = self.author_rights_cost + other.author_rights_cost
        output.health_insurance_base = self.health_insurance_base + other.health_insurance_base
        output.tax_base = self.tax_base + other.tax_base
        output.tax_base_total = other.contract_settings.tax_base_sum + self.tax_base
        output.tax = self.tax + other.tax
        output.health_insurance = self.health_insurance + other.health_insurance
        output.ppk_tax = self.ppk_tax + other.ppk_tax
        output.tax_advance_payment = self.tax_advance_payment + other.tax_advance_payment
        output.salary_deductions = self.salary_deductions + other.salary_deductions
        output.employee_ppk_contribution = self.employee_ppk_contribution + other.employee_ppk_contribution
        output.net_salary = self.net_salary + other.net_salary
        output.employer_pension_contribution = self.employer_pension_contribution + other.employer_pension_contribution
        output.employer_disability_contribution = self.employer_disability_contribution + other.employer_disability_contribution
        output.accident_insurance = self.accident_insurance + other.accident_insurance
        output.fp = self.fp + other.fp
        output.fgsp = self.fgsp + other.fgsp
        output.employer_ppk_contribution = self.employer_ppk_contribution + other.employer_ppk_contribution
        output.total_employer_cost = self.total_employer_cost + other.total_employer_cost
        return output

    def __iadd__(self, other: "Salary") -> "Salary":
        """
        In-place addition of Salary values.

        Args:
            other (Salary): Salary to merge.

        Returns:
            Salary: Updated object.
        """
        self.salary_base = self.salary_base + other.salary_base
        self.salary_sick_pay = self.salary_sick_pay + other.salary_sick_pay
        self.salary_gross = self.salary_gross + other.salary_gross
        self.social_security_base = self.social_security_base + other.social_security_base
        self.social_security_base_total = other.contract_settings.social_security_base_sum + self.social_security_base
        self.pension_insurance = self.pension_insurance + other.pension_insurance
        self.disability_insurance = self.disability_insurance + other.disability_insurance
        self.sickness_insurance = self.sickness_insurance + other.sickness_insurance
        self.social_insurance_sum = self.social_insurance_sum + other.social_insurance_sum
        self.author_rights_cost = self.author_rights_cost + other.author_rights_cost
        self.cost = self.cost + other.cost
        self.cost_fifty_total = other.contract_settings.cost_fifty_sum + self.author_rights_cost
        self.regular_cost = self.regular_cost + other.regular_cost
        self.health_insurance_base = self.health_insurance_base + other.health_insurance_base
        self.tax_base = self.tax_base + other.tax_base
        self.tax_base_total = other.contract_settings.tax_base_sum + self.tax_base
        self.tax = self.tax + other.tax
        self.health_insurance = self.health_insurance + other.health_insurance
        self.ppk_tax = self.ppk_tax + other.ppk_tax
        self.tax_advance_payment = self.tax_advance_payment + other.tax_advance_payment
        self.salary_deductions = self.salary_deductions + other.salary_deductions
        self.employee_ppk_contribution = self.employee_ppk_contribution + other.employee_ppk_contribution
        self.net_salary = self.net_salary + other.net_salary
        self.employer_pension_contribution = self.employer_pension_contribution + other.employer_pension_contribution
        self.employer_disability_contribution = self.employer_disability_contribution + other.employer_disability_contribution
        self.accident_insurance = self.accident_insurance + other.accident_insurance
        self.fp = self.fp + other.fp
        self.fgsp = self.fgsp + other.fgsp
        self.employer_ppk_contribution = self.employer_ppk_contribution + other.employer_ppk_contribution
        self.total_employer_cost = self.total_employer_cost + other.total_employer_cost
        return self

    def __sub__(self, other: "Salary") -> "Salary":
        """
        Computes difference between two Salary objects.

        Args:
            other (Salary): Salary to subtract.

        Returns:
            Salary: New Salary object representing differences.
        """
        output:Salary = Salary(self.rates,self.contract_settings)
        output.salary_base = self.salary_base - other.salary_base
        output.salary_sick_pay = self.salary_sick_pay - other.salary_sick_pay
        output.salary_gross = self.salary_gross - other.salary_gross
        output.social_security_base = self.social_security_base - other.social_security_base
        output.social_security_base_total = other.contract_settings.social_security_base_sum - self.social_security_base
        output.pension_insurance = self.pension_insurance - other.pension_insurance
        output.disability_insurance = self.disability_insurance - other.disability_insurance
        output.sickness_insurance = self.sickness_insurance - other.sickness_insurance
        output.social_insurance_sum = self.social_insurance_sum - other.social_insurance_sum
        output.author_rights_cost = self.author_rights_cost - other.author_rights_cost
        output.cost = self.cost - other.cost
        output.cost_fifty_total = other.contract_settings.cost_fifty_sum - self.author_rights_cost
        output.regular_cost = self.regular_cost - other.regular_cost
        output.author_rights_cost = self.author_rights_cost - other.author_rights_cost
        output.health_insurance_base = self.health_insurance_base - other.health_insurance_base
        output.tax_base = self.tax_base - other.tax_base
        output.tax_base_total = other.contract_settings.tax_base_sum - self.tax_base
        output.tax = self.tax - other.tax
        output.health_insurance = self.health_insurance - other.health_insurance
        output.ppk_tax = self.ppk_tax - other.ppk_tax
        output.tax_advance_payment = self.tax_advance_payment - other.tax_advance_payment
        output.salary_deductions = self.salary_deductions - other.salary_deductions
        output.employee_ppk_contribution = self.employee_ppk_contribution - other.employee_ppk_contribution
        output.net_salary = self.net_salary - other.net_salary
        output.employer_pension_contribution = self.employer_pension_contribution - other.employer_pension_contribution
        output.employer_disability_contribution = self.employer_disability_contribution - other.employer_disability_contribution
        output.accident_insurance = self.accident_insurance - other.accident_insurance
        output.fp = self.fp - other.fp
        output.fgsp = self.fgsp - other.fgsp
        output.employer_ppk_contribution = self.employer_ppk_contribution - other.employer_ppk_contribution
        output.total_employer_cost = self.total_employer_cost - other.total_employer_cost
        return output

    def __isub__(self, other: "Salary") -> "Salary":
        """
        In-place subtraction of Salary values.

        Args:
            other (Salary): Salary to subtract.

        Returns:
            Salary: Updated object.
        """
        self.salary_base = self.salary_base - other.salary_base
        self.salary_sick_pay = self.salary_sick_pay - other.salary_sick_pay
        self.salary_gross = self.salary_gross - other.salary_gross
        self.social_security_base = self.social_security_base - other.social_security_base
        self.social_security_base_total = other.contract_settings.social_security_base_sum - self.social_security_base
        self.pension_insurance = self.pension_insurance - other.pension_insurance
        self.disability_insurance = self.disability_insurance - other.disability_insurance
        self.sickness_insurance = self.sickness_insurance - other.sickness_insurance
        self.social_insurance_sum = self.social_insurance_sum - other.social_insurance_sum
        self.author_rights_cost = self.author_rights_cost - other.author_rights_cost
        self.cost = self.cost - other.cost
        self.cost_fifty_total = other.contract_settings.cost_fifty_sum - self.author_rights_cost
        self.regular_cost = self.regular_cost - other.regular_cost
        self.health_insurance_base = self.health_insurance_base - other.health_insurance_base
        self.tax_base = self.tax_base - other.tax_base
        self.tax_base_total = other.contract_settings.tax_base_sum - self.tax_base
        self.tax = self.tax - other.tax
        self.health_insurance = self.health_insurance - other.health_insurance
        self.ppk_tax = self.ppk_tax - other.ppk_tax
        self.tax_advance_payment = self.tax_advance_payment - other.tax_advance_payment
        self.salary_deductions = self.salary_deductions - other.salary_deductions
        self.employee_ppk_contribution = self.employee_ppk_contribution - other.employee_ppk_contribution
        self.net_salary = self.net_salary - other.net_salary
        self.employer_pension_contribution = self.employer_pension_contribution - other.employer_pension_contribution
        self.employer_disability_contribution = self.employer_disability_contribution - other.employer_disability_contribution
        self.accident_insurance = self.accident_insurance - other.accident_insurance
        self.fp = self.fp - other.fp
        self.fgsp = self.fgsp - other.fgsp
        self.employer_ppk_contribution = self.employer_ppk_contribution - other.employer_ppk_contribution
        self.total_employer_cost = self.total_employer_cost - other.total_employer_cost
        return self
