from decimal import Decimal
from typing import override
from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.contract_settings.employment_contract_settings import EmploymentContractSettings
from polish_salary_calc.contracts.base_contract import BaseContract
from polish_salary_calc.salary.salary_utilities import SalaryUtilities

class EmploymentContract(BaseContract[EmploymentContractSettings]):
    """
    Calculates salary components for a standard Polish employment contract (umowa o pracę).

    This class extends `BaseContract` with logic specific to employment contracts,
    including handling increased tax-deductible costs, author’s rights (50% kosztów),
    PPK, sick pay, and tax exemptions (e.g., under 26 years old).

    Attributes:
        rates (Rates): Current applicable social insurance and tax rates.
        contract_settings (EmploymentContractSettings): Configuration and parameters of the contract.
    """
    def __init__(self, rates: Rates, contract_settings: EmploymentContractSettings) -> None:
        """
        Initialize an EmploymentContract instance.

        Args:
            rates (Rates): Table of tax and insurance rates.
            contract_settings (EmploymentContractSettings): Settings for this contract.
        """
        super().__init__(rates, contract_settings)

    @override
    def calculate_salary_base(self) -> Decimal:
        """Return the contractual gross amount before deductions."""
        return super().calculate_salary_base()

    @override
    def calculate_sick_pay(self) -> Decimal:
        """
         Return the sick pay amount declared in contract settings.

         Returns:
             Decimal: Sick pay value.
         """
        return self.contract_settings.sick_pay

    @override
    def calculate_salary_gross(self) -> Decimal:
        """Return the gross salary after accounting for sick pay adjustments."""
        return super().calculate_salary_gross()

    @override
    def calculate_social_security_base(self) -> Decimal:
        """Return the base used for social insurance contributions."""
        return super().calculate_social_security_base()

    @override
    def calculate_pension_insurance(self) -> Decimal:
        """Return the employee pension insurance contribution."""
        return super().calculate_pension_insurance()

    @override
    def calculate_disability_insurance(self) -> Decimal:
        """Return the disability insurance contribution."""
        return super().calculate_disability_insurance()

    @override
    def calculate_sickness_insurance(self) -> Decimal:
        """Return the sickness insurance contribution."""
        return super().calculate_sickness_insurance()

    @override
    def calculate_cost(self) -> Decimal:
        """Return the tax-deductible cost value (regular or 50% authors' costs if enabled)."""
        return super().calculate_cost()

    @override
    def _calculate_regular_cost(self) -> Decimal:
        """
        Internal calculation of regular tax-deductible costs.
        Uses either standard or increased deductible amount.

        Returns:
            Decimal: Deductible costs amount.
        """
        if self.contract_settings.increased_costs:
            return self.rates.income_tax_deduction[1]
        else:
            return self.rates.income_tax_deduction[0]

    @override
    def _calculate_author_rights_cost(self) -> Decimal:
        """
        Internal calculation of 50% author rights cost (koszty uzyskania przychodu 50%).

        Returns:
            Decimal: Calculated author rights deductible amount.
        """
        return SalaryUtilities.calculate_author_rights_cost(
            self.regular_cost,
            self.contract_settings.cost_fifty_ratio,
            self.health_insurance_base,
            self.contract_settings.cost_fifty_sum,
            self.rates.cost_threshold
        )

    @override
    def calculate_health_insurance_base(self) -> Decimal:
        """Return the base for calculating health insurance contributions."""
        return super().calculate_health_insurance_base()

    @override
    def calculate_health_insurance(self) -> Decimal:
        """Return the health insurance contribution."""
        return super().calculate_health_insurance()

    @override
    def calculate_tax_base(self) -> Decimal:
        """Return the tax base before applying the tax rate."""
        return super().calculate_tax_base()

    @override
    def calculate_tax(self) -> Decimal:
        """
        Calculate the income tax.

        Special rules:
        - If employee is under 26: tax = 0.
        - If business activity is inactive: standard tax-free amount applies.
        """
        if self.contract_settings.under_26: return Decimal('0.0')
        if not self.contract_settings.active_business:
            out = SalaryUtilities.calculate_tax(
                self.rates.income_tax,
                self.tax_base,
                self.contract_settings.tax_base_sum,
                self.rates.tax_threshold,
                self.rates.month_tax_free
            )
        else:
            out = SalaryUtilities.calculate_tax(
                self.rates.income_tax,
                self.tax_base,
                self.contract_settings.tax_base_sum,
                self.rates.tax_threshold
            )
        return out

    @override
    def calculate_ppk_tax(self) -> Decimal:
        """
        Calculate tax on PPK contributions.

        If employee is under 26 years old: tax is zero.
        """
        if self.contract_settings.under_26: return Decimal('0.0')
        return super().calculate_ppk_tax()

    @override
    def calculate_salary_deductions(self) -> Decimal:
        """Return total salary deductions (other than insurance/tax)."""
        return super().calculate_salary_deductions()

    @override
    def calculate_employee_ppk_contribution(self) -> Decimal:
        """Return employee PPK contribution."""
        return super().calculate_employee_ppk_contribution()

    @override
    def calculate_net_salary(self) -> Decimal:
        """Return the net salary (take-home pay)."""
        return super().calculate_net_salary()
    @override
    def calculate_pension_contribution(self) -> Decimal:
        """Return employer pension contribution."""
        return super().calculate_pension_contribution()

    @override
    def calculate_disability_contribution(self)-> Decimal:
        """Return employer disability insurance contribution."""
        return super().calculate_disability_contribution()

    @override
    def calculate_accident_insurance(self) -> Decimal:
        """Return employer accident insurance contribution."""
        return super().calculate_accident_insurance()

    @override
    def calculate_fp(self) -> Decimal:
        """
        Calculate Labor Fund (FP) contribution.

        Disabled if `fp_fgsp` flag is False.
        """
        if not self.contract_settings.fp_fgsp:
            return Decimal('0')
        else:
            return super().calculate_fp()

    @override
    def calculate_fgsp(self) -> Decimal:
        """
        Calculate Guaranteed Employee Benefits Fund (FGŚP) contribution.

        Disabled if `fp_fgsp` flag is False.
        """
        if not self.contract_settings.fp_fgsp:
            return Decimal('0')
        else:
            return super().calculate_fgsp()