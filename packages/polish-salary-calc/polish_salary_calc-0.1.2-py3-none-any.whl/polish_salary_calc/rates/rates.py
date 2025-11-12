from typing import TypedDict, Unpack, override
from decimal import Decimal
from dataclasses import dataclass
from typing import Self

from polish_salary_calc.salary.salaryexporter import SalaryExporter

class RatesDict(TypedDict):
    """
    Typed dictionary structure defining expected fields for Rates configuration.

    Attributes:
        description (str): Opis zestawu stawek (np. okres obowiązywania).
        pension_insurance_rate (Decimal): Stawka składki emerytalnej (ubezpieczenie społeczne).
        disability_insurance_rate (Decimal): Stawka składki rentowej.
        sickness_insurance_rate (Decimal): Stawka składki chorobowej.
        income_tax_deduction (tuple[Decimal, Decimal]): Kwoty zmniejszające podatek dla dwóch progów.
        tax_free_amount (Decimal): Kwota wolna od podatku.
        income_tax_deduction_20_50 (tuple[Decimal, Decimal]): Koszty autorskie 20%/50%.
        income_tax (tuple[Decimal, Decimal]): Stawki podatku PIT (pierwszy próg, drugi próg).
        line_tax_rate (Decimal): Stawka podatku liniowego.
        health_insurance_rate (Decimal): Stawka składki zdrowotnej dla zasad ogólnych.
        health_insurance_rate_line_tax (Decimal): Stawka składki zdrowotnej dla podatku liniowego.
        se_lump_health_insurance_base (tuple[Decimal, Decimal]): Progi dla składki zdrowotnej ryczałtowej.
        health_insurance_lump_rate (tuple[Decimal, Decimal, Decimal]): Podstawy ZUS zdrowotnego dla ryczałtu.
        employer_pension_contribution_rate (Decimal): Składka pracodawcy na ZUS emerytalne.
        employer_disability_contribution_rate (Decimal): Składka pracodawcy na ZUS rentowe.
        accident_insurance_rate (Decimal): Składka wypadkowa.
        fp_rate (Decimal): Składka na Fundusz Pracy.
        fgsp_rate (Decimal): Składka na FGŚP.
        minimum_wage (Decimal): Aktualna płaca minimalna brutto.
        tax_threshold (Decimal): Próg podatkowy PIT.
        cost_threshold (Decimal): Próg kosztowy.
        standard_social_insurance_base (Decimal): Podstawa pełnych składek ZUS.
        reduced_social_insurance_base (Decimal): Podstawa obniżonych składek ZUS (mały ZUS).
        health_insurance_base (Decimal): Podstawa składki zdrowotnej (też limit dla działalności nierejestrowanej).
        social_insurance_cap (Decimal): Roczny limit podstawy składek społecznych.
    """
    description: str
    pension_insurance_rate: Decimal
    disability_insurance_rate: Decimal
    sickness_insurance_rate: Decimal
    income_tax_deduction: tuple[Decimal, Decimal]
    tax_free_amount: Decimal
    income_tax_deduction_20_50: tuple[Decimal, Decimal]
    income_tax: tuple[Decimal, Decimal]
    line_tax_rate: Decimal
    health_insurance_rate: Decimal
    health_insurance_rate_line_tax: Decimal
    se_lump_health_insurance_base: tuple[Decimal, Decimal]
    health_insurance_lump_rate: tuple[Decimal, Decimal,Decimal]
    #ub_zdr_odl: Decimal
    employer_pension_contribution_rate: Decimal
    employer_disability_contribution_rate: Decimal
    accident_insurance_rate: Decimal
    fp_rate: Decimal
    fgsp_rate: Decimal
    minimum_wage: Decimal
    tax_threshold: Decimal #próg podatkowy
    cost_threshold: Decimal
    standard_social_insurance_base: Decimal
    reduced_social_insurance_base: Decimal
    health_insurance_base: Decimal
    social_insurance_cap: Decimal

