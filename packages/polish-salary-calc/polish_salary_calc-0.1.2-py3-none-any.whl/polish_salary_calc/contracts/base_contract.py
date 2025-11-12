from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from decimal import Decimal, ROUND_UP
from polish_salary_calc.salary.salary import Salary,SalaryType
from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.salary.salary_utilities import SalaryUtilities
from abc import ABC, abstractmethod


class BaseContract[T: ContractSettngs](Salary, ABC):
    """
    Abstract base class for salary computation under configurable contract rules.

    This class defines a unified calculation pipeline shared across different contract
    types (e.g., employment contract, mandate contract, B2B). It relies on two primary
    inputs:
      * `Rates` - containing percentage rates and government limits (ZUS, FP, FGŚP, PPK, etc.)
      * `ContractSettngs` - containing individual contract-specific cumulative data
        (e.g., current year social base sum, tax base sum, PPK selections, 50% costs usage, etc.)

    Subclasses must implement:
        * _calculate_regular_cost()
        * _calculate_author_rights_cost()
        * calculate_tax()

    Attributes:
        rates (Rates):
            Active rate configuration (tax rates, insurance rates, legal caps).
        contract_settings (ContractSettngs):
            Contract-specific options and cumulative salary data.

    Inherited Attributes (from Salary, calculated dynamically):
        salary_base, salary_gross, tax_base, net_salary, etc.
    """
    def __init__(self, rates: Rates, contract_settings: T) -> None:
        """
        Initialize contract salary calculator with rate configuration and contract state.

        Args:
            rates (Rates): Current rate table for insurance and tax.
            contract_settings (T): Contract configuration and cumulative tracking values.
        """
        super().__init__(rates,contract_settings)
        self.rates = rates
        self.contract_settings = contract_settings


    def update_rates(self, rates: Rates) -> None:
        """
        Replace rate configuration and reset calculation state.

        Args:
            rates (Rates): New rate set.
        """
        self.rates = rates
        self.is_calculated = False

    def update_options(self, options: T) -> None:
        """
        Replace contract options and reset calculation state.
        Validates PPK contribution minimums.

        Args:
            options (T): New contract settings.

        Raises:
            ValueError: If employee or employer PPK contribution is below legal minimum.
        """
        self.contract_settings = options
        if 0 < self.contract_settings.employer_ppk < Decimal('0.015') or 0 < self.contract_settings.employee_ppk < Decimal('0.02'):
            raise ValueError('Employer or employee PPK is too small')
        self.is_calculated = False

    def get_rates(self) -> Rates:
        """Return the active rate configuration."""
        return self.rates

    def get_settings(self) -> ContractSettngs:
        """Return contract settings (options and cumulative sums)."""
        return self.contract_settings

    def calculate_salary_base(self) -> Decimal:
        """
        Define the base used for wage computation.
        Default behavior: salary_base == input_salary (gross input).
        Subclasses may override for variable hourly structures.
        """
        return self.input_salary

    def calculate_sick_pay(self) -> Decimal:
        """Calculate sick pay (salary for sick leave)."""
        return Decimal('0.0')

    def calculate_salary_gross(self) -> Decimal:
        """Gross salary = base + sick pay."""
        return self.salary_base+self.salary_sick_pay

    def calculate_social_security_base(self) -> Decimal:
        """Base for social security contributions (usually same as salary_base)."""
        return self.salary_base

    def calculate_social_security_base_total(self) -> Decimal:
        """Return cumulative social base including previous months."""
        return self.contract_settings.social_security_base_sum + self.social_security_base

    def calculate_pension_insurance(self) -> Decimal:
        """Employee pension insurance contribution."""
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.pension_insurance_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )

    def calculate_disability_insurance(self) -> Decimal:
        """Employee disability insurance contribution."""
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.disability_insurance_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )

    def calculate_sickness_insurance(self) -> Decimal:
        """Employee sickness insurance contribution."""
        return self.social_security_base * self.rates.sickness_insurance_rate


    def calculate_social_insurance_sum(self) -> Decimal:
        """Sum of employee social security contributions (pension + disability + sickness)."""
        return self.pension_insurance + self.disability_insurance + self.sickness_insurance

    @abstractmethod
    def _calculate_regular_cost(self) -> Decimal:
        """Calculate standard tax-deductible cost of income. Must be implemented."""
        pass

    @abstractmethod
    def _calculate_author_rights_cost(self) -> Decimal:
        """Calculate 50% author rights income deduction cost, if applicable."""
        pass

    def calculate_cost(self) -> Decimal:
        """Total deductible cost (regular + 50% author deduction if applicable)."""
        return self.author_rights_cost + self.regular_cost

    def calculate_cost_fifty_total(self) -> Decimal:
        """Return cumulative 50% author rights cost deduction including current month."""
        return self.contract_settings.cost_fifty_sum + self.author_rights_cost

    def calculate_health_insurance_base(self) -> Decimal:
        """Base for health insurance = salary_gross - social insurance contributions."""
        return self.salary_gross - (self.pension_insurance + self.disability_insurance + self.sickness_insurance)

    def calculate_health_insurance(self) -> Decimal:
        """Health insurance contribution calculated from health insurance base."""
        return self.health_insurance_base * self.rates.health_insurance_rate

    def calculate_tax_base(self) -> Decimal:
        """Taxable income = gross - social contributions - deductible costs."""
        return self.salary_gross - self.social_insurance_sum - self.cost

    def calculate_tax_base_total(self)  ->Decimal:
        """Return cumulative taxable income including previous months."""
        return self.contract_settings.tax_base_sum + self.tax_base

    @abstractmethod
    def calculate_tax(self) -> Decimal:
        """Compute final income tax. Must be implemented."""
        pass

    def _add_ppk_tax_and_check_if_is_positive(self,input_tax: Decimal) -> Decimal:
        """
        Add employer PPK tax effect and ensure result is non-negative.
        """
        input_tax += self.ppk_tax
        if input_tax<=0: return Decimal('0.0')
        return input_tax if input_tax > 0 else Decimal('0.0')


    def calculate_ppk_tax(self) -> Decimal:
        """Tax applied due to employer PPK contribution."""
        return self.social_security_base * self.contract_settings.employer_ppk * self.rates.income_tax[0]


    def calculate_tax_advance_payment(self) -> Decimal:
        """Tax advance = calculated tax, rounded up at accounting stage."""
        return self.tax


    def calculate_salary_deductions(self) -> Decimal:
        """Additional deductions defined in contract (e.g., voluntary deductions)."""
        return self.contract_settings.salary_deductions

    def calculate_employee_ppk_contribution(self) -> Decimal:
        """Employee PPK contribution."""
        return self.social_security_base * self.contract_settings.employee_ppk

    def calculate_net_salary(self) -> Decimal:
        """Net salary after all contributions, insurance, tax and deductions."""
        return self.salary_gross - (
                self.social_insurance_sum + self.tax_advance_payment + self.employee_ppk_contribution + self.health_insurance + self.salary_deductions)

    def calculate_pension_contribution(self) -> Decimal:
        """Employer pension contribution."""
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.employer_pension_contribution_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )


    def calculate_disability_contribution(self) -> Decimal:
        """Employer disability contribution."""
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.employer_disability_contribution_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )


    def calculate_accident_insurance(self) -> Decimal:
        """Employer accident insurance (uses contract override if provided)."""
        if self.contract_settings.accident_insurance_rate is None:
            return  self.social_security_base * self.rates.accident_insurance_rate
        return self.social_security_base * self.contract_settings.accident_insurance_rate

    def calculate_fp(self) -> Decimal:
        """Labor Fund contribution (only if gross salary >= minimum wage)."""
        if self.contract_settings.current_month_gross_sum + self.salary_gross >= self.rates.minimum_wage:
            return self.social_security_base * self.rates.fp_rate
        else:
            return Decimal('0')

    def calculate_fgsp(self) -> Decimal:
        """Guaranteed Employee Benefits Fund contribution."""
        return self.social_security_base * self.rates.fgsp_rate

    def calculate_employer_ppk_contribution(self) -> Decimal:
        """Employer PPK contribution."""
        return self.social_security_base*self.contract_settings.employer_ppk

    def calculate_total_employer_cost(self) -> Decimal:
        """Total employer cost = gross + employer contributions + PPK."""
        return self.salary_gross + self.employer_pension_contribution + self.employer_disability_contribution + self.accident_insurance + self.fp + self.fgsp + self.employer_ppk_contribution


    def calculate(self, salary_base: Decimal, salary_type: SalaryType = SalaryType.GROSS) -> None:
        """
        Perform salary calculation for a given input amount and salary type.

        Args:
            salary_base (Decimal): Input value (gross or net, depending on salary_type).
            salary_type (SalaryType): Salary interpretation (gross or net).

        Raises:
            AttributeError: If contract_settings is not set.
        """
        self.salary_type = salary_type
        if self.contract_settings is None:
            raise AttributeError('No contract_settings set to contract, use "update_options" before calculating')
        self.input_salary = salary_base
        if self.salary_type == SalaryType.GROSS:
            self.calculate_gross()
            self.is_calculated = True
        else:
            self._calculate_net()
            self.is_calculated = True


    def calculate_gross(self) -> None:
        """
        Calculate all dependent salary and contribution values starting from gross salary.

        This method populates all intermediate and final public fields such as:
            salary_base, salary_gross, cost, tax_advance_payment, net_salary,
            total_employer_cost, etc.
        """
        self.salary_base = self.calculate_salary_base().quantize(Decimal('0.01'))
        self.salary_sick_pay = self.calculate_sick_pay().quantize(Decimal('0.01'))
        self.salary_gross= self.calculate_salary_gross().quantize(Decimal('0.01'))
        self.social_security_base = self.calculate_social_security_base().quantize(Decimal('0.01'))
        self.social_security_base_total = self.calculate_social_security_base_total().quantize(Decimal('0.01'))
        self.pension_insurance = self.calculate_pension_insurance().quantize(Decimal('0.01'))
        self.disability_insurance = self.calculate_disability_insurance().quantize(Decimal('0.01'))
        self.sickness_insurance = self.calculate_sickness_insurance().quantize(Decimal('0.01'))
        self.social_insurance_sum = self.calculate_social_insurance_sum().quantize(Decimal('0.01'))
        self.health_insurance_base = self.calculate_health_insurance_base().quantize(Decimal('0.01'))
        self.regular_cost = self._calculate_regular_cost().quantize(Decimal('1'))
        self.author_rights_cost = self._calculate_author_rights_cost().quantize(Decimal('0.01'))
        self.cost = self.calculate_cost().quantize(Decimal('1'))
        self.cost_fifty_total = self.calculate_cost_fifty_total().quantize(Decimal('0.01'))
        self.tax_base = self.calculate_tax_base().quantize(Decimal('1'))
        self.tax_base_total = self.calculate_tax_base_total().quantize(Decimal('0.01'))
        self.ppk_tax = self.calculate_ppk_tax().quantize(Decimal('0.01'))
        self.tax = self._add_ppk_tax_and_check_if_is_positive(self.calculate_tax()).quantize(Decimal('0.01'))
        self.health_insurance = self.calculate_health_insurance().quantize(Decimal('0.01'))
        #self.ub_zdr_odl = self._calculate_ub_zdr_odl()
        self.salary_deductions = self.calculate_salary_deductions().quantize(Decimal('0.01'))
        self.tax_advance_payment = self.calculate_tax_advance_payment().quantize(Decimal('1'), rounding=ROUND_UP)
        self.employee_ppk_contribution = self.calculate_employee_ppk_contribution().quantize(Decimal('0.01'))
        self.employer_pension_contribution = self.calculate_pension_contribution().quantize(Decimal('0.01'))
        self.employer_disability_contribution = self.calculate_disability_contribution().quantize(Decimal('0.01'))
        self.accident_insurance = self.calculate_accident_insurance().quantize(Decimal('0.01'))
        self.fp = self.calculate_fp().quantize(Decimal('0.01'))
        self.fgsp = self.calculate_fgsp().quantize(Decimal('0.01'))
        self.employer_ppk_contribution = self.calculate_employer_ppk_contribution().quantize(Decimal('0.01'))

        self.net_salary = self.calculate_net_salary().quantize(Decimal('0.01'))
        self.total_employer_cost = self.calculate_total_employer_cost().quantize(Decimal('0.01'))


    def _calculate_net(self) -> None:
        """
        Iteratively search for gross salary that results in a desired net salary.
        Used when input salary type is net.
        """
        wished_netto = self.input_salary #salary_base= brutto_estimate

        while self.net_salary.quantize(Decimal('0.01')) != wished_netto.quantize(Decimal('0.01')) :
            self.input_salary += wished_netto - self.net_salary
            self.calculate_gross()
        self.input_salary = wished_netto




