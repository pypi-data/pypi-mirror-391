from decimal import Decimal


class SalaryUtilities:
    """
    Helper utility class providing static methods for performing core payroll calculations.
    These functions are used internally by salary computation routines and are isolated
    to support reuse and testability.
    """
    @staticmethod
    def calculate_pension_or_disability_insurance(
            pension_or_disability_insurance_rate: Decimal,
            social_security_base: Decimal,
            social_security_base_sum: Decimal,
            social_insurance_cap:  Decimal
    ) -> Decimal:
        """
        Calculates pension or disability insurance contribution while respecting the annual
        social insurance contribution cap (30× average salary in a given year).

        The function ensures that contributions do not exceed the legal maximum base.

        Args:
            pension_or_disability_insurance_rate (Decimal): Contribution rate (e.g., 0.0976 for pension).
            social_security_base (Decimal): Contribution base for the current period.
            social_security_base_sum (Decimal): Accumulated contribution base from previous periods.
            social_insurance_cap (Decimal): Maximum allowed annual contribution base.

        Returns:
            Decimal: Calculated contribution amount. Returns zero if the cap has been exceeded.
        """
        total_social_security_base_sum = social_security_base_sum + social_security_base
        if total_social_security_base_sum <= social_insurance_cap:
            return social_security_base *pension_or_disability_insurance_rate
        elif total_social_security_base_sum - social_security_base > social_insurance_cap:
            return Decimal('0.0')
        else:
            return (social_security_base - (total_social_security_base_sum - social_insurance_cap))*pension_or_disability_insurance_rate

    @staticmethod
    def calculate_author_rights_cost(
            income_tax_deduction: Decimal,
            cost_ratio: Decimal,
            base: Decimal,
            cost_fifty_sum: Decimal,
            cost_threshold: Decimal
        )-> Decimal:
        """
            Calculates deductible cost for author’s rights (50% cost of income), respecting the annual threshold.

            The deductible applies only to the portion of income exceeding the tax deduction threshold.
            Additionally, it may be limited by an annual limit.

            Args:
                income_tax_deduction (Decimal): Fixed deduction reducing taxable income before applying cost ratio.
                cost_ratio (Decimal): Cost deduction ratio (commonly 0.50).
                base (Decimal): Gross income subject to cost deduction in this period.
                cost_fifty_sum (Decimal): Accumulated author’s rights costs from previous periods.
                cost_threshold (Decimal): Annual maximum limit for 50% costs.

            Returns:
                Decimal: Deductible cost amount for this period, capped at the annual limit.
        """

        #if cost_fifty_ratio>0:
        if base > income_tax_deduction:
            cost_fifty = (base - income_tax_deduction) * cost_ratio
        else:
            cost_fifty = Decimal('0.0')
        total_cost_fifty_sum  = cost_fifty_sum +  cost_fifty
        if total_cost_fifty_sum <= cost_threshold:
            return cost_fifty
        elif total_cost_fifty_sum - cost_fifty < cost_threshold:
            return cost_threshold - (total_cost_fifty_sum -  cost_fifty)
        else:
            return Decimal('0.0')
    #else: return Decimal('0.0')

    @staticmethod
    def calculate_tax(
            income_tax: tuple[Decimal,Decimal],
            tax_base: Decimal,
            tax_base_sum: Decimal,
            tax_threshold: Decimal,
            month_tax_free: Decimal = Decimal('0.0'),
        )-> Decimal:
        """
        Calculates income tax for the current period using progressive tax thresholds.

        The function applies:
        - First tax bracket rate up to `tax_threshold`,
        - Higher tax rate above threshold,
        - Monthly tax-free deduction if applicable.

        Args:
            income_tax (tuple[Decimal, Decimal]):
                Tuple of tax rates (low_rate, high_rate), e.g. (0.12, 0.32).
            tax_base (Decimal): Taxable income for the current period.
            tax_base_sum (Decimal): Cumulative taxable income from previous periods.
            tax_threshold (Decimal): Threshold where the tax rate changes.
            month_tax_free (Decimal, optional): Monthly tax-free amount. Defaults to Decimal('0.0').

        Returns:
            Decimal: Calculated tax amount (never negative).
        """
        tax_base_sum_total = tax_base_sum + tax_base
        if tax_base_sum_total <= tax_threshold:
            out = tax_base * income_tax[0] - month_tax_free
        elif tax_base_sum_total - tax_base <= tax_threshold:
            tax_1 = (tax_threshold - (tax_base_sum_total - tax_base)) * income_tax[0] - month_tax_free
            tax_2 = (tax_base_sum_total - tax_threshold) * income_tax[1]
            out = tax_1 + tax_2
        else:
            out = tax_base * income_tax[1]

        return out if out > 0 else Decimal('0.0')