@dataclass
class Rates(SalaryExporter):
    """
        Container for tax and insurance rate values used in salary calculations.
        Represents a parameter set for a specific legal period or tax configuration.

        This class is intended to be used by salary calculators and exporters.
        Each field corresponds to a fixed statutory rate or threshold.

        Attributes:
            description: Opis zestawu stawek (np. rok / półrocze).
            pension_insurance_rate: Stawka składki emerytalnej.
            disability_insurance_rate: Stawka składki rentowej.
            sickness_insurance_rate: Stawka składki chorobowej.
            income_tax_deduction: Kwoty zmniejszające podatek (pierwszy próg, drugi próg).
            income_tax_deduction_20_50: Koszty uzyskania przychodu 20% / 50%.
            income_tax: Stawki podatku PIT (próg pierwszy, prog drugi).
            line_tax_rate: Stawka podatku liniowego 19%.
            tax_free_base: Kwota wolna od podatku.
            health_insurance_rate: Składka zdrowotna dla zasad ogólnych (pracownik).
            health_insurance_rate_line_tax: Składka zdrowotna dla podatku liniowego.
            se_lump_health_insurance_cap: Przedziały przychodów dla ryczałtowej składki zdrowotnej.
            health_insurance_lump_base: Podstawy wymiaru składki zdrowotnej przy ryczałcie.
            employer_pension_contribution_rate: Składka emerytalna pracodawcy.
            employer_disability_contribution_rate: Składka rentowa pracodawcy.
            accident_insurance_rate: Składka wypadkowa.
            fp_rate: Składka na Fundusz Pracy.
            fgsp_rate: Składka na Fundusz Gwarantowanych Świadczeń Pracowniczych.
            minimum_wage: Płaca minimalna brutto.
            tax_threshold: Próg podatkowy PIT.
            cost_threshold: Próg kosztowy.
            standard_social_insurance_base: Standardowa podstawa ZUS.
            reduced_social_insurance_base: Obniżona podstawa ZUS (mały ZUS).
            health_insurance_base: Podstawa składki zdrowotnej.
            unregistered_cap: Limit przychodu dla działalności nieewidencjonowanej.
            social_insurance_cap: Roczny limit podstawy składek społecznych.
    """
    description: str = 'Default Rates (2025 year second half)'
    pension_insurance_rate: Decimal = Decimal('0.0976')
    disability_insurance_rate: Decimal = Decimal('0.015')
    sickness_insurance_rate: Decimal = Decimal('0.0245')
    income_tax_deduction: tuple[Decimal,Decimal] = (Decimal('250'), Decimal('300'))
    income_tax_deduction_20_50: tuple[Decimal,Decimal] = (Decimal('0.2'), Decimal('0.5'))
    income_tax: tuple[Decimal,Decimal] = (Decimal('0.12'), Decimal('0.32'))
    line_tax_rate: Decimal = Decimal('0.19')
    tax_free_base : Decimal = Decimal('30000')
    health_insurance_rate: Decimal = Decimal('0.09')
    health_insurance_rate_line_tax: Decimal = Decimal('0.049')
    se_lump_health_insurance_cap: tuple[Decimal, Decimal] = (Decimal('60000.0'), Decimal('300000.0'))
    health_insurance_lump_base: tuple[Decimal, Decimal,Decimal] = (Decimal('5129.18'), Decimal('8549.18'), Decimal('15388.52'))
    employer_pension_contribution_rate: Decimal = Decimal('0.0976')
    employer_disability_contribution_rate: Decimal = Decimal('0.0650')
    accident_insurance_rate: Decimal = Decimal('0.0167')
    fp_rate: Decimal = Decimal('0.0245')
    fgsp_rate: Decimal = Decimal('0.001')
    minimum_wage: Decimal = Decimal('4666')
    tax_threshold: Decimal = Decimal('120000')
    cost_threshold: Decimal = Decimal('120000')
    standard_social_insurance_base: Decimal = Decimal('5203.80')
    reduced_social_insurance_base: Decimal = Decimal('1399.80 ')
    health_insurance_base: Decimal = Decimal('3499.50') #also unregistered cap
    unregistered_cap: Decimal = health_insurance_base
    social_insurance_cap: Decimal = Decimal('260190')

    @property
    def tax_free(self) -> Decimal:
        """
        Returns:
            Decimal: Annual tax-free deduction expressed as (low tax rate * tax_free_base).
        """
        return self.income_tax[0] * self.tax_free_base

    @property
    def month_tax_free(self) -> Decimal:
        """
        Returns:
            Decimal: Monthly portion of the tax-free amount.
        """
        return self.tax_free/12

    @classmethod
    def from_dict(cls,data: RatesDict) -> Self:
        """
        Instantiates a Rates object from a dictionary matching RatesDict schema.

        Args:
            data (RatesDict): Source data dictionary.

        Returns:
            Rates: A new Rates instance.
        """
        return cls(**data)

    def to_dict(self) -> Unpack[RatesDict]:
        """
        Converts the Rates instance into a dictionary matching RatesDict.

        Returns:
            RatesDict: Dictionary representation of the instance.
        """
        return self.__dict__

    @override
    def to_exporter_dict(self) -> dict[str, dict[str, str | Decimal | bool]]:
        """
        Prepares the object for standardized export.

        Returns:
            dict: Export-structured dictionary payload.
        """
        return {self.__class__.__name__:self.to_dict()}

    def __getitem__(self, item: str) -> Decimal | str:
        """
        Allows retrieving attribute values via dictionary-like access.

        Args:
            item (str): Attribute name.

        Returns:
            Decimal | str: Value of requested attribute.
        """
        return getattr(self, item)

    def __setitem__(self, key: str, value: Decimal | str) -> None:
        """
        Allows mutation of attributes via dictionary-like access.

        Args:
            key (str): Attribute name.
            value (Decimal | str): Value to assign.

        Raises:
            KeyError: If attribute does not exist.
        """
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f'Attribute {key} not found.')

    def __str__(self) -> str:
        """
        Returns:
            str: Human-readable string representation suitable for logs or console output.
        """
        return self.to_string()